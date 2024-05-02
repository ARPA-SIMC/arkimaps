# from __future__ import annotations
import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Type

from arkimapslib import cli


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
                cmd.run()

        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "")
