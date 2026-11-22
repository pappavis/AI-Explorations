# Version: 1.5.1 | Release ChatID: D82F4A61
import contextlib
import importlib.util
import io
import pathlib
import tempfile
import unittest
from unittest.mock import patch

base = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fm_status_integration', base / 'scripts/fm1_update.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class StatusIntegration(unittest.TestCase):
    def test_real_status_workflow_with_offline_catalog(self):
        catalog = [
            {'kind':'FM-1','id':'DemoNew','version':'2.0','url':'https://example.test/new'},
            {'kind':'FM-1','id':'DemoOld','version':'3.0','url':'https://example.test/old'},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / 'DemoOld.aot').write_bytes(b'firmware')
            (root / '.firmware-manager.json').write_text('{"items":{"FM-1/DemoOld":{"version":"2.0","files":["DemoOld.aot"]}}}')
            output = io.StringIO()
            with patch.object(m, 'discover_fm_verified', return_value=catalog), patch.object(m, 'discover_smk_catalog', return_value=[]):
                with contextlib.redirect_stdout(output):
                    code = m.main(['--mode','status','--status-full','--target',tmp,'--debug-json',str(root/'debug.json')])
            self.assertEqual(code, 0)
            self.assertIn('FM-1/DemoNew', output.getvalue())
            self.assertIn('FM-1/DemoOld', output.getvalue())
            self.assertIn('GEWIJZIGD', output.getvalue())
            self.assertIn('NIEUW', output.getvalue())
            self.assertTrue((root/'DemoOld.aot').exists())
