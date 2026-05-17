import os
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_inc
import numpy

module1 = Extension("prc_impl", 
                  define_macros = [('PY_XML_GEN','1')],
                  #include_dirs=['.','..','/home/drh/include/eigen3','/home/drh/lib/python3.2/site-packages/numpy/core/include/',incdir],
                  include_dirs=['.','..',numpy.get_include()],
#                  libraries= ['rt'],
                  #library_dirs= ['/home/drh/lib'],
                  sources = ["prc_impl.cc"])
#                  sources = ["prc_impl.cc","wrap_numpy.cc"])
#                  sources = ["prc_impl.cc","helper2.cc"])

setup(name="prc", 
      version="0.1.5",
      author='Doug Heisterkamp',
      author_email='drh@ieee.org',
      url='http://www.cs.okstate.edu/~doug/src/prc',
      description='Python bindings to PRC',
      long_description='Python bindings to Pinch Ratio Clusterings (PRC)  and Topologically Intrinsic Lexicographic Ordering (TILO)',
      #license='???',
      #py_modules = ['c_prc'],
      #scripts=['scriptfoo'],
      #package_data=[],
      #data_files=[('examples',['examples/prc_example.py'])],
      py_modules=['prc'],
	ext_modules = [module1])

