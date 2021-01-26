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
> sudo apt-get update

> sudo apt-get install python3-dev python3-pip python3-venv

> (pip3 install setuptools)

opencv

> sudo apt install build-essential cmake git pkg-config libgtk-3-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev libjpeg-dev libpng-dev libtiff-dev \
    gfortran openexr libatlas-base-dev python3-dev python3-numpy \
    libtbb2 libtbb-dev libdc1394-22-dev

pillow

> sudo apt-get install libtiff-dev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl-dev tk-dev python-tk

shapely

> sudo apt-get install libgeos-dev

* ASUS GPIO
> git clone https://github.com/TinkerBoard/gpio_lib_python.git

> cd ASUS_GPIO_PYTHON_PATH/gpio/

> sudo python3 setup.py install
>
* Install python library

> cd embed_gui_imagePATH

* Install opencv & opencv-contrib: https://linuxize.com/post/how-to-install-opencv-on-debian-10/
> pip3 install scikit-build

> pip3 install cython

> pip3 install numpy==1.18.5

> pip3 install opencv-python==3.4.10.37

* Scipy

> sudo apt-get install liblapack-def
> pip3 install scipy

* Python libary etc.
> pip3 install -r requirements.txt

* Install ghostscript: 
> sudo apt-get install ghostscript

## Config
### Debian
* setting.yaml
 ```yaml
TEST_MAMOS: True
 ```
* auto start
> sudo vi /home/.config/lxsession/LXDE/autostart
> add>> @./superscript
> cp superscript ./superscript