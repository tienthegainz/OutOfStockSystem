# OutOfStockSystem
Hanoi university of Science and Technology's Thesis by Ha Viet Tien

# Requirement
- Computer with camera or Raspberry

# Installation
There are several important package you need to install like:
- Python3
- Torch
- OpenCV
- PIL
- Numpy
- Celery
- Redis
- ReactJs
- SOcketIO

# Setup
- First thing first, please copy and make your own `.env` file.

- Copy `raspberry` folder to your raspberry PI

# Use the app
## Run the server
- Turn on redis
- Run background worker:
```
celery -A worker.celery worker -P solo --loglevel=INFO
```
- Run server:
```
python app.py
```

## Run the frontend
- Run with `yarn` or `npm` of your choice

## Run the raspberry PI
- Run with python 3:
```
python run.py
```

