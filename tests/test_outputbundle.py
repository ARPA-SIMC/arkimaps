# from __future__ import annotations
import datetime
import io
import tempfile
import unittest
from typing import Type

import arkimapslib.outputbundle as ob
from arkimapslib import flavours, orders
from arkimapslib.config import Config
from arkimapslib.inputs import ModelStep, Instant
from arkimapslib.recipes import Recipe


class BundleTestsMixin:
    reader_cls: Type[ob.Reader]
    writer_cls: Type[ob.Writer]

    def setUp(self):
        super().setUp()
        self.config = Config()

    def test_serialize(self):
        with tempfile.NamedTemporaryFile() as tf:
            input_summary = ob.InputSummary()
            log = ob.Log()
            log.append(ts=1702662773.123, level=10, msg="test message", name="test")
            products = ob.Products()

            with self.writer_cls(out=tf) as writer:
                writer.add_input_summary(input_summary)
                writer.add_log(log)
                writer.add_products(products)
                with io.BytesIO(b"product1") as fd:
                    writer.add_product("p/product1.txt", fd)
                with io.BytesIO(b"artifact1") as fd:
                    writer.add_artifact("a/artifact1.txt", fd)

            tf.flush()

            with self.reader_cls(path=tf.name) as reader:
                self.assertCountEqual(
                    reader.find(),
                    [
                        "version.txt",
                        "inputs.json",
                        "log.json",
                        "products.json",
                        "p/product1.txt",
                        "a/artifact1.txt",
                    ],
                )

    def test_add_unrendered_products(self):
        flavour = flavours.SimpleFlavour(config=self.config, name="flavour", defined_in="flavour.yaml")
        recipe = Recipe(name="recipe", defined_in="recipe.yaml")
        order = orders.MapOrder(
            flavour=flavour,
            recipe=recipe,
            input_files={},
            instant=Instant(reftime=datetime.datetime(2023, 12, 15), step=12),
        )

        products = ob.Products()
        with self.assertRaisesRegex(AssertionError, "not been rendered"):
            products.add_orders(recipe=recipe, orders=[order])

    def test_add_products(self):
        flavour = flavours.SimpleFlavour(config=self.config, name="flavour", defined_in="flavour.yaml")
        recipe = Recipe(name="recipe", defined_in="recipe.yaml")
        order = orders.MapOrder(
            flavour=flavour,
            recipe=recipe,
            input_files={},
            instant=Instant(reftime=datetime.datetime(2023, 12, 15), step=12),
        )
        order.output = orders.Output(name="output", relpath="test/output.png", magics_output="test/magics.png")

        products = ob.Products()
        products.add_orders(recipe=recipe, orders=[order])

        # products = ob.Products(
        #     summary=[
        #         {
        #             "flavour": {
        #                 "name": "flavour",
        #                 "defined_in": "flavour.yaml",
        #             },
        #             "recipe": {
        #                 "name": "recipe",
        #                 "defined_in": "recipe.yaml",
        #                 "description": "recipe description",
        #                 "info": {},
        #             },
        #             "reftimes": {
        #                 "2023-06-01 12:00:00": {
        #                     "inputs": ["input1", "input2"],
        #                     "steps": {
        #                         str(ModelStep(12)): 3,
        #                     },
        #                     "legend_info": {},
        #                     "render_stats": {
        #                         "time_ns": 123_456_789_012,
        #                     },
        #                 }
        #             },
        #             "images": {
        #                 "test/product": {"georef": {}},
        #             },
        #         },
        #     ]
        # )
        with io.BytesIO() as buf:
            with self.writer_cls(out=buf) as writer:
                writer.add_products(products)


class TestZipBundle(BundleTestsMixin, unittest.TestCase):
    reader_cls = ob.ZipReader
    writer_cls = ob.ZipWriter


class TestTarBundle(BundleTestsMixin, unittest.TestCase):
    reader_cls = ob.TarReader
    writer_cls = ob.TarWriter
