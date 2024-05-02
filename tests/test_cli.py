# from __future__ import annotations
import argparse
import contextlib
import io
import unittest
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
