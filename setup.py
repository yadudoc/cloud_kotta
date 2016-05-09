#!/usr/bin/env python

from setuptools import setup, find_packages

setup(# For machines
    name              = 'task_engine',
    version           = '2.0',
    packages          = find_packages(),
    entry_points      = { 'console_scripts': 
                          ['task_executor = task_engine.worker.task_executor:main']
                         },
    install_requires  = [ 'argparse',
                          'boto',
                          'boto3',
                          'bottle',
                          'beaker',
                          'cherrypy',
                          'pycrypto',
                          'python-dateutil',
                          'requests'],
    package_dir       = {'task_engine' : 'task_engine/'},
    package_data      = {'task_engine' : ['templates/*tpl']},
    # For humans
    description       ='Task management suite for TuringCompute.net',
    url               ='https://github.com/yadudoc/task_engine',
    author            ='Yadu Nand Babuji',
    author_email      ='yadu@uchicago.edu',
    license           ='Proprietary',
    zip_safe          =False)
