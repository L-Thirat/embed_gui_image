# Line Detection

## Requirements
* Windows / Debian 9.5 (Mamos)
* python 3.5

## Installation
### Windows
* Install python library
> pip3 install -r requirements.txt

### Debian
* Important lib
> sudo apt-get install python3-dev python3-pip
> pip3 install --upgrade pip setuptools
* ASUS GPIO
> git clone https://github.com/TinkerBoard/gpio_lib_python.git
> cd ASUS_GPIO_PYTHON_PATH/gpio/
> sudo python3 setup.py install
* Install opencv & opencv-contrib: https://linuxize.com/post/how-to-install-opencv-on-debian-10/
* Install ghostscript: 
> sudo apt-get install ghostscript
* Install python library
> pip3 install -r requirements.txt

## Config
### Debian
* setting.yaml
 ```yaml
TEST_MAMOS: True
 ```