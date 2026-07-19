from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://raw.githubusercontent.com/commaai/comma2k19/master/Example_1/b0c9d2329ad1606b%7C2018-08-02--08-34-47/40/"
FILES = ["processed_log/CAN/speed/t", "processed_log/CAN/speed/value"]


def main() -> None:
    root = Path("data/public/comma2k19")
    entries = []
    for relative in FILES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        request = Request(BASE + relative, headers={"User-Agent": "AutoGuard-Edge/0.1"})
        with urlopen(request, timeout=90) as response:  # noqa: S310 fixed official URL
            target.write_bytes(response.read())
        entries.append({"path": relative, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    (root / "manifest.json").write_text(json.dumps({"dataset": "comma2k19", "files": entries}, indent=2))
    print(root)


if __name__ == "__main__":
    main()
