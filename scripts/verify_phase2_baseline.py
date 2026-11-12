"""Compare a rebuilt directory against a frozen SHA-256 manifest."""
import argparse
import hashlib
import json
from pathlib import Path


def manifest(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    expected = json.loads(args.baseline.read_text())
    actual = manifest(args.directory)
    changed = sorted(key for key in set(expected) | set(actual) if expected.get(key) != actual.get(key))
    if changed:
        raise SystemExit('构建哈希不一致\n' + '\n'.join(changed))
    print(f'一期与第 1 步构建逐字一致，{len(actual)} 个文件 SHA-256 全部相同。')


if __name__ == '__main__':
    main()
