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
            if not isinstance(stm.value, ast.Constant):
                continue
            version = stm.value.value
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
    install_requires=["setuptools-git"],
    extras_require={
        "arkimet": ["arkimet"],
        "nice_python_trace": ["yapf"],
    },
    packages=['arkimapslib'],
    scripts=['arkimaps'],
    include_package_data=True,
)
