# from __future__ import annotations
import datetime
import io
import logging
import os
import tempfile
import unittest
from typing import Type

import arkimapslib.outputbundle as ob
from arkimapslib import flavours, inputs, orders
from arkimapslib.config import Config
from arkimapslib.inputs import Instant
from arkimapslib.recipes import Recipe
from arkimapslib.types import ModelStep


class BaseFixture:
    def setUp(self):
        super().setUp()
        self.config = Config()
        self.flavour = flavours.Simple(config=self.config, name="flavour", defined_in="flavour.yaml")
        self.recipe = Recipe(
            config=self.config, name="recipe", defined_in="recipe.yaml", recipe=[{"step": "add_basemap"}]
        )
        self.input = inputs.Static(
            config=self.config,
            name="test",
            defined_in="test.yaml",
            model="testmodel",
            mgrib={"foo": 1},
            notes="test notes",
            path=os.path.join(self.config.static_dir[0], "puntiCitta.geo"),
        )
        self.instant = Instant(reftime=datetime.datetime(2023, 12, 15), step=12)
        self.order = orders.MapOrder(
            flavour=self.flavour,
            recipe=self.recipe,
            input_files={"test": self.input},
            instant=self.instant,
        )
        self.order.output = orders.Output(name="output", relpath="test/output.png", magics_output="test/magics.png")


class TestTypes(BaseFixture, unittest.TestCase):
    def test_inputprocessingstats(self):
        val = ob.InputProcessingStats()
        val.add_computation_log(100_000_000, "mock processing")
        val.used_by.add(self.recipe.name)

        as_json = val.to_jsonable()
        val1 = ob.InputProcessingStats.from_jsonable(as_json)
        # TODO: inspect val1

    def test_inputsummary(self):
        stats = ob.InputProcessingStats()
        stats.add_computation_log(100_000_000, "mock processing")
        stats.used_by.add(self.recipe.name)

        val = ob.InputSummary()
        val.add("test", stats)

        as_json = val.to_jsonable()
        val1 = ob.InputSummary.from_jsonable(as_json)
        # TODO: inspect val1

    def test_reftimeorders(self):
        val = ob.ReftimeOrders()
        val.add(self.order)

        as_json = val.to_jsonable()
        val1 = ob.ReftimeOrders.from_jsonable(as_json)
        # TODO: inspect val1

    def test_recipeorders(self):
        val = ob.RecipeOrders()
        val.add(self.order)

        as_json = val.to_jsonable()
        val1 = ob.RecipeOrders.from_jsonable(as_json)
        # TODO: inspect val1

    def test_recipeorders_legend(self):
        val = ob.RecipeOrders()
        val.add(self.order)
        self.assertIsNone(val.legend_info)

        recipe = Recipe(
            config=self.config,
            name="recipe",
            defined_in="recipe.yaml",
            recipe=[
                {"step": "add_basemap"},
                {
                    "step": "add_contour",
                    "params": {"legend": "on"},
                },
            ],
        )
        order = orders.MapOrder(
            flavour=self.flavour,
            recipe=recipe,
            input_files={"test": self.input},
            instant=self.instant,
        )

        val = ob.RecipeOrders()
        val.add(order)
        self.assertEqual(
            val.legend_info,
            {
                "legend": True,
            },
        )

    def test_productinfo(self):
        val = ob.ProductInfo()
        val.add_recipe(self.recipe)
        val.add_instant(self.instant)
        val.add_georef({"lat": 45.0, "lon": 11.0})

        as_json = val.to_jsonable()
        val1 = ob.ProductInfo.from_jsonable(as_json)
        # TODO: inspect val1

    def test_log(self):
        val = ob.Log()
        val.append(ts=12345.67, level=logging.INFO, msg="test message", name="test.logger")

        as_json = val.to_jsonable()
        val1 = ob.Log.from_jsonable(as_json)
        # TODO: inspect val1

    def test_add_unrendered_products(self):
        flavour = flavours.Simple(config=self.config, name="flavour", defined_in="flavour.yaml")
        recipe = Recipe(config=self.config, name="recipe", defined_in="recipe.yaml")
        order = orders.MapOrder(
            flavour=flavour,
            recipe=recipe,
            input_files={},
            instant=Instant(reftime=datetime.datetime(2023, 12, 15), step=12),
        )

        products = ob.Products()
        with self.assertRaisesRegex(AssertionError, "not been rendered"):
            products.add_order(order)

    def test_products(self):
        val = ob.Products()
        val.add_order(self.order)

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

        as_json = val.to_jsonable()
        val1 = ob.Products.from_jsonable(as_json)
        # TODO: inspect val1


class BundleTestsMixin(BaseFixture):
    reader_cls: Type[ob.Reader]
    writer_cls: Type[ob.Writer]

    def test_product(self):
        product = b"TEST DATA"

        with tempfile.NamedTemporaryFile() as tf:
            with self.writer_cls(out=tf) as writer:
                with io.BytesIO(product) as fd:
                    writer.add_product("test/test.png", fd)

            tf.flush()

            with self.reader_cls(path=tf.name) as reader:
                p1 = reader.load_product("test/test.png")

        self.assertEqual(p1, product)

    def test_artifact(self):
        artifact = b"TEST DATA"

        with tempfile.NamedTemporaryFile() as tf:
            with self.writer_cls(out=tf) as writer:
                with io.BytesIO(artifact) as fd:
                    writer.add_artifact("test/test.bin", fd)

            tf.flush()

            with self.reader_cls(path=tf.name) as reader:
                p1 = reader.load_artifact("test/test.bin")

        self.assertEqual(p1, artifact)

    def test_serialize(self):
        stats = ob.InputProcessingStats()
        stats.add_computation_log(100_000_000, "mock processing")
        stats.used_by.add(self.recipe.name)

        input_summary = ob.InputSummary()
        input_summary.add("test", stats)

        log = ob.Log()
        log.append(ts=1.5, level=2, msg="message", name="logname")

        products = ob.Products()
        products.flavour = {"name": "test"}
        products.by_recipe["rtest"] = recipe_orders = ob.RecipeOrders()
        recipe_orders.by_reftime[datetime.datetime(2023, 7, 1)] = ro = ob.ReftimeOrders()
        ro.inputs.add("test")
        ro.steps[ModelStep(17)] = 1
        ro.legend_info = {"bar": 2}
        ro.render_time_ns = 12345
        products.by_path["test"] = ob.ProductInfo(recipe="recipe", reftime=datetime.datetime(2023, 7, 1), step=17)

        with tempfile.NamedTemporaryFile() as tf:
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

                self.assertEqual(reader.version(), "1")
                self.assertEqual(reader.input_summary().to_jsonable(), input_summary.to_jsonable())
                self.assertEqual(reader.log().entries, log.entries)
                self.assertEqual(reader.products().to_jsonable(), products.to_jsonable())


class TestZipBundle(BundleTestsMixin, unittest.TestCase):
    reader_cls = ob.ZipReader
    writer_cls = ob.ZipWriter


class TestTarBundle(BundleTestsMixin, unittest.TestCase):
    reader_cls = ob.TarReader
    writer_cls = ob.TarWriter
