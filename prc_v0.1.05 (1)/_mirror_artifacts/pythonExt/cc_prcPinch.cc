static
PyObject * prc_prc(PyObject * PYBINDGEN_UNUSED(dummy), PyObject *args, PyObject *kwargs, PyObject **return_exception)
{
    PyArrayObject *m;
    PyObject *py_retval;
    PyPRCOrderObject *order;
    Pystd__vector__lt___int___gt__ *labels;
    int K;
    PyPRCPrcPolicyStruct *policy;
    const char *keywords[] = {"adjMatrix","order", "labels", "K", "policy", NULL};
    PyPRCPrcReturnStruct *py_prcReturnStruct;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, (char *) "O!O!O!iO!", (char **) keywords, &PyArray_Type, &m, &PyPRCOrderObject_Type, &order, 
            &Pystd__vector__lt___int___gt___Type , &labels, &K, &PyPRCPrcPolicyStruct_Type, &policy)) 
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

   std::vector<int> &lv = *((Pystd__vector__lt___int___gt__ *)labels)->obj;
   if ((long(lv.size()) != long(m->dimensions[0])))
   {
      lv.resize(m->dimensions[0]);
   }

   PRC::DenseNumpyStorage dns(m);
   PRC::prcReturnStruct retval = PRC::pinchRatioClustering(dns, *((PyPRCOrderObject *) order)->obj, lv, K, *((PyPRCPrcPolicyStruct *) policy)->obj);

   py_prcReturnStruct = PyObject_New(PyPRCPrcReturnStruct, &PyPRCPrcReturnStruct_Type);
   py_prcReturnStruct->flags = PYBINDGEN_WRAPPER_FLAG_NONE;
   py_prcReturnStruct->obj = new PRC::prcReturnStruct(retval);
   PyPRCPrcReturnStruct_wrapper_registry[(void *) py_prcReturnStruct->obj] = (PyObject *) py_prcReturnStruct;
   py_retval = Py_BuildValue((char *) "N", py_prcReturnStruct);
   return py_retval;
}

