# from __future__ import annotations

import unittest
from typing import Dict, Any, List

from arkimapslib import flavours, steps
from arkimapslib.recipes import Recipe, RecipeStep, Recipes
from arkimapslib.config import Config
from arkimapslib.lint import Lint


class TestLint(Lint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.step_messages: List[str] = []

    def warn_input(self, msg: str, *, defined_in: str, name: str, **kwargs: Any) -> None:
        raise AssertionError(f"input {name}: {msg}")

    def warn_flavour(self, msg: str, *, defined_in: str, name: str, **kwargs: Any) -> None:
        raise AssertionError(f"flavour {name}: {msg}")

    def warn_postprocessor(self, msg: str, *, defined_in: str, name: str, **kwargs: Any) -> None:
        raise AssertionError("postprocessor {name}: {msg}")

    def warn_recipe(self, msg: str, *, defined_in: str, name: str, **kwargs: Any) -> None:
        raise AssertionError(f"recipe {name}: {msg}")

    def warn_recipe_step(self, msg: str, *, defined_in: str, name: str, step: str, **kwargs: Any) -> None:
        self.step_messages.append(f"{name}: {msg}")


class RecipeStepTestsBase(unittest.TestCase):
    def setUp(self) -> None:
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
    def test_add_symbols(self) -> None:
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

    def test_compile_args(self) -> None:
        compile_args = steps.AddSymbols.compile_args
        for fp, fdp, r, exp in (
            # Recipe has priority over flavour and defaults
            (
                {"symbol_type": "fparam"},
                None,
                {"symbol_type": "recipe"},
                {"symbol_type": "recipe"},
            ),
            # Flavour has priority over defaults
            (
                {"symbol_type": "fparam"},
                None,
                None,
                {"symbol_type": "fparam"},
            ),
            # Defaults are used when nothing is specified
            (
                None,
                None,
                None,
                {
                    "legend": "off",
                    "symbol_colour": "black",
                    "symbol_height": 0.28,
                    "symbol_marker_index": 15,
                    "symbol_type": "marker",
                },
            ),
            # Flavour default_params are applied over recipe
            (
                None,
                {"symbol_text_position": "left"},
                {"symbol_type": "recipe"},
                {
                    "symbol_type": "recipe",
                    "symbol_text_position": "left",
                },
            ),
            # Flavour default_params are applied over flavour
            (
                {"symbol_type": "flavour"},
                {"symbol_text_position": "left"},
                None,
                {
                    "symbol_type": "flavour",
                    "symbol_text_position": "left",
                },
            ),
            # Flavour default_params are applied over defaults
            (
                None,
                {"symbol_text_position": "left"},
                None,
                {
                    "legend": "off",
                    "symbol_colour": "black",
                    "symbol_height": 0.28,
                    "symbol_marker_index": 15,
                    "symbol_type": "marker",
                    "symbol_text_position": "left",
                },
            ),
        ):
            with self.subTest(fp=fp, fdp=fdp, r=r):
                fspec = steps.AddSymbolsFlavourSpec()
                if fp is not None:
                    fspec.params = steps.AddSymbolsParamsSpec.model_validate(fp)
                if fdp is not None:
                    fspec.default_params = steps.AddSymbolsParamsSpec.model_validate(fdp)
                if r is not None:
                    rargs = {"params": r}
                else:
                    rargs = {}
                self.assertEqual(
                    compile_args(fspec, rargs),
                    {"params": exp},
                )
