"""Acquire the official, pinned Construction-PPE release without training or conversion.

Run from the repository root. All downloads and extracted originals stay in the
ignored model/data directory. HTTPS certificate verification remains enabled.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tempfile
import urllib.request
import zipfile

import yaml

REVISION = '1bbe9baf26965b46009401db8895d565d73d19ea'
BASE = f'https://raw.githubusercontent.com/ultralytics/ultralytics/{REVISION}/'
CONFIG = BASE + 'ultralytics/cfg/datasets/construction-ppe.yaml'
DOC = BASE + 'docs/en/datasets/detect/construction-ppe.md'
ARCHIVE = 'https://github.com/ultralytics/assets/releases/download/v0.0.0/construction-ppe.zip'
# Observed in this audit, not a publisher-signed digest. Release URLs can change.
EXPECTED_ARCHIVE_SHA256 = 'e5817aa9c73f33e525d76ca6bc6af4e4eac9dcea9bcfef1cfd1a71c09fbc1232'


def sha256(path):
    """Hash files in chunks so archives do not need to fit in memory."""
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def download(url, path):
    """Stream HTTPS to a new file; remove incomplete downloads on failure."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    try:
        with urllib.request.urlopen(url, timeout=120) as response, path.open('xb') as output:
            if not response.url.startswith('https://'):
                raise ValueError('Refusing a non-HTTPS final download URL')
            shutil.copyfileobj(response, output)
    except Exception:
        path.unlink(missing_ok=True)
        raise


def extract_originals(archive, destination):
    """Reject traversal, symlinks and duplicate members before extracting a ZIP."""
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    with zipfile.ZipFile(archive) as zipped:
        seen = set()
        entries = zipped.infolist()
        if sum(entry.file_size for entry in entries) > 4 * 1024**3:
            raise ValueError('Archive expands beyond the 4 GiB safety limit')
        for entry in entries:
            path = PurePosixPath(entry.filename)
            if (not path.parts or path.is_absolute() or '..' in path.parts
                    or '\\' in entry.filename or ':' in entry.filename
                    or stat.S_ISLNK(entry.external_attr >> 16)):
                raise ValueError('Unsafe archive member')
            key = path.as_posix().casefold()
            if key in seen:
                raise ValueError('Duplicate archive member')
            seen.add(key)
        # A failed extraction is discarded rather than leaving an apparent complete dataset.
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
            zipped.extractall(temporary)  # CRC checking remains enabled by zipfile.
            Path(temporary).rename(destination)


def file_manifest(root):
    return {p.relative_to(root).as_posix(): sha256(p)
            for p in sorted(root.rglob('*')) if p.is_file()}


def acquire(workspace):
    workspace = Path(workspace).resolve()
    repo = Path(__file__).resolve().parents[1]
    relative = workspace.relative_to(repo)
    if subprocess.run(['git', '-C', str(repo), 'check-ignore', '-q', str(relative)]).returncode:
        raise ValueError('Acquisition workspace must be Git-ignored')
    if workspace.exists() and any(workspace.iterdir()):
        raise FileExistsError('Use a fresh workspace; existing acquisitions are preserved')
    workspace.mkdir(parents=True, exist_ok=True)
    metadata = {'status': 'started', 'source_revision': REVISION,
                'configuration_url': CONFIG, 'documentation_url': DOC,
                'archive_url': ARCHIVE,
                'attempted_at_utc': datetime.now(timezone.utc).isoformat()}
    try:
        # Each fresh run uses a new workspace; existing data is never overwritten.
        download(CONFIG, workspace / 'official.yaml')
        download(DOC, workspace / 'official-documentation.md')
        config = yaml.safe_load((workspace / 'official.yaml').read_text())
        if config.get('download') != ARCHIVE:
            raise ValueError('Official archive URL changed; review before acquiring')
        documentation = (workspace / 'official-documentation.md').read_text()
        if 'CC BY 4.0' not in documentation or 'Images and annotations' not in documentation:
            raise ValueError('Expected published image/annotation license statement absent')
        metadata.update(configuration_sha256=sha256(workspace / 'official.yaml'),
                        documentation_sha256=sha256(workspace / 'official-documentation.md'),
                        published_data_license='CC BY 4.0')
        archive = workspace / 'construction-ppe.zip'
        download(ARCHIVE, archive)
        metadata.update(archive_sha256=sha256(archive), archive_bytes=archive.stat().st_size,
                        downloaded_at_utc=datetime.now(timezone.utc).isoformat())
        if metadata['archive_sha256'] != EXPECTED_ARCHIVE_SHA256:
            raise ValueError('Archive differs from audited release; review before extraction')
        extract_originals(archive, workspace / 'original')
        manifest = file_manifest(workspace / 'original')
        (workspace / 'original-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        metadata.update(status='downloaded_and_extracted', original_files=len(manifest))
    except Exception as error:
        # Record the failure type, not potentially credential-bearing remote error text.
        metadata.update(status='blocked_or_failed', error_type=type(error).__name__)
        raise
    finally:
        (workspace / 'acquisition.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True,
                        help='Fresh ignored directory, e.g. model/data/audit-2026-11-05')
    args = parser.parse_args()
    print(json.dumps(acquire(args.workspace), indent=2))


if __name__ == '__main__':
    main()
