static PyObject * prc_test_dense_numpy(PyObject * PYBINDGEN_UNUSED(dummy), PyObject *args, PyObject *kwargs, PyObject **return_exception)
{
    PyArrayObject *m;
    PyPRCOrderObject *order;
    const char *keywords[] = {"adjMatrix","order", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, (char *) "O!O!", (char **) keywords, &PyArray_Type, &m, &PyPRCOrderObject_Type, &order )) 
    {
       {
            PyObject *exc_type, *traceback;
            PyErr_Fetch(&exc_type, return_exception, &traceback);
            Py_XDECREF(exc_type);
            Py_XDECREF(traceback);
        }
        return NULL;
    }
   if(m==NULL)
   {
        PyErr_SetString(PyExc_TypeError, "Failed to convert matrix");
        return NULL;
   }
   if ((m->nd != 2) || (m->dimensions[0] != m->dimensions[1]))
   {
        PyErr_SetString(PyExc_TypeError, "matrix is not 2D and square.");
        return NULL;
   }

   PRC::DenseNumpyStorage p(m);
   PRC::OrderObject &o  = *((PyPRCOrderObject *) order)->obj;

   std::cout << "Testing Dense Numpy Storage " << std::endl;
   std::cout << "p.rows() = "<<p.rows() << std::endl;
   std::cout << "p.cols() = "<<p.cols() << std::endl;
   std::cout << "Matrix = " << std::endl;
   for (int r = 0; r < p.rows(); ++r)
   {
      std::cout << "    ";
      for(int c=0; c<p.cols(); ++c)
      {
         std::cout << p.getCoeff(r,c) << " ";
      }
      std::cout << std::endl;
   }
   std::cout << "degrees = ";
   for (int r = 0; r < p.rows(); ++r)
   {
      std::cout << p.degree(r) << " ";
   }
   std::cout << std::endl;
   for (int r = 0; r < p.rows(); ++r)
   {
      for(int c=0; c<p.cols(); ++c)
      {
      std::cout << "   slope("<<r<<","<<c<<") = " << p.slope(r,c,o) << std::endl;
      }
   }
   Py_INCREF(Py_None);
   return Py_None;
}
