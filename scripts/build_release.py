"""Build an allowlisted, reproducible Skill ZIP; never reads runtime caches."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

NAME = 'ecommerce-image-replicator'
VERSION = '0.1.0-mvp.11'
MEMBERS = ('SKILL.md', 'references/input-deltas.md', 'references/diagnostics-and-recovery.md')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def payload(root):
    source = root / 'skills' / NAME
    paths = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    if paths != set(MEMBERS) or any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('Unexpected or linked Skill member')
    result = {}
    for name in MEMBERS:
        data = (source / name).read_bytes().replace(b'\r\n', b'\n')
        text = data.decode('utf-8')
        if re.search(r'(?<![\w])[A-Za-z]:[\\/]|\b(?:run_|thread_)[a-f0-9]{16,}|\b[a-f0-9]{64}\b|dsh-mvp-workspace|Administrator|橙子|青苹果|230g|30片', text, re.I):
            raise ValueError('Private test content in ' + name)
        result[name] = data
    if f'version: {VERSION}' not in result['SKILL.md'].decode():
        raise ValueError('Skill version mismatch')
    for name in MEMBERS:
        for target in re.findall(r'\]\(([^)]+)\)', result[name].decode()):
            if target not in MEMBERS:
                raise ValueError('Invalid Skill resource: ' + target)
    result['LICENSE'] = (root / 'LICENSE').read_bytes().replace(b'\r\n', b'\n')
    return result


def verify(archive, manifest):
    with zipfile.ZipFile(archive) as z:
        expected = {NAME + '/' + f['path']: f for f in manifest['files']}
        if len(z.namelist()) != len(expected) or set(z.namelist()) != set(expected):
            raise ValueError('ZIP members differ from manifest')
        for path, record in expected.items():
            data = z.read(path)
            if len(data) != record['bytes'] or digest(data) != record['sha256']:
                raise ValueError('ZIP content mismatch: ' + path)
    if digest(Path(archive).read_bytes()) != manifest['archive']['sha256']:
        raise ValueError('ZIP digest mismatch')


def build(root, out):
    files = payload(root)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    out.mkdir(parents=True, exist_ok=True)
    archive = out / f'{NAME}-{VERSION}.zip'
    if any(out.iterdir()):
        raise ValueError('Output directory must be empty')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(NAME + '/' + name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    manifest = {'version': VERSION, 'tag': 'v' + VERSION, 'revision': revision,
                'files': [{'path': n, 'bytes': len(d), 'sha256': digest(d)} for n, d in sorted(files.items())],
                'archive': {'name': archive.name, 'sha256': digest(archive.read_bytes())}}
    verify(archive, manifest)
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    for source, name in [('MANUAL.md', 'MANUAL.md'), ('docs/MVP11-DELIVERY.md', 'VALIDATION.md')]:
        (out / name).write_bytes((root / source).read_bytes().replace(b'\r\n', b'\n'))
    sums = ''.join(f'{digest(p.read_bytes())}  {p.name}\n' for p in sorted(out.iterdir()))
    (out / 'SHA256SUMS.txt').write_text(sums, encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(Path(__file__).resolve().parents[1], args.out)))
