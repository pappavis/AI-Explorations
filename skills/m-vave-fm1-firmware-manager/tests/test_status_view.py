# Version: 1.5.1 | Release ChatID: D82F4A61
import importlib.util
import pathlib
import unittest
from unittest.mock import patch

root = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('firmware_status', root / 'scripts/fm1_update.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class StatusViewTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            {'kind': 'FM-1', 'id': 'new', 'version': '2', 'url': 'https://example.test/new'},
            {'kind': 'FM-1', 'id': 'old', 'version': '3', 'url': 'https://example.test/old'},
            {'kind': 'FM-1', 'id': 'same', 'version': '1', 'url': 'https://example.test/same'},
        ]
        self.changes = [
            ('NIEUW', 'FM-1/new', '—', '2', '—', 'https://example.test/new'),
            ('GEWIJZIGD', 'FM-1/old', '2', '3', '2', 'https://example.test/old'),
            ('ONVERANDERD', 'FM-1/same', '1', '1', '1', 'https://example.test/same'),
        ]
    def test_summary_shows_counts_and_versions(self):
        output = m.render_status_summary(self.entries, self.changes, {'FM-1': 2}, '/tmp/example')
        for term in ['FM-1', '3', 'NIEUW', 'GEWIJZIGD', 'ACTUEEL', '2', '/tmp/example']:
            self.assertIn(term, output)
    def test_full_shows_every_firmware_and_versions(self):
        output = m.render_status_full(self.entries, self.changes, {'FM-1': 2}, '/tmp/example')
        for term in ['FM-1/new', 'FM-1/old', 'FM-1/same', 'https://example.test/new', 'GEWIJZIGD']:
            self.assertIn(term, output)
    def test_cli_accepts_full(self):
        with patch.object(m, 'run', return_value=0) as run:
            with patch.object(m, 'DebugLog'):
                self.assertEqual(m.main(['--mode', 'status', '--status-full']), 0)
                self.assertTrue(run.call_args.args[0].status_full)
