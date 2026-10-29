import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release', ROOT / 'scripts/build_release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def test_build_and_reject_tampering(self):
        cache = ROOT / '.cache/release-tests'
        cache.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache) as tmp:
            out = Path(tmp) / 'output'
            manifest = release.build(ROOT, out)
            archive = out / manifest['archive']['name']
            self.assertEqual(len(manifest['files']), 4)
            self.assertEqual(json.loads((out / 'manifest.json').read_text()), manifest)
            release.verify(archive, manifest)
            with zipfile.ZipFile(archive, 'a') as z:
                z.writestr('ecommerce-image-replicator/private.txt', 'unexpected')
            with self.assertRaises(ValueError):
                release.verify(archive, manifest)
            with self.assertRaises(ValueError):
                release.build(ROOT, out)


if __name__ == '__main__':
    unittest.main()
