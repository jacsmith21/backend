#!/usr/bin/env bash
export MONGODB_URI=`heroku config:get MONGODB_URI`
python scripts/reset.py
