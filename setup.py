#!/usr/bin/env python3
# coding: utf-8

from setuptools import setup
import ast

# Read VERSION from arkimaps
version = None
with open("arkimaps") as fd:
    tree = ast.parse(fd.read(), "arkimaps")
    for stm in tree.body:
        if version is not None:
            break
        if not isinstance(stm, ast.Assign):
            continue
        for target in stm.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id != "VERSION":
                continue
            if isinstance(stm.value, ast.Constant):
                version = stm.value.value
                break
            elif isinstance(stm.value, ast.Str):
                version = stm.value.s
                break

if version is None:
    raise RuntimeError("VERSION not found in arkimaps")

setup(
    name='arkimaps',
    version=version,
    python_requires=">= 3.6",
    description="Render maps from model output",
    author='Enrico Zini',
    author_email='enrico@enricozini.org',
    url='https://github.com/ARPA-SIMC/arkimaps/',
    license="http://www.gnu.org/licenses/gpl-3.0.html",
    requires=["Magics", "yaml"],
    extras_require={
        "arkimet": ["arkimet"],
        "nice_python_trace": ["yapf"],
        # distro is only required for the workaround of issue #83 on Fedora 34
        "issue83": ["distro"],
    },
    packages=['arkimapslib'],
    scripts=['arkimaps'],
    include_package_data=True,
)
