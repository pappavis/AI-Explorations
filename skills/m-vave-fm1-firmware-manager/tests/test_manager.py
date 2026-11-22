# Version: 1.2.0 | Release ChatID: E6B91A42
import importlib.util, pathlib, tempfile, unittest, zipfile
p=pathlib.Path(__file__).resolve().parents[1]/'scripts/fm1_update.py'
s=importlib.util.spec_from_file_location('manager',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_catalog_versions(self):
  entries=m.fm_catalog({'ok':True,'library':[{'id':'OPN-1','name':'OPN-1','version':'v2.0.0'}]})
  self.assertEqual(entries[0]['version'],'v2.0.0')
  self.assertIn('id=OPN-1',entries[0]['url'])
 def test_catalog_duplicate_rejected(self):
  with self.assertRaises(m.UpdateError):m.fm_catalog({'ok':True,'library':[{'id':'X'},{'id':'X'}]})
 def test_fm_links(self):
  a=m.discover('FM-1','<a href="/api/convert/lib?id=OPN-1">x</a>');self.assertEqual(a[0]['id'],'OPN-1')
 def test_smk_links(self):
  a=m.discover('SMK-37-Pro','<a href="https://thefirmwarehub.com/firmware.zip">x</a>');self.assertEqual(a[0]['id'],'firmware')
 def test_report_required_sections(self):
  entries=[{'kind':'FM-1','id':'OPN-1','url':'https://thefirmwarehub.com/x'}]
  changes=[('GEWIJZIGD','FM-1/OPN-1','v1','v2','v2','https://thefirmwarehub.com/x'),('NIEUW','FM-1/DUB-1','—','v1','v1','https://thefirmwarehub.com/y')]
  report=m.render_report(entries,changes,{'FM-1':1},{'FM-1':2},{'downloads':'OK','validation':'OK','cleanup':'OK','installation':'OK'})
  for term in ('╔','FM-1','SMK-37 PRO','Website firmwares','Lokaal vóór update','GEWIJZIGD','NIEUW','Hardware flash','Cleanup','Download:'):
   self.assertIn(term,report)
  self.assertLess(report.index('GEWIJZIGD\n'),report.index('NIEUW\n'))
 def test_external_smk_link_rejected(self):
  with self.assertRaises(m.UpdateError):m.discover('SMK-37-Pro','<a href="https://example.org/malware.zip">x</a>')
 def test_no_links(self):
  with self.assertRaises(m.UpdateError):m.discover('SMK-37-Pro','<p>No links</p>')
 def test_zip_traversal(self):
  with tempfile.TemporaryDirectory() as t:
   z=pathlib.Path(t)/'x.zip'
   with zipfile.ZipFile(z,'w') as f:f.writestr('../evil.aot','bad')
   with self.assertRaises(m.UpdateError):m.validate_zip(z,pathlib.Path(t)/'out','FM-1')
 def test_zip_valid(self):
  with tempfile.TemporaryDirectory() as t:
   z=pathlib.Path(t)/'x.zip'
   with zipfile.ZipFile(z,'w') as f:f.writestr('nested/OPN-1.aot','ok')
   self.assertEqual(len(m.validate_zip(z,pathlib.Path(t)/'out','FM-1')),1)
if __name__=='__main__':unittest.main()
