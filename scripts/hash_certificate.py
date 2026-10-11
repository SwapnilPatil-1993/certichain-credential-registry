"""Print a 32-byte SHA-256 fingerprint suitable for the CertiChain demo."""
import hashlib
import pathlib
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: python scripts/hash_certificate.py <file>")

path = pathlib.Path(sys.argv[1])
if not path.is_file():
    raise SystemExit(f"File not found: {path}")

print("0x" + hashlib.sha256(path.read_bytes()).hexdigest())

