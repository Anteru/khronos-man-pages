#!/bin/bash

rm -rf src
mkdir src

mkdir src/opengl
svn co https://cvs.khronos.org/svn/repos/ogl/trunk/ecosystem/public/sdk/docs/man4/ src/opengl/4.0

mkdir src/opencl
svn co https://cvs.khronos.org/svn/repos/registry/trunk/public/cl/sdk/1.2/docs/man/ src/opencl/1.2
svn co https://cvs.khronos.org/svn/repos/registry/trunk/public/cl/sdk/2.0/docs/man/ src/opencl/2.0

rm -rf build
mkdir build
mkdir build/gl
mkdir build/cl
mkdir build/gl/4.0 build/cl/1.2 build/cl/2.0

mkdir build/offline

wget https://github.com/mathjax/MathJax/zipball/v2.2-latest -O build/offline/mathjax-2.2.zip

rm -rf venv
virtualenv -p python3 venv
source venv/bin/activate
pip install jinja2
pip install beautifulsoup4
pip install lxml
