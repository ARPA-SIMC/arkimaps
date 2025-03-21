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
        self.flavour = flavours.Simple(config=self.config, name="flavour", defined_in="flavour.yaml", args={})
        self.recipe = Recipe(
            config=self.config, name="recipe", defined_in="recipe.yaml", args={"recipe": [{"step": "add_basemap"}]}
        )
        self.input = inputs.Static(
            config=self.config,
            name="test",
            defined_in="test.yaml",
            args={
                "model": "testmodel",
                "mgrib": {"foo": 1},
                "notes": "test notes",
                "path": os.path.join(self.config.static_dir[0], "puntiCitta.geo"),
            },
        )
        self.instant = Instant(reftime=datetime.datetime(2023, 12, 15), step=12)
        self.order = orders.MapOrder(
            flavour=self.flavour,
            recipe=self.recipe,
            input_files={"test": self.input},
            instant=self.instant,
        )
        self.order.output = orders.Output(name="output", relpath="test/output.png", magics_output="test/magics.png")


class InputProcessingStatsTests(BaseFixture, unittest.TestCase):
    def test_inputprocessingstats(self):
        val = ob.InputProcessingStats()
        val.add_computation_log(100_000_000, "mock processing")
        val.used_by.add(self.recipe.name)

        as_json = val.to_jsonable()
        self.assertEqual(as_json, {"computation": [(100000000, "mock processing")], "used_by": ["recipe"]})

        val1 = ob.InputProcessingStats.from_jsonable(as_json)
        self.assertEqual(val1, val)


class InputSummaryTests(BaseFixture, unittest.TestCase):
    def test_inputsummary(self):
        stats = ob.InputProcessingStats()
        stats.add_computation_log(100_000_000, "mock processing")
        stats.used_by.add(self.recipe.name)

        val = ob.InputSummary()
        val.add("test", stats)

        as_json = val.to_jsonable()
        self.assertEqual(as_json, {"test": stats.to_jsonable()})

        val1 = ob.InputSummary.from_jsonable(as_json)
        self.assertEqual(val1, val)


class LogTests(BaseFixture, unittest.TestCase):
    def test_log(self):
        val = ob.Log()
        val.append(ts=12345.67, level=logging.INFO, msg="test message", name="test.logger")

        as_json = val.to_jsonable()
        self.assertEqual(as_json, [{"level": 20, "msg": "test message", "name": "test.logger", "ts": 12345.67}])

        val1 = ob.Log.from_jsonable(as_json)
        self.assertEqual(val1, val)


class ReftimeProductsTests(BaseFixture, unittest.TestCase):
    def test_reftimeproduct(self):
        val = ob.ReftimeProducts()
        val.add_order(self.order)

        as_json = val.to_jsonable()
        self.assertEqual(
            as_json,
            {
                "inputs": ["test"],
                "steps": {"12h": 1},
                "legend_info": None,
                "render_stats": {"time_ns": 0},
                "products": {
                    "test/output.png": {
                        "georef": {"bbox": [-180.0, -90.0, 180.0, 90.0], "epsg": 4326, "projection": "EPSG"}
                    }
                },
            },
        )

        val1 = ob.ReftimeProducts.from_jsonable(as_json)
        self.assertEqual(val1, val)

    def test_legend(self) -> None:
        recipe = Recipe(
            config=self.config,
            name="recipe",
            defined_in="recipe.yaml",
            args={
                "recipe": [
                    {"step": "add_basemap"},
                    {
                        "step": "add_contour",
                        "params": {"legend": "on"},
                    },
                ]
            },
        )
        order = orders.MapOrder(
            flavour=self.flavour,
            recipe=recipe,
            input_files={"test": self.input},
            instant=self.instant,
        )
        order.output = orders.Output("legend", "test/legend.png", "")

        val = ob.ReftimeProducts()
        val.add_order(order)

        as_json = val.to_jsonable()
        self.assertEqual(
            as_json,
            {
                "inputs": ["test"],
                "steps": {"12h": 1},
                "legend_info": {"legend": True},
                "render_stats": {"time_ns": 0},
                "products": {
                    "test/legend.png": {
                        "georef": {"bbox": [-180.0, -90.0, 180.0, 90.0], "epsg": 4326, "projection": "EPSG"}
                    }
                },
            },
        )

        val1 = ob.ReftimeProducts.from_jsonable(as_json)
        self.assertEqual(val1, val)


class RecipeProductsTests(BaseFixture, unittest.TestCase):
    def test_recipeproducts(self) -> None:
        val = ob.RecipeProducts()
        val.add_order(self.order)

        as_json = val.to_jsonable()
        self.assertEqual(
            as_json,
            {
                "flavour": {"defined_in": "flavour.yaml", "name": "flavour"},
                "recipe": {
                    "defined_in": "recipe.yaml",
                    "description": "Unnamed recipe",
                    "info": {},
                    "name": "recipe",
                },
                "reftimes": {"2023-12-15 00:00:00": val.reftimes["2023-12-15 00:00:00"].to_jsonable()},
            },
        )

        val1 = ob.RecipeProducts.from_jsonable(as_json)
        self.assertEqual(val1, val)


class ProductsTests(BaseFixture, unittest.TestCase):
    def test_add_unrendered_products(self):
        flavour = flavours.Simple(config=self.config, name="flavour", defined_in="flavour.yaml", args={})
        recipe = Recipe(config=self.config, name="recipe", defined_in="recipe.yaml", args={})
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

        as_json = val.to_jsonable()
        self.assertEqual(as_json, [val.products[("flavour", "recipe")].to_jsonable()])

        val1 = ob.Products.from_jsonable(as_json)
        self.assertEqual(val1, val)

    def test_by_path(self):
        val = ob.Products()
        val.add_order(self.order)
        self.assertEqual(
            val.by_path,
            {
                "test/output.png": ob.PathInfo(
                    georef={"projection": "EPSG", "epsg": 4326, "bbox": [-180.0, -90.0, 180.0, 90.0]},
                    recipe="recipe",
                )
            },
        )


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
        products.add_order(self.order)

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
                self.assertEqual(reader.input_summary(), input_summary)
                self.assertEqual(reader.log(), log)
                self.assertEqual(reader.products(), products)


class TestZipBundle(BundleTestsMixin, unittest.TestCase):
    reader_cls = ob.ZipReader
    writer_cls = ob.ZipWriter


class TestTarBundle(BundleTestsMixin, unittest.TestCase):
    reader_cls = ob.TarReader
    writer_cls = ob.TarWriter
