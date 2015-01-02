#! /bin/bash

cd homeSound
sudo echo "Starting"
sudo ./homeSound.py > home.log 2>&1 &
./webApp.py > web.log 2>&1 &

