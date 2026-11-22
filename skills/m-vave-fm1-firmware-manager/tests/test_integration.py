# Version: 1.5.0 | Release ChatID: B6D9A420
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout, redirect_stderr
from types import SimpleNamespace
from unittest.mock import patch

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'fm1_update.py'
spec = importlib.util.spec_from_file_location('firmware_integration', SOURCE)
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


class IntegrationTests(unittest.TestCase):
    def test_refresh_installs_then_second_refresh_skips_known_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory) / 'library'
            entry = {'kind': 'FM-1', 'id': 'OPN-1', 'name': 'OPN-1',
                     'version': '2.0', 'url': 'https://thefirmwarehub.com/api/convert/lib?id=OPN-1'}
            calls = []

            def fake_download(url, destination):
                calls.append(url)
                with zipfile.ZipFile(destination, 'w') as archive:
                    archive.writestr('OPN-1.wasm', b'wasm')
                    archive.writestr('OPN-1.json', b'{"version":"2.0"}')

            for _ in range(2):
                log = manager.DebugLog(pathlib.Path(directory) / 'log.json', 'refresh')
                args = SimpleNamespace(debug_log=log, target=str(root), no_browser=False,
                                       mode='refresh', list=False, dry_run=False,
                                       temp=directory)
                with patch.object(manager, 'discover_fm_verified', return_value=[entry]), \
                     patch.object(manager, 'discover_smk_catalog', return_value=[]), \
                     patch.object(manager, 'download', side_effect=fake_download), \
                     redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertEqual(manager.run(args), 0)
            self.assertEqual(len(calls), 1)
            self.assertTrue((root / 'OPN-1.wasm').is_file())
            self.assertEqual(json.loads((root / '.firmware-manager.json').read_text())['items']['FM-1/OPN-1']['version'], '2.0')

    def test_invalid_zip_leaves_existing_firmware_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory) / 'library'
            root.mkdir()
            (root / 'OPN-1.wasm').write_bytes(b'old')
            entry = {'kind': 'FM-1', 'id': 'OPN-1', 'name': 'OPN-1',
                     'version': '2.0', 'url': 'https://thefirmwarehub.com/api/convert/lib?id=OPN-1'}
            log = manager.DebugLog(pathlib.Path(directory) / 'log.json', 'refresh')
            args = SimpleNamespace(debug_log=log, target=str(root), no_browser=False,
                                   mode='refresh', list=False, dry_run=False,
                                   temp=directory)

            def fake_bad_download(url, destination):
                destination.write_bytes(b'not-a-zip')

            with patch.object(manager, 'discover_fm_verified', return_value=[entry]), \
                 patch.object(manager, 'discover_smk_catalog', return_value=[]), \
                 patch.object(manager, 'download', side_effect=fake_bad_download), \
                 redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(manager.UpdateError):
                    manager.run(args)
            self.assertEqual((root / 'OPN-1.wasm').read_bytes(), b'old')


if __name__ == '__main__':
    unittest.main()
