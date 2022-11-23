# from __future__ import annotations

import unittest

from arkimapslib.recipes import Recipe


class TestRecipes(unittest.TestCase):
    def test_simple(self):
        r = Recipe("test", defined_in="test.yaml", data={
            "recipe": [
                {"step": "add_grib", "grib": "t2m"},
                {"step": "add_user_boundaries"}
            ],
        })
        self.assertEqual(r.name, "test")
        self.assertEqual(r.defined_in, "test.yaml")
        self.assertEqual(len(r.steps), 2)
        self.assertEqual(r.steps[0].name, "add_grib")
        self.assertEqual(r.steps[1].name, "add_user_boundaries")
