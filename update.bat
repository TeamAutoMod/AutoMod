@echo off

git pull origin master
py -3  -m pip install -U -r requirements.txt --user
py -3 launch.py