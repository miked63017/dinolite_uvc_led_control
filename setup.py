#!/usr/bin/env python

import os

from setuptools import setup
from setuptools import find_packages

def get_requirements():
    dirname = os.path.dirname(__file__)
    try:
        with open(os.path.join(dirname, 'requirements.txt'), 'r') as f:
            lines = f.readlines()
        return map(lambda x: x.replace('\n', ''), lines)
    except IOError:
        print 'What happened to your requirements.txt file?!?'
        exit(1)


setup(name='dinoliteuvccontrol',
      version='0.0.1',
      description='Sample description',
      author="Mike Donlon",
      author_email='mdonlon@rgare.com',
      url='',
      install_requires=get_requirements(),
      include_package_data=True,
      packages=find_packages(),
      scripts=[
                'scripts/dinolite'
              ],
      )
