PyObject * prc_sp_tilo(PyObject * PYBINDGEN_UNUSED(dummy), PyObject *args, PyObject *kwargs, PyObject **return_exception)
{
    PyObject *py_retval;
    PyPRCOrderObject *order;
    PyPRCTiloPolicyStruct *policy = NULL;
    int nnz; // number non zero
    PyArrayObject *data; // non zero values
    PyArrayObject *indices; // row indices
    PyArrayObject *indptr; // col start indices
    int N;

    const char *keywords[] = {"N","nnz","data","indices","indptr","order", "policy", NULL};
    PyPRCPrcCountsStruct *py_prcCountsStruct;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, (char *) "iiO!O!O!O!|O!", (char **) keywords, 
             &N, 
             &nnz,
             &PyArray_Type, &data,
             &PyArray_Type, &indices,
             &PyArray_Type, &indptr,
             &PyPRCOrderObject_Type, &order, 
             &PyPRCTiloPolicyStruct_Type, &policy)) 
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


   PRC::SparseCSCNumpyStorage sp_csc(N,nnz,data,indices,indptr);
   PRC::prcCountsStruct retval = PRC::TILO(*((PyPRCOrderObject *) order)->obj, sp_csc, (policy ? (*((PyPRCTiloPolicyStruct *) policy)->obj) : PRC::tiloPolicyStruct()));
   py_prcCountsStruct = PyObject_New(PyPRCPrcCountsStruct, &PyPRCPrcCountsStruct_Type);
   py_prcCountsStruct->flags = PYBINDGEN_WRAPPER_FLAG_NONE;
   py_prcCountsStruct->obj = new PRC::prcCountsStruct(retval);
   PyPRCPrcCountsStruct_wrapper_registry[(void *) py_prcCountsStruct->obj] = (PyObject *) py_prcCountsStruct;
   py_retval = Py_BuildValue((char *) "N", py_prcCountsStruct);
   return py_retval;
}

