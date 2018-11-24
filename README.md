# Curriculum Mapping Backend
This is the backend system for [curriculum mapping frontend](https://github.com/jsmith/curriculummapping).

It is deployed [here](https://royal-canoe-18209.herokuapp.com).

## Environment Setup
Make sure you have MongoDB installed locally. Then run the following commands.
```
pipenv install

# running the application for development
pipenv run python app.py
```

## Deploying
```
./scripts/deploy.sh
```

## Resetting DB
```
# local
python scripts/reset.py

# remote
./scripts/reset_remote.sh
```
