# from __future__ import annotations

import unittest

from arkimapslib.recipes import Recipe, Recipes
from arkimapslib.config import Config


class TestRecipe(unittest.TestCase):
    def setUp(self):
        self.config = Config()

    def test_simple(self):
        r = Recipe(
            config=self.config,
            name="test",
            defined_in="test.yaml",
            args={"recipe": [{"step": "add_grib", "grib": "t2m"}, {"step": "add_user_boundaries"}]},
        )
        self.assertEqual(r.name, "test")
        self.assertEqual(r.defined_in, "test.yaml")
        self.assertEqual(len(r.steps), 2)
        self.assertEqual(r.steps[0].name, "add_grib")
        self.assertEqual(r.steps[1].name, "add_user_boundaries")

    def test_inherit_simple(self):
        r1 = Recipe(
            config=self.config,
            name="test",
            defined_in="test.yaml",
            args={"recipe": [{"step": "add_grib", "grib": "t2m"}, {"step": "add_user_boundaries"}]},
        )

        r2 = Recipe(config=self.config, **Recipe.inherit(name="test1", defined_in="test1.yaml", parent=r1))

        self.assertEqual(r2.name, "test1")
        self.assertEqual(r2.defined_in, "test1.yaml")
        self.assertEqual(len(r2.steps), 2)
        self.assertEqual(r2.steps[0].name, "add_grib")
        self.assertEqual(r2.steps[0].args, {"grib": "t2m"})
        self.assertEqual(r2.steps[1].name, "add_user_boundaries")

    def test_inherit_change_args(self):
        r1 = Recipe(
            config=self.config,
            name="test",
            defined_in="test.yaml",
            args={"recipe": [{"step": "add_grib", "grib": "t2m", "id": "input"}, {"step": "add_user_boundaries"}]},
        )

        r2 = Recipe(
            config=self.config,
            **Recipe.inherit(
                name="test1",
                defined_in="test1.yaml",
                parent=r1,
                change={
                    "input": {"grib": "t2mavg"},
                },
            )
        )

        self.assertEqual(r2.name, "test1")
        self.assertEqual(r2.defined_in, "test1.yaml")
        self.assertEqual(len(r2.steps), 2)
        self.assertEqual(r2.steps[0].name, "add_grib")
        self.assertEqual(r2.steps[0].id, "input")
        self.assertEqual(r2.steps[0].args, {"grib": "t2mavg"})
        self.assertEqual(r2.steps[1].name, "add_user_boundaries")

    def test_inherit_change_params(self):
        r1 = Recipe(
            config=self.config,
            name="test",
            defined_in="test.yaml",
            args={"recipe": [{"step": "add_basemap", "params": {"a": 1, "b": 2, "c": 3}, "id": "basemap"}]},
        )

        r2 = Recipe(
            config=self.config,
            **Recipe.inherit(
                name="test1",
                defined_in="test1.yaml",
                parent=r1,
                change={
                    "basemap": {"params": {"b": 3, "c": None}},
                },
            )
        )

        self.assertEqual(r2.name, "test1")
        self.assertEqual(r2.defined_in, "test1.yaml")
        self.assertEqual(len(r2.steps), 1)
        self.assertEqual(r2.steps[0].name, "add_basemap")
        self.assertEqual(r2.steps[0].id, "basemap")
        self.assertEqual(r2.steps[0].args, {"params": {"a": 1, "b": 3}})


class TestRecipes(unittest.TestCase):
    def setUp(self):
        self.config = Config()

    def test_inherit(self):
        recipes = Recipes(config=self.config)
        recipes.add(
            name="test",
            defined_in="test.yaml",
            recipe=[{"step": "add_grib", "grib": "t2m", "id": "input"}, {"step": "add_user_boundaries"}],
        )

        recipes.add_derived(
            name="test1",
            defined_in="test1.yaml",
            extends="test",
            change={
                "input": {"grib": "t2mavg"},
            },
        )

        recipes.resolve_derived()

        r2 = recipes.get("test1")
        self.assertEqual(r2.name, "test1")
        self.assertEqual(r2.defined_in, "test1.yaml")
        self.assertEqual(len(r2.steps), 2)
        self.assertEqual(r2.steps[0].name, "add_grib")
        self.assertEqual(r2.steps[0].id, "input")
        self.assertEqual(r2.steps[0].args, {"grib": "t2mavg"})
        self.assertEqual(r2.steps[1].name, "add_user_boundaries")

    def test_loop(self):
        recipes = Recipes(config=self.config)
        recipes.add_derived(name="test1", defined_in="test1.yaml", extends="test2")
        recipes.add_derived(name="test2", defined_in="test2.yaml", extends="test1")

        with self.assertRaises(Exception):
            recipes.resolve_derived()
