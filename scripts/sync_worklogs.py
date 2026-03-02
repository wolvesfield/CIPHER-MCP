"""
Sync work logs with a single source of truth.

Source-of-truth directory:
  - CIPHER_WORKLOG_DIR env var, or
  - ~/work-logs

Repository work-logs acts as a mirror/archive only.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path


def copy_if_newer(src: Path, dst: Path) -> bool:
    if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime + 1:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    repo_logs = repo_root / "work-logs"
    canonical_env = os.environ.get("CIPHER_WORKLOG_DIR")
    canonical = (
        Path(canonical_env).expanduser()
        if canonical_env
        else (Path.home() / "work-logs")
    )

    repo_logs.mkdir(parents=True, exist_ok=True)
    canonical.mkdir(parents=True, exist_ok=True)

    repo_files = sorted(repo_logs.glob("*.md"))
    canonical_files = sorted(canonical.glob("*.md"))

    copied_to_canonical = 0
    copied_to_repo = 0

    # One-time bootstrap from repo mirror if canonical is empty.
    if not canonical_files and repo_files:
        for src in repo_files:
            if copy_if_newer(src, canonical / src.name):
                copied_to_canonical += 1

    # Canonical -> mirror sync (ongoing).
    for src in sorted(canonical.glob("*.md")):
        if copy_if_newer(src, repo_logs / src.name):
            copied_to_repo += 1

    print(
        f"[worklog-sync] canonical={canonical} "
        f"repo_mirror={repo_logs} "
        f"copied_to_canonical={copied_to_canonical} copied_to_repo={copied_to_repo}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
