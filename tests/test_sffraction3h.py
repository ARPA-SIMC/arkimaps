# from __future__ import annotations
from typing import List

from arkimapslib.unittest import add_recipe_test_cases


class SFFRACTION3HMixin:
    def test_dispatch(self):
        self.maxDiff = None
        self.fill_pantry(extra_sample_dirs=["sf3h"], step=3)

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual(
            # Precipitation decumulation
            ["tpdec3h:Decumulate:vg6d_transform '--comp-step=0 03' --comp-stat-proc=1 --comp-frac-valid=0"
             " --comp-full-steps - tpdec3h-decumulated.grib",
             "sffraction3h:SFFraction:sffraction tpdec3h_2021_1_10_0_0_0+3.grib,snowdec3h_2021_1_10_0_0_0+3.grib"
             " sffraction3h_2021_1_10_0_0_0+3.grib"] +

            # Snow preprocessing
            self.get_snow_preprocessing_log() +

            # Snow decumulation
            ["snowdec3h:Decumulate:vg6d_transform '--comp-step=0 03'"
             " --comp-stat-proc=1 --comp-frac-valid=0 --comp-full-steps - snowdec3h-decumulated.grib"]
        )

        self.assertRenders(orders[0], step=3)

        self.assertMgribArgsEqual(
                orders[0], cosmo={'grib_automatic_scaling': False}, ifs={'grib_automatic_scaling': False})

    def get_snow_preprocessing_log(self) -> List[str]:
        if self.model_name == "ifs":
            return [f"snow:Or:ifs_sf_2021_1_10_0_0_0+{step}.grib as snow_2021_1_10_0_0_0+{step}.grib"
                    for step in range(3, 13, 3)]
        else:
            return (
                ["snowsum:VG6DTransform:vg6d_transform --output-variable-list=B13205 -"
                 f" snowsum_2021_1_10_0_0_0+{step}.grib" for step in range(0, 13)] +
                [f"snow:Or:snowsum_2021_1_10_0_0_0+{step}.grib as snow_2021_1_10_0_0_0+{step}.grib"
                 for step in range(0, 13)]
            )


add_recipe_test_cases(__name__, "tiles/sffraction3h")
