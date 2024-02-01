# ADHD

### Introduction

This project is for esp32 only

2 sensors 12 channels 2 classes recognization

+ 0 - stop

+ 1 - move

### Enviroment

```
conda with python 3.9
```

### Project Setup

```
cd src/client

conda install --yes --file requirements.txt
```

or you can install the packages manually as following:

### Packages

```
bokeh
jupyter notebook
tensorflow
jupyter_bokeh
paho-mqtt
```

### Configuration

Please add `config.yaml` into `/src/client/config.yaml`

This is the example:

```
mqtt:
  broker_address: '127.0.0.1'
  port: 1883
  username: ESP32_Monitor
  password: '123'
  topic: AD1
data:
  length: 30
  channels: 12
  window_size: 30
  train_data_path: ../../public/data/csv/
env:
  test: true
model:
  pb_path: ../../public/pb/new_test30_1.pb
```

### Compile and Hot-Reload for Development

```
cd /src/client
jupyter notebook monitor.py
```

