# from __future__ import annotations

import unittest
from typing import Dict, Any, List

from arkimapslib import flavours, steps
from arkimapslib.recipes import Recipe, RecipeStep, Recipes
from arkimapslib.config import Config
from arkimapslib.lint import Lint


class TestLint(Lint):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.step_messages: List[str] = []

    def warn_input(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        raise AssertionError(f"input {name}: {msg}")

    def warn_flavour(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        raise AssertionError(f"flavour {name}: {msg}")

    def warn_postprocessor(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        raise AssertionError("postprocessor {name}: {msg}")

    def warn_recipe(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        raise AssertionError(f"recipe {name}: {msg}")

    def warn_recipe_step(self, msg: str, *, defined_in: str, name: str, step: str, **kwargs) -> None:
        self.step_messages.append(f"{name}: {msg}")


class RecipeStepTestsBase(unittest.TestCase):
    def setUp(self):
        self.config = Config()

    def assert_lints(self, name: str, args: Dict[str, Any]) -> None:
        recipe = Recipe(
            config=self.config,
            name="test",
            defined_in="test.yaml",
            args={"recipe": [{"step": name, **args}]},
        )
        flavour = flavours.Simple(config=self.config, name="test", defined_in="test.yaml", args={})
        lint = TestLint(flavour)
        recipe.lint(lint)
        self.assertEqual(lint.step_messages, [])


class AddSymbolsTest(RecipeStepTestsBase):
    def test_add_symbols(self):
        self.maxDiff = None
        self.assert_lints(
            "add_symbols",
            args={
                "params": {
                    "symbol_type": "marker",
                    "symbol_table_mode": "on",
                    "symbol_min_table": [1, 3, 5, 6, 8, 9, 12],
                    "symbol_max_table": [2, 4, 6, 7, 9, 10, 13],
                    "symbol_marker_table": [18, 18, 18, 18, 18, 18],
                    "symbol_colour_table": ["GREEN", "RED", "BLUE", "YELLOW", "TURQUOISE", "YELLOWISH_ORANGE", "ochre"],
                    "symbol_height_table": [0.6, 0.6, 0.6, 0.6, 0.6, 0.6],
                }
            },
        )
