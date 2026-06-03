"""Repository cloning utility."""

import os
import shutil
import stat
import tempfile
import subprocess
from typing import Tuple


async def clone_repository(repo_url: str, branch: str = "main") -> Tuple[str, list[str]]:
    """Clone a repository to a temp directory and return path + file list."""
    tmp_dir = tempfile.mkdtemp(prefix="agent-repo-")

    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", branch, repo_url, tmp_dir],
        check=True,
        capture_output=True,
    )

    file_list = []
    for root, dirs, files in os.walk(tmp_dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), tmp_dir)
            # Normalize to POSIX separators so paths stay valid downstream
            # (AST map keys, generated test names, Linux sandbox, PR diffs).
            file_list.append(rel_path.replace(os.sep, "/"))

    return tmp_dir, file_list


def cleanup_repo(path: str) -> None:
    """Remove a cloned repo directory (handles Windows read-only git files)."""
    def _handle_readonly(func, fpath, _exc_info):
        os.chmod(fpath, stat.S_IWRITE)
        func(fpath)

    shutil.rmtree(path, onerror=_handle_readonly)
