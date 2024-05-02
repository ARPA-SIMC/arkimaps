# from __future__ import annotations

import datetime
import unittest
from arkimapslib.types import Instant, ModelStep


class TestModelStep(unittest.TestCase):
    def test_from_int(self) -> None:
        ms = ModelStep(0)
        self.assertEqual(str(ms), "0h")
        ms = ModelStep(12)
        self.assertEqual(str(ms), "12h")

    def test_from_str(self) -> None:
        ms = ModelStep("0h")
        self.assertEqual(str(ms), "0h")

        ms = ModelStep("12h")
        self.assertEqual(str(ms), "12h")

        with self.assertRaises(ValueError):
            ModelStep("30m")
        with self.assertRaises(ValueError):
            ModelStep("43200s")
        with self.assertRaises(ValueError):
            ModelStep("")
        with self.assertRaises(ValueError):
            ModelStep("h")

    def test_from_invalid(self) -> None:
        with self.assertRaises(TypeError):
            ModelStep(None)

    def test_from_modelstep(self) -> None:
        ms = ModelStep(ModelStep("0h"))
        self.assertEqual(str(ms), "0h")

        ms = ModelStep(ModelStep("12h"))
        self.assertEqual(str(ms), "12h")

    def test_equals(self) -> None:
        ms = ModelStep(0)
        self.assertEqual(ms, 0)
        self.assertEqual(ms, "0h")
        self.assertEqual(ms, ModelStep("0h"))
        self.assertTrue(ms.is_zero())
        self.assertNotEqual(ms, Instant(datetime.datetime(2024, 1, 1), 0))

        ms = ModelStep(12)
        self.assertEqual(ms, 12)
        self.assertEqual(ms, "12h")
        self.assertEqual(ms, ModelStep("12h"))
        self.assertFalse(ms.is_zero())

        with self.assertRaises(ValueError):
            ms == "720m"
        with self.assertRaises(ValueError):
            ms == "43200s"
        with self.assertRaises(ValueError):
            ms == ""
        with self.assertRaises(ValueError):
            ms == "h"

    def test_lt(self) -> None:
        ms = ModelStep(0)
        self.assertLess(ms, 1)
        self.assertLess(ms, "1h")
        self.assertLess(ms, ModelStep("1h"))

        ms = ModelStep(12)
        self.assertLess(ms, 13)
        self.assertLess(ms, "13h")
        self.assertLess(ms, ModelStep("13h"))

        with self.assertRaises(ValueError):
            ms < "721m"
        with self.assertRaises(ValueError):
            ms < "43201s"
        with self.assertRaises(ValueError):
            ms < ""
        with self.assertRaises(ValueError):
            ms < "h"
        with self.assertRaises(TypeError):
            ms < Instant(datetime.datetime(2024, 1, 1), 0)

    def test_le(self) -> None:
        ms = ModelStep(0)
        self.assertLessEqual(ms, 0)
        self.assertLessEqual(ms, "0h")
        self.assertLessEqual(ms, ModelStep("0h"))
        self.assertLessEqual(ms, 1)
        self.assertLessEqual(ms, "1h")
        self.assertLessEqual(ms, ModelStep("1h"))

        ms = ModelStep(12)
        self.assertLessEqual(ms, 12)
        self.assertLessEqual(ms, "12h")
        self.assertLessEqual(ms, ModelStep("12h"))
        self.assertLessEqual(ms, 13)
        self.assertLessEqual(ms, "13h")
        self.assertLessEqual(ms, ModelStep("13h"))

        with self.assertRaises(ValueError):
            ms <= "721m"
        with self.assertRaises(ValueError):
            ms <= "43201s"
        with self.assertRaises(ValueError):
            ms <= ""
        with self.assertRaises(ValueError):
            ms <= "h"
        with self.assertRaises(TypeError):
            ms <= Instant(datetime.datetime(2024, 1, 1), 0)

    def test_suffix(self) -> None:
        ms = ModelStep(0)
        self.assertEqual(ms.suffix(), "+000")
        ms = ModelStep(12)
        self.assertEqual(ms.suffix(), "+012")

    def test_hashable(self) -> None:
        steps = {
            ModelStep(0),
            ModelStep(12),
        }
        self.assertEqual(len(steps), 2)
        self.assertEqual(
            steps,
            {
                ModelStep(0),
                ModelStep(12),
            },
        )

    def test_from_grib1(self) -> None:
        self.assertEqual(ModelStep.from_grib1(60, 0), ModelStep(1))
        with self.assertRaises(NotImplementedError):
            ModelStep.from_grib1(30, 0)
        self.assertEqual(ModelStep.from_grib1(1, 1), ModelStep(1))
        self.assertEqual(ModelStep.from_grib1(1, 2), ModelStep(24))
        self.assertEqual(ModelStep.from_grib1(2, 2), ModelStep(48))
        with self.assertRaises(NotImplementedError):
            ModelStep.from_grib1(1, 3)
        with self.assertRaises(NotImplementedError):
            ModelStep.from_grib1(1, 4)
        with self.assertRaises(NotImplementedError):
            ModelStep.from_grib1(1, 5)
        with self.assertRaises(NotImplementedError):
            ModelStep.from_grib1(1, 6)
        with self.assertRaises(NotImplementedError):
            ModelStep.from_grib1(1, 7)
        with self.assertRaises(ValueError):
            ModelStep.from_grib1(1, 8)
        with self.assertRaises(ValueError):
            ModelStep.from_grib1(1, 9)
        self.assertEqual(ModelStep.from_grib1(1, 10), ModelStep(3))
        self.assertEqual(ModelStep.from_grib1(1, 11), ModelStep(6))
        self.assertEqual(ModelStep.from_grib1(1, 12), ModelStep(12))
        self.assertEqual(ModelStep.from_grib1(3600, 254), ModelStep(1))
        with self.assertRaises(NotImplementedError):
            ModelStep.from_grib1(60, 254)

    def test_from_timedef(self) -> None:
        self.assertEqual(ModelStep.from_timedef(60, 0), ModelStep(1))
        with self.assertRaises(NotImplementedError):
            ModelStep.from_timedef(30, 0)
        self.assertEqual(ModelStep.from_timedef(1, 1), ModelStep(1))
        self.assertEqual(ModelStep.from_timedef(1, 2), ModelStep(24))
        self.assertEqual(ModelStep.from_timedef(2, 2), ModelStep(48))
        with self.assertRaises(NotImplementedError):
            ModelStep.from_timedef(1, 3)
        with self.assertRaises(NotImplementedError):
            ModelStep.from_timedef(1, 4)
        with self.assertRaises(NotImplementedError):
            ModelStep.from_timedef(1, 5)
        with self.assertRaises(NotImplementedError):
            ModelStep.from_timedef(1, 6)
        with self.assertRaises(NotImplementedError):
            ModelStep.from_timedef(1, 7)
        with self.assertRaises(ValueError):
            ModelStep.from_timedef(1, 8)
        with self.assertRaises(ValueError):
            ModelStep.from_timedef(1, 9)
        self.assertEqual(ModelStep.from_timedef(1, 10), ModelStep(3))
        self.assertEqual(ModelStep.from_timedef(1, 11), ModelStep(6))
        self.assertEqual(ModelStep.from_timedef(1, 12), ModelStep(12))
        self.assertEqual(ModelStep.from_timedef(3600, 13), ModelStep(1))
        with self.assertRaises(NotImplementedError):
            ModelStep.from_timedef(60, 13)


class TestInstant(unittest.TestCase):
    def test_access(self) -> None:
        i = Instant(datetime.datetime(2023, 1, 1), 12)
        self.assertEqual(i.reftime, datetime.datetime(2023, 1, 1))
        self.assertEqual(i.step, 12)

        self.assertTrue(i == Instant(datetime.datetime(2023, 1, 1), 12))
        self.assertTrue(i != Instant(datetime.datetime(2023, 1, 1), 11))
        self.assertTrue(i != Instant(datetime.datetime(2023, 1, 2), 12))

    def test_lt(self) -> None:
        i = Instant(datetime.datetime(2023, 1, 1), 12)
        self.assertLess(i, Instant(datetime.datetime(2023, 1, 1), 13))
        self.assertLess(i, Instant(datetime.datetime(2023, 1, 2), 12))
        self.assertFalse(Instant(datetime.datetime(2023, 1, 1), 13) < i)
        self.assertFalse(Instant(datetime.datetime(2023, 1, 2), 12) < i)

        self.assertGreater(Instant(datetime.datetime(2023, 1, 1), 13), i)
        self.assertGreater(Instant(datetime.datetime(2023, 1, 2), 12), i)
        self.assertFalse(i > Instant(datetime.datetime(2023, 1, 1), 13))
        self.assertFalse(i > Instant(datetime.datetime(2023, 1, 1), 12))
        with self.assertRaises(TypeError):
            i < None

    def test_le(self) -> None:
        i = Instant(datetime.datetime(2023, 1, 1), 12)
        self.assertLessEqual(i, Instant(datetime.datetime(2023, 1, 1), 13))
        self.assertLessEqual(i, Instant(datetime.datetime(2023, 1, 2), 12))
        self.assertLessEqual(Instant(datetime.datetime(2023, 1, 1), 12), i)
        self.assertFalse(Instant(datetime.datetime(2023, 1, 1), 13) <= i)
        self.assertFalse(Instant(datetime.datetime(2023, 1, 2), 12) <= i)

        self.assertGreaterEqual(Instant(datetime.datetime(2023, 1, 1), 13), i)
        self.assertGreaterEqual(Instant(datetime.datetime(2023, 1, 2), 12), i)
        self.assertGreaterEqual(Instant(datetime.datetime(2023, 1, 1), 12), i)
        self.assertFalse(i >= Instant(datetime.datetime(2023, 1, 1), 13))
        self.assertFalse(i >= Instant(datetime.datetime(2023, 1, 2), 12))

        with self.assertRaises(TypeError):
            i <= None
        with self.assertRaises(TypeError):
            i >= None
