#!/bin/bash

#
# Installing Python dependencies.
#
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt