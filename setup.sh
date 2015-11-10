#!/bin/bash

apt-get update
apt-get -y install python-pip emacs
pip install boto bottle cherrypy
