# Version: 1.5.0 | Release ChatID: B6D9A420
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest
from contextlib import redirect_stderr

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'fm1_update.py'
spec = importlib.util.spec_from_file_location('firmware_progress', SOURCE)
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


class ProgressTests(unittest.TestCase):
    def test_human_progress_contains_firmware_and_url(self):
        output = io.StringIO()
        with redirect_stderr(output):
            manager.ProgressView().show('download', 'Download gestart', {
                'firmware': 'FM-1/OPN-1', 'index': 1, 'total': 3,
                'url': 'https://thefirmwarehub.com/api/convert/lib?id=OPN-1',
                'version': '2.0', 'local_version': '1.0', 'archive': '0.zip'
            })
        self.assertIn('[001/003]', output.getvalue())
        self.assertIn('OPN-1', output.getvalue())
        self.assertIn('Websiteversie', output.getvalue())
        self.assertIn('Bron', output.getvalue())

    def test_progress_bar_is_rendered(self):
        output = io.StringIO()
        with redirect_stderr(output):
            manager.ProgressView().show('validation', 'ZIP gevalideerd', {
                'firmware': 'FM-1/OPN-1', 'index': 1, 'total': 2,
                'files': ['OPN-1.aot', 'OPN-1.json']
            })
        self.assertIn('50%', output.getvalue())
        self.assertIn('OPN-1.aot', output.getvalue())

    def test_json_contains_named_firmware(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / 'firmware-debug.json'
            log = manager.DebugLog(path, 'refresh')
            log.event('download', 'Download gestart', firmware='FM-1/OPN-1', index=1, total=2)
            self.assertEqual(json.loads(path.read_text())['events'][0]['firmware'], 'FM-1/OPN-1')


if __name__ == '__main__':
    unittest.main()
