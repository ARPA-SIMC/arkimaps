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
            ["tpdec3h:Decumulate:vg6d_transform --comp-frac-valid=0 '--comp-step=0 03' --comp-stat-proc=1"
             " --comp-full-steps - tpdec3h-decumulated.grib",
             f"sffraction:Expr:expr tpdec3h_2021_1_10_0_0_0+3.grib,{self.model_name}_snowdec3h_2021_1_10_0_0_0+3.grib"
             " sffraction_2021_1_10_0_0_0+3.grib"] +

            # Snow preprocessing
            self.get_snow_preprocessing_log() +

            # Snow decumulation
            ["snowdec3h:Decumulate:vg6d_transform --comp-frac-valid=0 '--comp-step=0 03'"
             f" --comp-stat-proc=1 --comp-full-steps - {self.model_name}_snowdec3h-decumulated.grib"]
        )

        self.assertRenders(orders[0], step=3)

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})

    def get_snow_preprocessing_log(self) -> List[str]:
        if self.model_name == "ifs":
            return []

        return (
            ["snowsum:VG6DTransform:vg6d_transform --output-variable-list=B13205 -"
             f" cosmo_snowsum_2021_1_10_0_0_0+{step}.grib" for step in range(0, 13)] +
            [f"snowcosmo:Or:cosmo_snowsum_2021_1_10_0_0_0+{step}.grib as cosmo_snowcosmo_2021_1_10_0_0_0+{step}.grib"
             for step in range(0, 13)]
        )


add_recipe_test_cases(__name__, "sffraction3h")
