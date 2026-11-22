import io, tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hunter


def bank():
    data = bytes([0] * 4096)
    checksum = (-sum(data)) & 127
    return b'\xf0\x43\x00\x09\x20\x00' + data + bytes([checksum, 0xf7])


class TestHunter(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(hunter.valid_bank(bank()))

    def test_checksum(self):
        corrupted = bytearray(bank()); corrupted[6] = 1
        self.assertFalse(hunter.valid_bank(corrupted))

    def test_wrong_format(self):
        corrupted = bytearray(bank()); corrupted[3] = 0
        self.assertFalse(hunter.valid_bank(corrupted))

    def test_zip(self):
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, 'w') as z:
            z.writestr('folder/TEST.SYX', bank())
            z.writestr('README.txt', 'no')
        entries = list(hunter.unpack_candidates('patches.zip', bio.getvalue()))
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0][1], bank())

    def test_collect_deduplicates(self):
        config = {'sources': [{'id': 'test', 'type': 'direct', 'urls': ['https://example.com/a.syx', 'https://example.com/b.syx']} ]}
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(hunter, 'http_get', return_value=bank()):
                result = hunter.collect(config, temp)
            self.assertEqual(result['verified_new'], 1)
            self.assertEqual(result['duplicates'], 1)
            self.assertEqual(len(list((Path(temp) / '01_VERIFIED').glob('*.syx'))), 1)


if __name__ == '__main__':
    unittest.main()
