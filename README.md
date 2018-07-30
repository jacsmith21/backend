# Curriculum Mapping Backend
This is the backend system for [curriculum mapping frontend](https://github.com/jacsmith21/curriculummapping).

It is deployed [here](https://royal-canoe-18209.herokuapp.com).

## Environment Setup
```
pip install -r requirements.txt

# running the application for development
python app.py
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
