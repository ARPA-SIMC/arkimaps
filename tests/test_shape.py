# from __future__ import annotations
import os
from pathlib import Path
from unittest import TestCase

from PIL import Image

from arkimapslib.render import Renderer
from arkimapslib.unittest import Workdir


class TestShape(TestCase):
    def setUp(self):
        self.workdir = Workdir(self)

    def test_load_recipes(self):
        self.workdir.add_yaml_file(
            "flavours.yaml",
            {
                "flavours": [
                    {
                        "name": "emro_web",
                        "steps": {
                            "add_basemap": {
                                "params": {
                                    "page_id_line": "off",
                                    "output_width": 1280,
                                    # Explicitly not using output_cairo_transparent_background
                                    # to get a fully white image
                                    # "output_cairo_transparent_background": True,
                                    "subpage_map_projection": "EPSG:3857",
                                    "subpage_lower_left_longitude": 9.19514626509458,
                                    "subpage_lower_left_latitude": 43.714193665380236,
                                    "subpage_upper_right_longitude": 12.8283195496460942,
                                    "subpage_upper_right_latitude": 45.14257501046363,
                                    "page_frame": "off",
                                    "subpage_frame": "off",
                                    "skinny_mode": "on",
                                    "page_x_length": 7.265,
                                    "page_y_length": 4,
                                    "super_page_x_length": 7.265,
                                    "super_page_y_length": 4,
                                    "subpage_x_length": 7.265,
                                    "subpage_y_length": 4,
                                    "subpage_x_position": 0,
                                    "subpage_y_position": 0,
                                    "map_grid": "off",
                                }
                            }
                        },
                    }
                ]
            },
        )
        self.workdir.add_yaml_file(
            "cut.yaml",
            {
                "inputs": {
                    "t2m": [
                        {"model": "cosmo", "arkimet": "product:GRIB1,,2,11;level:GRIB1,105,2"},
                    ]
                },
                "recipe": [
                    {"step": "add_basemap"},
                    {"step": "add_grib", "grib": "t2m"},
                    {"step": "add_contour"},
                ],
            },
        )
        kitchen = self.workdir.as_kitchen("arkimet")
        kitchen.pantry.fill(path=Path("testdata/t2m/cosmo_t2m_2021_1_10_0_0_0+12.arkimet"))
        orders = kitchen.make_orders(flavour="emro_web")

        renderer = Renderer(config=kitchen.config, workdir=kitchen.workdir)
        order = renderer.render_one(orders[0])
        imagefile = os.path.join(kitchen.workdir, order.output.relpath)
        img = Image.open(imagefile, mode="r")
        # TODO: this should change to match the cut region
        self.assertEqual(img.getbbox(), (0, 0, 1280, 705))
        img.close()

        # print(order.outputs[0].relpath)
        # print(order.outputs)

        # import subprocess
        # subprocess.run(["find", self.workdir.path])
        # subprocess.run(["find", kitchen.workdir])
        # subprocess.run(["/bin/bash"])
