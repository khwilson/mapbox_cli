#!/usr/b/env python
import os
from setuptools import find_packages, setup
import warnings


def parse_requirements(filename):
  """ Parse a requirements file ignoring comments and -r inclusions of other files """
  reqs = []
  with open(filename, 'r') as f:
    for line in f:
      hash_idx = line.find('#')
      if hash_idx >= 0:
        line = line[:hash_idx]
      line = line.strip()
      if line:
        reqs.append(line)
  return reqs


with open(os.path.join('mapbox_cli', 'VERSION'), 'r') as f:
  version = f.read().strip()


with open('README.md', 'r') as f:
  readme = f.read().strip()


setup(
  name="mapbox_cli",
  version=version,
  url="https://github.com/khwilson/mapbox_cli",
  author="Kevin Wilson",
  author_email="khwilson@gmail.com",
  license="Apache v2.0",
  packages=find_packages(),
  package_data={'mapbox_cli': ['VERSION']},
  install_requires=parse_requirements('requirements.txt'),
  tests_require=parse_requirements('requirements.testing.txt'),
  description="A simple CLI for doing routine tasks with Mapbox's API",
  entry_points="""
  [console_scripts]
  mapbox=mapbox_cli.cli:cli
  """,
  long_description="\n" + readme
)
