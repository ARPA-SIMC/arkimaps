# from __future__ import annotations

import unittest

from arkimapslib.utils import setdefault_deep


class TestSetdefaultDeep(unittest.TestCase):
    def test_empty(self):
        d = {}
        setdefault_deep(d, {})
        self.assertEquals(d, {})

    def test_set(self):
        d = {}
        setdefault_deep(d, {"a": 1, "b": {"c": 2}})
        self.assertEquals(d, {"a": 1, "b": {"c": 2}})

    def test_merge(self):
        d = {"a": 1}
        setdefault_deep(d, {"a": 2, "b": 3})
        self.assertEquals(d, {"a": 1, "b": 3})

    def test_merge_deep(self):
        d = {"a": 1, "b": {"c": 1, "d": 2}}
        setdefault_deep(d, {"a": 2, "b": {"e": 3, "c": 2}})
        self.assertEquals(d, {"a": 1, "b": {"c": 1, "d": 2, "e": 3}})
