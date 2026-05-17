static
PyObject * prc_test_sp_csc(PyObject * PYBINDGEN_UNUSED(dummy), PyObject *args, PyObject *kwargs, PyObject **return_exception)
{
    int nnz; // number non zero
    PyArrayObject *data; // non zero values
    PyArrayObject *indices; // row indices
    PyArrayObject *indptr; // col start indices
    PyPRCOrderObject *order;
    int N;
    const char *keywords[] = {"N","nnz","data","indices","indptr","order",  NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, (char *) "iiO!O!O!O!", (char **) keywords,
             &N, 
             &nnz,
             &PyArray_Type, &data,
             &PyArray_Type, &indices,
             &PyArray_Type, &indptr,
             &PyPRCOrderObject_Type, &order
             )) 
    {
       {
            PyObject *exc_type, *traceback;
            PyErr_Fetch(&exc_type, return_exception, &traceback);
            Py_XDECREF(exc_type);
            Py_XDECREF(traceback);
        }
        return NULL;
    }

   if(data==NULL)
   {
        PyErr_SetString(PyExc_TypeError, "Failed to convert data to numpy array of values");
        return NULL;
   }
   if(indices==NULL)
   {
        PyErr_SetString(PyExc_TypeError, "Failed to convert indices to numpy array of values");
        return NULL;
   }
   if(indptr==NULL)
   {
        PyErr_SetString(PyExc_TypeError, "Failed to convert indptr to numpy array of values");
        return NULL;
   }


   if ((data->nd != 1) || (data->dimensions[0] != nnz))
   {
        PyErr_SetString(PyExc_TypeError, "data is not 1D and length equal nnz");
        return NULL;
   }
   if ((indices->nd != 1) || (indices->dimensions[0] != nnz))
   {
        PyErr_SetString(PyExc_TypeError, "indices is not 1D and length equal nnz");
        return NULL;
   }
   if ((indptr->nd != 1) || (indptr->dimensions[0] != N+1))
   {
        PyErr_SetString(PyExc_TypeError, "indptr is not 1D and length equal N");
        return NULL;
   }

   PRC::SparseCSCNumpyStorage p(N,nnz,data,indices,indptr);
   PRC::OrderObject &o  = *((PyPRCOrderObject *) order)->obj;
   std::cout << "Testing Sparse CSC Storage " << std::endl;
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
