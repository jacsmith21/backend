#!/usr/bin/env bash
export CODE=`cat CODE`
heroku config:set CODE=${CODE}
git push heroku master
