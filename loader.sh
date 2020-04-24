#!/bin/sh
curl --request GET -sL \
     --url 'https://raw.githubusercontent.com/ph20/fixgitcommits/master/fixgitcommits.py'\
     --output /tmp/fixgitcommits.py
python3 /tmp/fixgitcommits.py