#!/usr/bin/env python3
# Version: 1.6.0 | Release ChatID: A61E4C92
"""Download-only firmware archive manager. Never connects to hardware."""
import argparse, hashlib, html.parser, json, os, platform, re, shutil, sys, tempfile, urllib.parse, urllib.request, zipfile, datetime, traceback, time
from pathlib import Path, PurePosixPath

VERSION='1.6.0'; CHAT_ID='A61E4C92'
PAGES={'FM-1':'https://thefirmwarehub.com/convert/','SMK-37-Pro':'https://thefirmwarehub.com/smk37/'}
MAX_DOWNLOAD=200*1024*1024; MAX_UNPACK=500*1024*1024
class DebugLog:
 def __init__(self,path,mode):
  self.path=Path(path).expanduser();self.data={'schema':1,'release':VERSION,'chat_id':CHAT_ID,'mode':mode,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'RUNNING','events':[],'errors':[]}
  self.write()
 def write(self):
  self.path.parent.mkdir(parents=True,exist_ok=True)
  fd,tmp=tempfile.mkstemp(prefix='.firmware-debug-',dir=self.path.parent)
  try:
   with os.fdopen(fd,'w',encoding='utf-8') as f:
    json.dump(self.data,f,indent=2,ensure_ascii=False);f.flush();os.fsync(f.fileno())
   os.replace(tmp,self.path)
  finally:Path(tmp).unlink(missing_ok=True)
 def event(self,step,message,**details):
  event={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'step':step,'message':message,**details}
  self.data['events'].append(event)
  self.write()
  ProgressView().show(step, message, details)
 def finish(self,status,error=None):
  self.data['status']=status;self.data['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
  if error:self.data['errors'].append(str(error))
  self.write()

class ProgressView:
    """Human-readable progress; machine-readable facts stay in the JSON log."""

    def __init__(self):
        self.tty = sys.stderr.isatty()
        self.color = self.tty and not os.environ.get('NO_COLOR')

    def tint(self, value, code):
        if not self.color:
            return value
        return f"\033[{code}m{value}\033[0m"

    def show(self, step, message, details):
        firmware = details.get('firmware', '')
        current = details.get('index')
        total = details.get('total')
        position = f"[{current:03d}/{total:03d}] " if current and total else ''
        prefix = self.tint(step.upper(), '36')
        label = f"{position}{firmware} — {message}" if firmware else message
        print(f"{prefix}  {label}", file=sys.stderr, flush=True)

        for key, title in (
            ('name', 'Naam'),
            ('version', 'Websiteversie'),
            ('local_version', 'Lokale versie'),
            ('action', 'Actie'),
            ('url', 'Bron'),
            ('archive', 'ZIP-bestand'),
            ('bytes', 'Grootte (bytes)'),
            ('elapsed_seconds', 'Duur (seconden)'),
            ('sha256', 'SHA-256'),
            ('files', 'Bestanden'),
            ('target', 'Doelmap'),
            ('error', 'Fout'),
        ):
            if key in details:
                value = details[key]
                if isinstance(value, list):
                    value = ', '.join(str(item) for item in value)
                print(f"    {title:<18}: {value}", file=sys.stderr, flush=True)

        if current and total and step == 'validation':
            percent = int(current * 100 / total)
            filled = int(percent * 30 / 100)
            bar = '█' * filled + '░' * (30 - filled)
            print(f"    {bar} {percent:3d}% ({current}/{total})", file=sys.stderr, flush=True)


class UpdateError(Exception): pass
class Links(html.parser.HTMLParser):
 def __init__(self): super().__init__(); self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':
   a=dict(attrs); self.links.append((a.get('href',''),a.get('download','')))
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'FirmwareLibraryManager/1.1','Accept':'text/html,*/*'})
 with urllib.request.urlopen(req,timeout=25) as r: return r.read(8*1024*1024+1)
def fm_catalog(payload):
 """Read a real catalog response, never synthesize IDs."""
 if not isinstance(payload,dict) or payload.get('ok') is not True or not isinstance(payload.get('library'),list) or not payload['library']:
  raise UpdateError('Ongeldige of lege FM-1 catalogus')
 items=[];seen=set()
 for entry in payload['library']:
  if not isinstance(entry,dict):raise UpdateError('Ongeldige catalogusentry')
  ident=entry.get('id')
  if not isinstance(ident,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',ident) or ident in seen:raise UpdateError('Ongeldige/dubbele firmware-ID')
  seen.add(ident)
  items.append({'id':ident,'url':'https://thefirmwarehub.com/api/convert/lib?id='+urllib.parse.quote(ident,safe=''),
                'version':str(entry.get('version') or 'onbekend'),'name':str(entry.get('name') or ident),'kind':'FM-1'})
 return sorted(items,key=lambda x:x['id'])

def discover_fm_catalog():
 """Original updater's catalog source; fail closed if unverified."""
 data=fetch('https://thefirmwarehub.com/api/convert/library')
 if len(data)>8*1024*1024:raise UpdateError('Catalogus te groot')
 return fm_catalog(json.loads(data.decode('utf-8')))

def browser_html(kind):
 try:from playwright.sync_api import sync_playwright
 except ImportError:raise UpdateError('Browserfallback ontbreekt: pip install playwright && python -m playwright install chromium')
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True)
  try:
   page=browser.new_page()
   page.goto(PAGES[kind],wait_until='domcontentloaded',timeout=60000)
   page.wait_for_timeout(3500)
   for _ in range(12):page.mouse.wheel(0,1800);page.wait_for_timeout(200)
   return page.content()
  finally:browser.close()

def discover(kind,html=None):
 """Conservative discovery; FM-1 may expose URLs in HTML, JS or a library index."""
 page=PAGES[kind]
 body=fetch(page).decode('utf-8','replace') if html is None else html
 if len(body)>8*1024*1024:raise UpdateError('HTML te groot')
 p=Links();p.feed(body)
 # Some sites generate download buttons with JavaScript, not <a href> tags.
 candidates=[href for href,_ in p.links]
 candidates+=re.findall(r'(?:https?:\\?/\\?/[^\s\"\'<>]+)?\\?/api\\?/convert\\?/lib\?id=[A-Za-z0-9_-]+',body)
 candidates+=re.findall(r'[\"\']([^\"\']+\.zip(?:\?[^\"\']*)?)[\"\']',body,re.I)
 found={}
 for href in candidates:
  href=href.replace('\\/','/')
  url=urllib.parse.urljoin(page,href);parsed=urllib.parse.urlparse(url)
  if parsed.scheme!='https':continue
  if kind=='FM-1':
   if parsed.hostname not in {'thefirmwarehub.com','www.thefirmwarehub.com'} or parsed.path.rstrip('/')!='/api/convert/lib':continue
   ident=urllib.parse.parse_qs(parsed.query).get('id',[''])[0]
   if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',ident):continue
  else:
   if not parsed.path.lower().endswith('.zip'):continue
   if parsed.hostname not in {'thefirmwarehub.com','www.thefirmwarehub.com'}:continue
   ident=Path(urllib.parse.unquote(parsed.path)).stem
   if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',ident):continue
  if ident in found and found[ident]['url']!=url:raise UpdateError('Dubbele ID met afwijkende URL: '+ident)
  found[ident]={'id':ident,'url':url,'version':'onbekend','name':ident,'kind':kind}
 if not found:
  raise UpdateError(f'{kind}: geen directe downloadlinks gevonden in HTML; probeer browserfallback. Geen wijzigingen.')
 return sorted(found.values(),key=lambda x:x['id'])

class SMKCards(html.parser.HTMLParser):
 """Read SMK-37 firmware cards; installer links are NOT firmware ZIPs."""
 def __init__(self):
  super().__init__();self.cards=[];self.heading=False;self.title=[];self.active=None;self.in_anchor=False;self.anchor_href='';self.anchor_text=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='h3':
   self.heading=True;self.title=[]
  elif tag=='a':
   self.in_anchor=True;self.anchor_href=a.get('href','');self.anchor_text=[]
 def handle_data(self,data):
  if self.heading:self.title.append(data)
  if self.in_anchor:self.anchor_text.append(data)
 def handle_endtag(self,tag):
  if tag=='h3' and self.heading:
   self.heading=False
   title=' '.join(''.join(self.title).split())
   if title and not title.lower().startswith('your firmware'):
    self.active={'id':re.sub(r'[^A-Za-z0-9_.-]+','-',title)[:100], 'name':title,'version':'onbekend','kind':'SMK-37-Pro','url':'','downloadable':False}
    self.cards.append(self.active)
  if tag=='a' and self.in_anchor:
   label=' '.join(''.join(self.anchor_text).split()).lower()
   if self.active and ('install' in label or 'how to install' in label):
    self.active['url']=urllib.parse.urljoin(PAGES['SMK-37-Pro'],self.anchor_href)
   self.in_anchor=False

def discover_smk_catalog(html=None):
 """Inventory installer cards; do not mistake an installer for a downloadable ZIP."""
 body=fetch(PAGES['SMK-37-Pro']).decode('utf-8','replace') if html is None else html
 parser=SMKCards();parser.feed(body)
 cards=[c for c in parser.cards if c['url']]
 if not cards:raise UpdateError('SMK-37: geen firmwarekaarten gevonden; HTML-structuur controleren')
 return cards


def discover_fm_verified():
 """Original v1.0.0 source first: /api/convert/library and /api/convert/lib?id=.
 No catalog.json guesswork. HTML/Playwright only as fallbacks.
 """
 errors=[]
 try:
  return discover_fm_catalog()
 except (OSError,ValueError,UpdateError) as exc:
  errors.append('original library: '+str(exc))
 try:
  return discover('FM-1')
 except (OSError,ValueError,UpdateError) as exc:
  errors.append('HTML: '+str(exc))
 try:
  return discover_fm_browser()
 except (OSError,ValueError,UpdateError) as exc:
  errors.append('browser: '+str(exc))
 raise UpdateError('FM-1 discovery mislukt; '+ '; '.join(errors))

def discover_fm_browser():
 """Observe genuine site responses, never invent firmware IDs or endpoints."""
 try:from playwright.sync_api import sync_playwright
 except ImportError as exc:raise UpdateError('Playwright ontbreekt (pip install playwright; python -m playwright install chromium)') from exc
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True)
  try:
   page=browser.new_page()
   found={}; catalog=[]
   def observe(response):
    url=response.url
    if '/api/convert/library' in url:
     try:catalog.extend(fm_catalog(response.json()))
     except Exception:pass
    if '/api/convert/lib?id=' in url:
     try:
      parsed=urllib.parse.urlparse(url)
      ident=urllib.parse.parse_qs(parsed.query).get('id',[''])[0]
      if parsed.hostname=='thefirmwarehub.com' and re.fullmatch(r'[A-Za-z0-9_-]{1,80}',ident):
       found[ident]={'id':ident,'name':ident,'version':'onbekend','url':url,'kind':'FM-1'}
     except Exception:pass
   page.on('response',observe)
   page.goto(PAGES['FM-1'],wait_until='domcontentloaded',timeout=60000)
   page.wait_for_timeout(2500)
   for _ in range(20):page.mouse.wheel(0,1800);page.wait_for_timeout(120)
   if catalog:return catalog
   try:return discover('FM-1',page.content())
   except UpdateError:
    if found:return sorted(found.values(),key=lambda x:x['id'])
    raise
  finally:browser.close()

def status_for(entry,old,root):
 key=entry['kind']+'/'+entry['id'];prev=old.get(key)
 if not prev:return 'NIEUW'
 files=prev.get('files',[])
 if not files or any(not (root/f).is_file() for f in files):return 'NIEUW'
 site=entry.get('version','onbekend');local=prev.get('version','onbekend')
 if site!='onbekend' and local!='onbekend' and site!=local:return 'GEWIJZIGD'
 if entry.get('sha256_expected') and prev.get('sha256')!=entry['sha256_expected']:return 'GEWIJZIGD'
 return 'ONVERANDERD' if site!='onbekend' else 'ONBEKEND'

def root_path():
 h=Path.home();system=platform.system()
 if system=='Darwin':return h/'Library/Application Support/VIBE FM/Firmware'
 if system=='Windows':
  if not os.getenv('APPDATA'):raise UpdateError('APPDATA ontbreekt')
  return Path(os.environ['APPDATA'])/'VIBE FM/Firmware'
 return Path(os.getenv('XDG_DATA_HOME',str(h/'.local/share')))/'VIBE FM/Firmware'
def download(url,dest):
 req=urllib.request.Request(url,headers={'User-Agent':'FirmwareLibraryManager/1.1'})
 with urllib.request.urlopen(req,timeout=40) as r,dest.open('wb') as out:
  total=0
  while True:
   b=r.read(131072)
   if not b:break
   total+=len(b)
   if total>MAX_DOWNLOAD:raise UpdateError('Pakket te groot')
   out.write(b)
def validate_zip(src,dst,kind):
 if not zipfile.is_zipfile(src):raise UpdateError('Geen ZIP')
 names=set();out=[];total=0
 with zipfile.ZipFile(src) as z:
  for i in z.infolist():
   n=i.filename.replace('\\','/');p=PurePosixPath(n)
   if not n or n.startswith('/') or n.startswith('//') or '..' in p.parts or ':' in n or i.flag_bits&1 or ((i.external_attr>>16)&0o170000)==0o120000:raise UpdateError('Onveilige ZIP entry: '+n)
   total+=i.file_size
   if total>MAX_UNPACK:raise UpdateError('Uitgepakte omvang te groot')
   if i.is_dir():continue
   name=p.name
   if kind=='FM-1' and p.suffix.lower() not in {'.aot','.json','.wasm'}:continue
   if not name or name.casefold() in names:raise UpdateError('Dubbele bestandsnaam: '+name)
   names.add(name.casefold());out.append(i)
  if not out:raise UpdateError('Geen bruikbare bestanden')
  if z.testzip() is not None:raise UpdateError('CRC mislukt')
  dst.mkdir(parents=True,exist_ok=True)
  for i in out:
   with z.open(i) as inp,(dst/PurePosixPath(i.filename.replace('\\','/')).name).open('wb') as target:shutil.copyfileobj(inp,target)
 return [dst/PurePosixPath(i.filename.replace('\\','/')).name for i in out]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(131072),b''):h.update(b)
 return h.hexdigest()
def manifest(path):
 try:return json.loads(path.read_text(encoding='utf-8'))
 except FileNotFoundError:return {'items':{}}
def commit(staged,root,manifest_data):
 """Backup touched files and roll back on installation failure."""
 root.mkdir(parents=True,exist_ok=True); backup=Path(tempfile.mkdtemp(prefix='.fm-backup-',dir=root.parent)); touched=[]
 try:
  for src,dest in staged:
   dest.parent.mkdir(parents=True,exist_ok=True);old=dest.exists();back=backup/str(len(touched))
   if old:shutil.copy2(dest,back)
   touched.append((dest,back,old))
   fd,tmp=tempfile.mkstemp(prefix='.fw-',dir=dest.parent)
   try:
    with os.fdopen(fd,'wb') as o,src.open('rb') as i:shutil.copyfileobj(i,o);o.flush();os.fsync(o.fileno())
    os.replace(tmp,dest)
   finally:Path(tmp).unlink(missing_ok=True)
  state=root/'.firmware-manager.json'
  if state.exists():
   back=backup/'manifest';shutil.copy2(state,back);touched.append((state,back,True))
  else:touched.append((state,backup/'manifest',False))
  fd,tmp=tempfile.mkstemp(prefix='.fw-',dir=root)
  try:
   with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(manifest_data,f,indent=2,ensure_ascii=False);f.flush();os.fsync(f.fileno())
   os.replace(tmp,state)
  finally:Path(tmp).unlink(missing_ok=True)
 except Exception:
  for dest,back,old in reversed(touched):
   if old:os.replace(back,dest)
   else:dest.unlink(missing_ok=True)
  raise
 finally:shutil.rmtree(backup)
def box(lines, width=56):
    """Unicode ASCII-style box with correct display widths for normal terminal text."""
    out=['╔'+'═'*(width-2)+'╗']
    for line in lines:
        if line is None:
            out.append('╠'+'═'*(width-2)+'╣')
        else:
            out.append('║ '+str(line)[:width-4].ljust(width-4)+' ║')
    out.append('╚'+'═'*(width-2)+'╝')
    return '\n'.join(out)


def render_report(entries, changes, before, after, result, platform_name=None):
    platform_name=platform_name or platform.system()
    lines=[f'M-VAVE FIRMWARE MANAGER v{VERSION}',f'Platform: {platform_name}',None]
    for kind,label in [('FM-1','FM-1'),('SMK-37-Pro','SMK-37 PRO')]:
        e=[x for x in entries if x['kind']==kind]
        c=[x for x in changes if x[1].startswith(kind+'/')]
        lines += [label, f'Website firmwares       {len(e):>7}',
                  f'Lokaal vóór update      {before.get(kind,0):>7}',
                  f'Lokaal na update        {after.get(kind,0):>7}',
                  f'Nieuwe firmwares        {sum(x[0]=="NIEUW" for x in c):>7}',
                  f'Gewijzigde firmwares    {sum(x[0]=="GEWIJZIGD" for x in c):>7}',None]
    lines += ['STATUS',f'Downloads                 {result.get("downloads","NVT")}',
              f'Validatie                 {result.get("validation","NVT")}',
              'Hardware flash            NOOIT',
              f'Cleanup                   {result.get("cleanup","NVT")}',
              f'Installatie               {result.get("installation","NVT")}']
    out=[box(lines)]
    for status,heading in [('GEWIJZIGD','GEWIJZIGD'),('NIEUW','NIEUW')]:
        rows=[c for c in changes if c[0]==status]
        out += ['',heading,'Firmware                     Vorig       Website     Lokaal',
                '------------------------------------------------------------------']
        for _,key,previous,site,local,url in sorted(rows,key=lambda x:x[1]):
            out.append(f'{key[:28]:28} {previous[:11]:11} {site[:11]:11} {local[:11]:11}')
            out.append(f'  Download: {url}')
        if not rows:out.append('(geen)')
    return '\n'.join(out)



def render_status_summary(entries, changes, before, target):
    """Readable overview without changing discovery, downloads, or installation."""
    lines = [
        f'M-VAVE FIRMWARE MANAGER v{VERSION} — STATUS',
        f'Firmwaremap: {target}',
        'Hardware flash: NOOIT',
        None,
    ]
    for kind in ('FM-1', 'SMK-37-Pro'):
        rows = [row for row in changes if row[1].startswith(kind + '/')]
        lines.extend([
            f'{kind} | website: {sum(e["kind"] == kind for e in entries)} | lokaal (manifest): {before.get(kind, 0)}',
            '  NIEUW: {0} | GEWIJZIGD: {1} | ACTUEEL: {2} | ONBEKEND: {3}'.format(
                sum(row[0] == 'NIEUW' for row in rows),
                sum(row[0] == 'GEWIJZIGD' for row in rows),
                sum(row[0] == 'ONVERANDERD' for row in rows),
                sum(row[0] == 'ONBEKEND' for row in rows),
            ),
        ])
    lines.extend([None, 'Gebruik: status full voor alle firmwareversies en bronlinks.'])
    return box(lines, width=100)


def render_status_full(entries, changes, before, target):
    """Full per-firmware comparison, including unchanged and unknown entries."""
    output = [render_status_summary(entries, changes, before, target)]
    output.append('')
    output.append('STATUS FULL — WEBSITE VERSUS LOKAAL (MANIFEST)')
    output.append(f'{"STATUS":<14} {"FIRMWARE":<40} {"LOKAAL":<18} {"WEBSITE":<18}')
    output.append('─' * 96)
    order = {'GEWIJZIGD': 0, 'NIEUW': 1, 'ONBEKEND': 2, 'ONVERANDERD': 3}
    for state, key, previous, website, local, url in sorted(changes, key=lambda row: (order.get(row[0], 9), row[1].lower())):
        output.append(f'{state:<14} {key[:40]:<40} {local[:18]:<18} {website[:18]:<18}')
        output.append(f'  Bron: {url}')
    output.append('')
    output.append('Let op: lokale versies komen uit het manifest; dit is geen plugin-runtimecontrole.')
    return '\n'.join(output)

def run(args):
 log=args.debug_log
 log.event('start','Firmware manager gestart',mode=args.mode)
 root=Path(args.target).expanduser() if args.target else root_path()
 log.event('paths','Doelmap bepaald',target=str(root))
 old=manifest(root/'.firmware-manager.json').get('items',{})
 entries=[]
 try:
  if args.no_browser:
   try:fm=discover_fm_catalog()
   except (OSError,ValueError,UpdateError):fm=discover('FM-1')
  else:
   fm=discover_fm_verified()
  entries.extend(fm)
  log.event('discovery_fm','FM-1 catalogus gevonden',count=len(fm))
  try:
   smk=discover_smk_catalog();entries.extend(smk)
   log.event('discovery_smk','SMK-37 catalogus gevonden',count=len(smk))
  except (OSError,ValueError,UpdateError) as exc:
   print('WAARSCHUWING: SMK-37 inventarisatie niet beschikbaar:',exc,file=sys.stderr)
   log.event('warning','SMK-37 discovery niet beschikbaar',error=str(exc))
 except Exception:
  print(box([f'M-VAVE FIRMWARE MANAGER v{VERSION}','Discovery: FOUT','Installatie: NIET UITGEVOERD','Hardware flash: NOOIT']))
  raise
 log.event('discovery','Inventarisatie voltooid',total=len(entries))
 before={k:sum(key.startswith(k+'/') for key in old) for k in PAGES}
 after=before.copy()
 changes=[];selected=[]
 for e in entries:
  key=e['kind']+'/'+e['id'];prev=old.get(key,{})
  state=status_for(e,old,root)
  changes.append((state,key,str(prev.get('version','—')),e['version'],str(prev.get('version','—')),e['url']))
  if e['kind']=='FM-1' and (args.mode=='update-all' or state!='ONVERANDERD'):
   selected.append(e)
 log.event('selection','Firmwareselectie berekend',selected=len(selected),fm_total=len(fm),mode=args.mode)
 log.event('paths','Firmwarebibliotheek',target=str(root))
 result={'downloads':'NVT','validation':'NVT','cleanup':'NVT','installation':'NVT'}
 if args.list or args.dry_run or args.mode=='status':
  if args.status_json:
   from firmware_dashboard import DashboardSnapshot
   snapshot=DashboardSnapshot.build(entries,changes,before,root)
   destination=Path(args.status_json).expanduser()
   destination.parent.mkdir(parents=True,exist_ok=True)
   fd,tmp=tempfile.mkstemp(prefix='.status-',dir=destination.parent)
   try:
    with os.fdopen(fd,'w',encoding='utf-8') as output:
     json.dump(snapshot,output,indent=2,ensure_ascii=False)
    os.replace(tmp,destination)
   finally:
    Path(tmp).unlink(missing_ok=True)
  log.event('report','Statusrapport opgebouwd',changes=len(changes))
  if args.mode == 'status' and not args.list and not args.dry_run:
   if args.status_full:
    print(render_status_full(entries, changes, before, root))
   else:
    print(render_status_summary(entries, changes, before, root))
  else:
   print(render_report(entries, changes, before, after, result))
  print(f'FM-1 geselecteerd voor {args.mode}: {len(selected)} / {len(fm)}')
  return 0
 temp=Path(args.temp).expanduser() if args.temp else (Path(os.getenv('TEMP',tempfile.gettempdir())) if platform.system()=='Windows' else Path.home()/'Downloads')
 temp.mkdir(parents=True,exist_ok=True)
 staged=[];seen=set();new=dict(old)
 try:
  with tempfile.TemporaryDirectory(prefix='m-vave-',dir=temp) as work:
   work=Path(work)
   for index,e in enumerate(selected):
    key=e['kind']+'/'+e['id'];archive=work/f'{index}.zip';folder=work/f'{index}-files'
    local=old.get(key,{}).get('version','—')
    action='NIEUW' if key not in old else ('OPNIEUW DOWNLOADEN' if args.mode=='update-all' else 'BIJWERKEN')
    log.event('download','Download gestart',firmware=key,name=e.get('name',e['id']),version=e.get('version','onbekend'),local_version=local,action=action,index=index+1,total=len(selected),url=e['url'],archive=archive.name)
    started=time.monotonic()
    download(e['url'],archive)
    elapsed=round(time.monotonic()-started,2)
    log.event('download','Download voltooid',firmware=key,index=index+1,total=len(selected),archive=archive.name,bytes=archive.stat().st_size,elapsed_seconds=elapsed)
    digest=sha(archive)
    expected=e.get('sha256_expected')
    if expected and (not re.fullmatch('[a-fA-F0-9]{64}',str(expected)) or digest.lower()!=str(expected).lower()):
     raise UpdateError('SHA-256 mismatch: '+key)
    files=validate_zip(archive,folder,'FM-1')
    log.event('validation','ZIP gevalideerd: ZIP/CRC/padveiligheid gecontroleerd',firmware=key,index=index+1,total=len(selected),archive=archive.name,files=[f.name for f in files],sha256=digest)
    candidates=[(f,root/f.name) for f in files]
    for source,dest in candidates:
     if str(dest).casefold() in seen:raise UpdateError('Bestandsnaamconflict: '+str(dest))
     seen.add(str(dest).casefold());staged.append((source,dest))
    new[key]={**e,'sha256':digest,'files':[str(d.relative_to(root)) for _,d in candidates]}
   result['downloads']='OK';result['validation']='OK'
   log.event('installation','Installatie gestart na volledige ZIP-validatie',files=len(staged),target=str(root))
   if staged:commit(staged,root,{'version':VERSION,'items':new})
   log.event('installation','Installatie afgerond',files=len(staged),target=str(root))
   result['installation']='OK';after={k:sum(x.startswith(k+'/') for x in new) for k in PAGES}
 finally:
  result['cleanup']='OK'
  log.event('cleanup','Tijdelijke werkmap afgesloten')
 changes=[]
 for e in entries:
  key=e['kind']+'/'+e['id'];prev=old.get(key,{})
  state=status_for(e,old,root) if e['kind']=='SMK-37-Pro' else ('NIEUW' if not prev else ('GEWIJZIGD' if key in {x['kind']+'/'+x['id'] for x in selected} else 'ONVERANDERD'))
  changes.append((state,key,str(prev.get('version','—')),e['version'],str(new.get(key,{}).get('version','—')),e['url']))
 log.event('report','Eindrapport opgebouwd',changes=len(changes))
 print(render_report(entries,changes,before,after,result))
 print(f'FM-1 pakketten gedownload: {len(selected)} / {len(fm)} | modus: {args.mode}')
 print('SMK-37: alleen catalogusstatus; fysieke hardware nooit benaderd.')
 return 0

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--list',action='store_true');p.add_argument('--dry-run',action='store_true');p.add_argument('--target');p.add_argument('--temp');p.add_argument('--verbose',action='store_true');p.add_argument('--no-browser',action='store_true');p.add_argument('--debug-json',help='JSON-logbestand; wordt bij iedere run overschreven');p.add_argument('--mode',choices=['status','refresh','update-all'],default='refresh');p.add_argument('--status-json',help='Schrijf UI-status als JSON');p.add_argument('--status-full',action='store_true',help='Toon alle firmwareversies en bronlinks');args=p.parse_args(argv)
 logpath=Path(args.debug_json).expanduser() if args.debug_json else Path(__file__).resolve().parent.parent/'firmware-debug.json'
 try:args.debug_log=DebugLog(logpath,args.mode)
 except OSError as e:print('FOUT: debuglog kan niet worden geschreven:',e,file=sys.stderr);return 2
 try:
  result=run(args)
  args.debug_log.finish('SUCCESS' if result==0 else 'FAILED')
  return result
 except Exception as e:
  args.debug_log.event('error','Uitvoering mislukt',error=str(e),type=type(e).__name__)
  args.debug_log.finish('FAILED',e)
  print('FOUT:',e,file=sys.stderr)
  return 2
if __name__=='__main__':sys.exit(main())
