#!/bin/bash

# BEGIN: Clean public folder
rm -rf ./public/*
# END: Clean public folder

# BEGIN: Copying requirements.txt
cp ./requirements.txt ./public/
# END: Copying requirements.txt

# BEGIN: Recursive copying
cp -r ./src/* ./public/
# END: Recursive copying
