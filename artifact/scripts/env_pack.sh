#! /bin/bash
mkdir ../package
cd ../airly/lib/python3.6/site-packages/
zip -r ../../../../package/AirlyAlexaMainFunction.zip .
cd ../../../..
zip package/AirlyAlexaMainFunction.zip ../py/AirlyAlexaMainFunction.py