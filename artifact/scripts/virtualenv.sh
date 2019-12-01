
#! /bin/bash

virtualenv ../airly -p python3.6
# create virtualenv called ansible with python3.6.

. ../airly/bin/activate
#activate the virtualenv.

pip install -r ../requirements.txt
# install needed packages inside the virtualenv.