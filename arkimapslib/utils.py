# from __future__ import annotations

import time

if hasattr(time, "perf_counter_ns"):
    perf_counter_ns = time.perf_counter_ns
else:
    # Polyfill for Python < 3.7
    def perf_counter_ns() -> int:
        return int(time.perf_counter() * 1000000000)
