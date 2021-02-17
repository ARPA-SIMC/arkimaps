#from __future__ import annotations
from typing import List
import subprocess
import tempfile
import logging
import os
import shlex


log = logging.getLogger("arkimaps.preprocess")


def run_script(cmd: List[str]):
    log.info("Running command %s", " ".join(shlex.quite(c) for c in cmd))
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        log.warning("Command %s exited with code %d", " ".join(shlex.quite(c) for c in cmd), e.returncode)
        log.warning("Script stderr: %r", e.stderr)
        raise


def outfile(workdir: str, source: str) -> str:
    intermediate_dir = os.path.join(workdir, "intermediate")
    os.makedirs(intermediate_dir, exist_ok=True)
    root, ext = os.path.splitext(source)
    fd, pathname = tempfile.mkstemp(suffix=ext, dir=intermediate_dir)
    os.close(fd)
    return pathname


def preprocess_cp(workdir: str, source: str, **kw) -> str:
    """
    Example preprocessor that just copies the input to the output
    """
    res = outfile(workdir, source)
    run_script(["cp", source, res])
    return res
