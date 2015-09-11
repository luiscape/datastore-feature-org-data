#!/bin/bash

#
# Configuration.
#
API_KEY="Foo"
RESOURCE_ID=1f3dbfae-76d1-42da-bc29-b497fa144e90

#
# Running script.
#
source venv/bin/activate
python scripts/create-datastore.py $RESOURCE_ID $API_KEY
