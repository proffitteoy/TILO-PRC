static
PyObject * prc_sp_prc(PyObject * PYBINDGEN_UNUSED(dummy), PyObject *args, PyObject *kwargs, PyObject **return_exception)
{
    int nnz; // number non zero
    PyArrayObject *data; // non zero values
    PyArrayObject *indices; // row indices
    PyArrayObject *indptr; // col start indices
    PyObject *py_retval;
    PyPRCOrderObject *order;
    Pystd__vector__lt___int___gt__ *labels;
    int K;
    int N;
    PyPRCPrcPolicyStruct *policy;
    const char *keywords[] = {"N","nnz","data","indices","indptr","order", "labels", "K", "policy", NULL};
    PyPRCPrcReturnStruct *py_prcReturnStruct;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, (char *) "iiO!O!O!O!O!iO!", (char **) keywords,
             &N, 
             &nnz,
             &PyArray_Type, &data,
             &PyArray_Type, &indices,
             &PyArray_Type, &indptr,
             &PyPRCOrderObject_Type, &order,
             &Pystd__vector__lt___int___gt___Type , &labels, 
             &K, 
             &PyPRCPrcPolicyStruct_Type, &policy)) 
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

   std::vector<int> &lv = *((Pystd__vector__lt___int___gt__ *)labels)->obj;
   if ((long(lv.size()) != long(N)))
   {
      lv.resize(N);
   }

   PRC::SparseCSCNumpyStorage sp_csc(N,nnz,data,indices,indptr);

   PRC::prcReturnStruct retval = PRC::pinchRatioClustering(sp_csc,
          *((PyPRCOrderObject *) order)->obj, lv, K, *((PyPRCPrcPolicyStruct *) policy)->obj);

   py_prcReturnStruct = PyObject_New(PyPRCPrcReturnStruct, &PyPRCPrcReturnStruct_Type);
   py_prcReturnStruct->flags = PYBINDGEN_WRAPPER_FLAG_NONE;
   py_prcReturnStruct->obj = new PRC::prcReturnStruct(retval);
   PyPRCPrcReturnStruct_wrapper_registry[(void *) py_prcReturnStruct->obj] = (PyObject *) py_prcReturnStruct;
   py_retval = Py_BuildValue((char *) "N", py_prcReturnStruct);
   return py_retval;
}

