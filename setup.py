#!/usr/bin/env python

from setuptools import setup

setup(name='task_engine',
      version='2.0',
      description='Task management suite for TuringCompute.net',
      url='https://github.com/yadudoc/task_engine',
      author='Yadu Nand Babuji',
      author_email='yadu@uchicago.edu',
      license='Proprietary',
      packages=['task_executor'],
      scripts=['bin/task_executor.py'],
      entry_points={
          'console_scripts': [
              'task_executor = task_engine.worker.task_executor.__main__:main'
          ]
      install_requires=[ 'argparse',
                         'boto',
                         'bottle',
                         'beaker',
                         'cherrypy',
                         'pycrypto',
                         'requests'],
      zip_safe=False)
