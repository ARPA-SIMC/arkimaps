# from __future__ import annotations
import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Type
from unittest import mock

from arkimapslib import cli, outputbundle
from arkimapslib.unittest import system_definitions


class CLITest:
    def create(self, cls: Type[cli.Command], *cmd: str):
        parser = argparse.ArgumentParser(description="Render maps from model output.")
        parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
        parser.add_argument("--debug", action="store_true", help="verbose output")
        # From Python 3.7+, use required=True
        subparsers = parser.add_subparsers(help="sub-command help", dest="command")
        cls.make_subparser(subparsers)

        args = [cls.NAME]
        args.extend(cmd)
        parsed = parser.parse_args(args=args)
        patcher = mock.patch("arkimapslib.cli.DefinitionsCommand._create_defs", return_value=system_definitions())
        patcher.start()
        self.addCleanup(patcher.stop)
        return cls(args=parsed)


class TestPrintArkiQuery(CLITest, unittest.TestCase):
    def test_run(self) -> None:
        cmd = self.create(cli.PrintArkiQuery)
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                cmd.run()

        self.assertEqual(stderr.getvalue(), "")
        self.assertIn("product:", stdout.getvalue())


class TestDocumentRecipes(CLITest, unittest.TestCase):
    def test_run(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            cmd = self.create(cli.DocumentRecipes, "--destdir", tempdir)

            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                with contextlib.redirect_stderr(io.StringIO()) as stderr:
                    cmd.run()

            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")

            docdir = Path(tempdir)
            self.assertIn("t2m.md", [p.name for p in docdir.iterdir()])


class TestDumpRecipes(CLITest, unittest.TestCase):
    def test_run(self) -> None:
        cmd = self.create(cli.DumpRecipes)

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                cmd.run()

        self.assertEqual(stderr.getvalue(), "")
        output = json.loads(stdout.getvalue())
        self.assertIn("inputs", output)


class TestLint(CLITest, unittest.TestCase):
    def test_run(self) -> None:
        cmd = self.create(cli.LintCmd)

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                with self.assertLogs() as log:
                    cmd.run()

        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("INFO:arkimaps:tp (cosmo): checking input", log.output)


class TestDispatch(CLITest, unittest.TestCase):
    def test_run(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            cmd = self.create(cli.Dispatch, tempdir, "testdata/t2m/cosmo_t2m_2021_1_10_0_0_0+12.arkimet")

            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                with contextlib.redirect_stderr(io.StringIO()) as stderr:
                    cmd.run()

            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(stdout.getvalue(), "")

            workdir = Path(tempdir)
            pantry = workdir / "pantry"
            self.assertIn("cosmo_t2m_2021_1_10_0_0_0+12.grib", [p.name for p in pantry.iterdir()])


class TestRender(CLITest, unittest.TestCase):
    def test_run(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            cmd = self.create(cli.Dispatch, tempdir, "testdata/t2m/cosmo_t2m_2021_1_10_0_0_0+12.arkimet")

            with contextlib.redirect_stdout(io.StringIO()):
                with contextlib.redirect_stderr(io.StringIO()):
                    cmd.run()

            workdir = Path(tempdir)
            output = workdir / "output.tar"
            cmd = self.create(cli.Render, tempdir, "--output", output.as_posix())

            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                with contextlib.redirect_stderr(io.StringIO()) as stderr:
                    with self.assertLogs(level="DEBUG") as log:
                        cmd.run()

            self.assertTrue(output.exists())

            self.assertIn(
                "DEBUG:arkimaps.flavours:flavour default:"
                " recipe t2m input t2m available for instants 2021-01-10T00:00:00+012",
                log.output,
            )

            with outputbundle.TarReader(output) as bundle:
                self.assertIn("t2m", bundle.input_summary().inputs)
                # Log is empty here because assertLogs stole it
                # self.assertEqual(len(bundle.log().entries), 334)
                products = bundle.products()
                self.assertEquals(products.flavour["name"], "default")
                self.assertIn("t2m", products.by_recipe)
                self.assertIn("2021-01-10T00:00:00/t2m_default/t2m+012.png", products.by_path)
                data = bundle.load_product("2021-01-10T00:00:00/t2m_default/t2m+012.png")
                self.assertEqual(data[:4], b"\x89PNG")
                data = bundle.load_artifact("version.txt")
                self.assertEqual(data, b"1\n")


class TestPreview(CLITest, unittest.TestCase):
    def test_run(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            cmd = self.create(cli.Dispatch, tempdir, "testdata/t2m/cosmo_t2m_2021_1_10_0_0_0+12.arkimet")

            with contextlib.redirect_stdout(io.StringIO()):
                with contextlib.redirect_stderr(io.StringIO()):
                    cmd.run()

            workdir = Path(tempdir)
            cmd = self.create(cli.Preview, tempdir, "t2m")

            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                with contextlib.redirect_stderr(io.StringIO()) as stderr:
                    with mock.patch("arkimapslib.cli.Preview._display") as mock_run:
                        with self.assertLogs(level="DEBUG") as log:
                            cmd.run()

            self.assertIn("DEBUG:arkimaps.flavours:flavour default: recipe t2m uses inputs: {'t2m'}", log.output)

            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(stdout.getvalue(), "")
            mock_run.assert_called_with(workdir / "2021-01-10T00:00:00/t2m_default/t2m+012.png")
