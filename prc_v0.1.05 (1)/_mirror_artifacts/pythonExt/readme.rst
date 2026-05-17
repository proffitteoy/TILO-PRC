========================
Python Extension for PRC
========================

Building Extension
==================

The python extension expects to be built in source code directory.
Edit the setup.cfg to provide the path to eigen headers. The
setup.cfg.linux and setup.cfg.win32 are example configuration files.

Currently, the extension does not build with python3.

To build:

``python  setup.py  build``

The extension should be create in a build directory.  You can copy
the examples/prc_example.py to the build/lib* directory and test it
by cd'ing into that directory and running

``python prc_example.py``

If it works, you can install by running

``python setup.py install``

If you wish to create binary distributions, then

| ``python setup.py bdist_dumb``
| ``python setup.py bdist_wininst``
| ``python setup.py bdist_msi``

could be used.

Generating Extenstion
=====================

Typically, you do not need to do this step.  It currently requires pybindgen and gccxml.
It only needs to be done if the C++ code is changed.

Steps
   1. run pybindgen to generate the extension 
       ``python prc_gen.py > prc_impl.cc``
   2. Edit prc_impl.cc to add import_array() at the start of 
      PyMODINIT_FUNC initprc_impl function.  This is needed to
      initialized numpy arrays.  
   3. build as usual. 
       ``python setup.py build``
       ``python setup.py install``



PRC Module Documentation
========================

Currently not documented.  Look at examples/prc_example.py for usage.
The module can use either dense numpy arrays or sparse arrays from scipy.
The arrays are passed through to the C++ code without copying.

The extension is prc_impl, but normally you will want to import prc as that
provides some help in accessing the automatically generated code in prc_impl.
