# Version: 1.4.1 | Release ChatID: 6C2A9F41
import importlib.util,json,tempfile,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'scripts/fm1_update.py'
s=importlib.util.spec_from_file_location('firmware_debug',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class DebugTests(unittest.TestCase):
 def test_overwrite_and_valid_json(self):
  with tempfile.TemporaryDirectory() as t:
   path=Path(t)/'debug.json'
   a=m.DebugLog(path,'status');a.event('discovery','test',count=3);a.finish('SUCCESS')
   self.assertEqual(json.loads(path.read_text())['events'][0]['details'] if False else json.loads(path.read_text())['events'][0]['count'],3)
   b=m.DebugLog(path,'refresh');b.finish('FAILED','network')
   data=json.loads(path.read_text());self.assertEqual(data['mode'],'refresh');self.assertEqual(data['events'],[]);self.assertEqual(data['errors'],['network'])
if __name__=='__main__':unittest.main()
