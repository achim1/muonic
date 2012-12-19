muonic setup and installation
=============================

Muonic consists of two main parts:
1. the python package `muonic` 
2. a python executable

prerequesitories
-------------------

muonic needs the following packages to be installed (list may not be complete!)

* python-scipy
* python-matplotlib
* python-numpy
* python-qt4
* python-serial


installation with the setup.py script
---------------------------------------

Run the following command in the muonic main directory

`python setup.py install`

This will put the muonic package into your python site-packages directory and alsot the exectuables `muonic` and `which_tty_daq` to your user/bin directory.

The use of python-virtualenv is recommended.

installing muonic without the setup script
---------------------------------------------------

You just need the script `./bin/muonic` to the upper directory and rename it to `muonic.py`.
You can do this by typing

`mv bin/muonic muonic.py`

while being in the muonic main directory.

Afterwards you have to create the folder `muonic_data` in your home directory.

`mkdir ~/muonic_data`



