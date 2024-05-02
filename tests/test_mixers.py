# from __future__ import annotations

import unittest

from arkimapslib import mixers


class TestMixers(unittest.TestCase):
    def test_register(self) -> None:
        m = mixers.Mixers()
        self.assertEqual(m.registry, {})

        m.register("test", {})
        self.assertEqual(m.registry, {"test": {}})

        with self.assertRaises(RuntimeError):
            m.register("test", {})
