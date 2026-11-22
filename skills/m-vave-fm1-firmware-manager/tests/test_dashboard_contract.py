# Version: 1.6.0 | Release ChatID: A61E4C92
"""Dashboard contract tests: pure data; no live network or hardware."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import firmware_dashboard as dashboard

class DashboardContract(unittest.TestCase):
    def test_counts_and_order(self):
        entries = [
            {'kind':'FM-1','id':'a','version':'2','url':'https://example.test/a'},
            {'kind':'FM-1','id':'b','version':'1','url':'https://example.test/b'},
            {'kind':'FM-1','id':'c','version':'1','url':'https://example.test/c'},
        ]
        changes = [
            ('GEWIJZIGD','FM-1/a','1','2','1','https://example.test/a'),
            ('NIEUW','FM-1/b','—','1','—','https://example.test/b'),
            ('ONVERANDERD','FM-1/c','1','1','1','https://example.test/c'),
        ]
        state = dashboard.DashboardSnapshot.build(entries, changes, {'FM-1':2}, '/tmp/fm')
        self.assertEqual(state['counts']['FM-1']['changed'], 1)
        self.assertEqual(state['counts']['FM-1']['new'], 1)
        self.assertEqual(state['counts']['FM-1']['current'], 1)
        self.assertEqual(state['rows'][0]['status'], 'GEWIJZIGD')
        self.assertEqual(state['rows'][0]['local_version'], '1')
        self.assertEqual(state['rows'][0]['website_version'], '2')
        self.assertEqual(len(state['rows']), 3)
    def test_ui_labels(self):
        self.assertIn('Nu bijwerken', dashboard.DashboardLabels.PRIMARY_ACTION)
        self.assertIn('Firmware', dashboard.DashboardLabels.TITLE)

if __name__ == '__main__':
    unittest.main()
