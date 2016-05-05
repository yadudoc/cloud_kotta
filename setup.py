#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='task_engine',
      packages    = find_packages(),
      entry_points= { 'console_scripts': ['task_executor = task_engine.worker.task_executor:__main__'] },
      install_requires=[ 'argparse',
                         'boto',
                         'boto3',
                         'bottle',
                         'beaker',
                         'cherrypy',
                         'pycrypto',
                         'python-dateutil',
                         'requests'],

      version='2.0',
          
      description='Task management suite for TuringCompute.net',
      url='https://github.com/yadudoc/task_engine',
      author='Yadu Nand Babuji',
      author_email='yadu@uchicago.edu',
      license='Proprietary',
      zip_safe=False)
