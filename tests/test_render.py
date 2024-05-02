# from __future__ import annotations
import os
import tempfile
import unittest
from pathlib import Path

from arkimapslib.config import Config
from arkimapslib.render import Renderer


class TestRender(unittest.TestCase):
    def test_issue83(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            workdir = Path(tempdir)
            renderer = Renderer(Config(), workdir)
            with renderer.override_env():
                import Magics
                from Magics import macro

                output = macro.output(output_formats=["png"], output_name=os.path.join(workdir, "issue83"))
                parts = []
                parts.append(
                    macro.mmap(
                        **{
                            "subpage_map_projection": "mercator",
                            "subpage_lower_left_longitude": 5.1,
                            "subpage_lower_left_latitude": 43.0,
                            "subpage_upper_right_longitude": 15.0,
                            "subpage_upper_right_latitude": 47.5,
                            "subpage_map_vertical_longitude": 10.3,
                        }
                    )
                )
                parts.append(
                    macro.msymb(
                        **{
                            "symbol_type": "marker",
                            "symbol_marker_index": 15,
                            "legend": "off",
                            "symbol_colour": "black",
                            "symbol_height": 0.28,
                        }
                    )
                )

                has_issue83 = False
                try:
                    macro.plot(output, *parts)
                except Magics.Magics.MagicsError as e:
                    if "ProjP: cannot create crs to crs" in str(e):
                        has_issue83 = True
                    else:
                        raise

                if has_issue83:
                    self.fail(
                        "this system seems to have trouble locating proj.db. See"
                        " https://github.com/ARPA-SIMC/arkimaps/issues/83 or"
                        " https://www.enricozini.org/blog/2021/debian/an-educational-debugging-session/"
                        " for details, and set PROJ_LIB=/usr/share/proj (or the"
                        " equivalent path in your system) as a workaround"
                    )
