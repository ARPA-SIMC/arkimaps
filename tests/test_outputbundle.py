# from __future__ import annotations
import io
import unittest

from arkimapslib.inputs import ModelStep
import arkimapslib.outputbundle as ob


class TestOutputBundle(unittest.TestCase):
    def test_add_products(self):
        products = ob.Products(
            summary=[
                {
                    "flavour": {
                        "name": "flavour",
                        "defined_in": "flavour.yaml",
                    },
                    "recipe": {
                        "name": "recipe",
                        "defined_in": "recipe.yaml",
                        "description": "recipe description",
                        "info": {},
                    },
                    "reftimes": {
                        "2023-06-01 12:00:00": {
                            "inputs": ["input1", "input2"],
                            "steps": {
                                str(ModelStep(12)): 3,
                            },
                            "legend_info": {},
                            "render_stats": {
                                "time_ns": 123_456_789_012,
                            },
                        }
                    },
                    "images": {
                        "test/product": {"georef": {}},
                    },
                },
            ]
        )
        with io.BytesIO() as buf:
            with ob.Writer(out=buf) as writer:
                writer.add_products(products)
