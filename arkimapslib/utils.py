# from __future__ import annotations

import time
from typing import Any, Dict, Tuple

if hasattr(time, "perf_counter_ns"):
    perf_counter_ns = time.perf_counter_ns
else:  # pragma: no cover
    # Polyfill for Python < 3.7
    def perf_counter_ns() -> int:
        return int(time.perf_counter() * 1000000000)


def setdefault_deep(target: Dict[Any, Any], source: Dict[Any, Any], path: Tuple[Any, ...] = ()):
    """Use source as defaults for target, recursing into dicts."""
    for k, v in source.items():
        if k in target:
            old = target[k]
            if isinstance(old, Dict):
                if isinstance(v, Dict):
                    setdefault_deep(old, v, path + (k,))
                else:
                    fmt_path = "/".join(str(p) for p in path)
                    raise ValueError(f"mapping/non-mapping mismatch in dict at {fmt_path}")
            else:
                # Value exists in source, not overriding it
                pass
        else:
            target[k] = v
