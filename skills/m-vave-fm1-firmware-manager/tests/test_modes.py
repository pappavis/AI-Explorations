# Version: 1.4.0 | Release ChatID: 4F8C2A91
import importlib.util, pathlib, tempfile, unittest
p=pathlib.Path(__file__).resolve().parents[1]/'scripts/fm1_update.py'
s=importlib.util.spec_from_file_location('fwmanager14',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Modes(unittest.TestCase):
 def test_original_catalog_url(self):
  from unittest.mock import patch
  class Response:
   def __enter__(self):return self
   def __exit__(self,*args):return False
   def read(self,*args):return b'{"ok":true,"library":[{"id":"OPN-1","version":"v2"}]}'
  with patch.object(m,'fetch',return_value=Response().read()):
   result=m.discover_fm_verified()
  self.assertEqual(result[0]['url'],'https://thefirmwarehub.com/api/convert/lib?id=OPN-1')
 def test_original_source_has_priority(self):
  from unittest.mock import patch
  expected=[{'id':'X','kind':'FM-1'}]
  with patch.object(m,'discover_fm_catalog',return_value=expected), patch.object(m,'discover',side_effect=AssertionError('fallback must not run')):
   self.assertEqual(m.discover_fm_verified(),expected)
 def test_status_missing(self):
  with tempfile.TemporaryDirectory() as d:
   e={'kind':'FM-1','id':'OPN-1','version':'2.0'}
   self.assertEqual(m.status_for(e,{},pathlib.Path(d)),'NIEUW')
 def test_status_version_change(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'a.aot').write_bytes(b'a')
   e={'kind':'FM-1','id':'OPN-1','version':'2.0'}
   old={'FM-1/OPN-1':{'version':'1.0','files':['a.aot']}}
   self.assertEqual(m.status_for(e,old,root),'GEWIJZIGD')
 def test_status_current(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'a.aot').write_bytes(b'a')
   e={'kind':'FM-1','id':'OPN-1','version':'2.0'}
   old={'FM-1/OPN-1':{'version':'2.0','files':['a.aot']}}
   self.assertEqual(m.status_for(e,old,root),'ONVERANDERD')
if __name__=='__main__':unittest.main()
