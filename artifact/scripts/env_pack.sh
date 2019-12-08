#! /bin/bash
mkdir ../package
cd ../airly/lib/python3.6/site-packages/
zip -g -r ../../../../package/AirlyAlexaMainFunction.zip . 
cd ../../../../../py/
pwd && ls -al
zip -g ../artifact/package/AirlyAlexaMainFunction.zip AirlyAlexaMainFunction.py
