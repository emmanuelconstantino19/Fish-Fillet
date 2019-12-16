#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   	echo "This script must be run as root" 
   	exit 1
else
	# PyGame
	echo "Installing PyGame"
	python3 -m pip install -U pygame --user

    echo "Installing OpenGL"
    pip3 install PyOpenGL PyOpenGL_accelerate

    echo "Installing FreeGLUT"
    sudo apt-get install freeglut3-dev

    echo "Installing Scipy"
    pip3 install scipy

    echo ""
    echo "Setup Done!"

fi