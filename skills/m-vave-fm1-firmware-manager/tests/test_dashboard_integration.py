# Version: 1.6.0 | Release ChatID: A61E4C92
"""Offline end-to-end status JSON contract through the real updater entry point."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import fm1_update as updater


class DashboardIntegration(unittest.TestCase):
    def test_status_json_and_no_changes_to_firmware(self):
        entries = [
            {'kind':'FM-1', 'id':'FRASIL', 'version':'2.6', 'url':'https://example.test/frasil'},
            {'kind':'FM-1', 'id':'SPAMPY', 'version':'r949', 'url':'https://example.test/spampy'},
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            firmware = root / 'FRASIL.wasm'
            firmware.write_bytes(b'original-unchanged')
            (root / '.firmware-manager.json').write_text(json.dumps({
                'items': {'FM-1/FRASIL': {'version':'2.5', 'files':['FRASIL.wasm']}}
            }))
            status_path = root / 'status.json'
            with patch.object(updater, 'discover_fm_verified', return_value=entries), \
                 patch.object(updater, 'discover_smk_catalog', return_value=[]):
                result = updater.main([
                    '--mode', 'status', '--target', str(root),
                    '--status-json', str(status_path),
                    '--debug-json', str(root / 'debug.json'),
                ])
            self.assertEqual(result, 0)
            snapshot = json.loads(status_path.read_text())
            self.assertEqual(snapshot['counts']['FM-1']['changed'], 1)
            self.assertEqual(snapshot['counts']['FM-1']['new'], 1)
            self.assertEqual(snapshot['rows'][0]['name'], 'FRASIL')
            self.assertEqual(firmware.read_bytes(), b'original-unchanged')
            self.assertFalse(snapshot['hardware_flash'])


if __name__ == '__main__':
    unittest.main()
