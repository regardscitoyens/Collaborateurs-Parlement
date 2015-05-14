#!/bin/bash

sudo apt-get install pip
sudo pip install virtualenv virtualenvwrapper
source $(which virtualenvwrapper.sh)
mkvirtualenv --no-site-packages collabs
workon collabs
pip install -r requirements.txt
add2virtualenv .
deactivate

