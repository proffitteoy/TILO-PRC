PyObject * prc_refine_tilo(PyObject * PYBINDGEN_UNUSED(dummy), PyObject *args, PyObject *kwargs, PyObject **return_exception)
{
    PyObject *py_retval;
    PyArrayObject *m;
    PyPRCOrderObject *order;
    PyPRCTiloPolicyStruct *policy = NULL;
    const char *keywords[] = {"adjMatrix","order", "policy", NULL};
    PyPRCPrcCountsStruct *py_prcCountsStruct;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, (char *) "O!O!|O!", (char **) keywords, &PyArray_Type, &m, &PyPRCOrderObject_Type, &order, &PyPRCTiloPolicyStruct_Type, &policy)) 
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

   PRC::DenseNumpyStorage dns(m);
   PRC::prcCountsStruct retval = PRC::RefineTILO(*((PyPRCOrderObject *) order)->obj, dns, (policy ? (*((PyPRCTiloPolicyStruct *) policy)->obj) : PRC::tiloPolicyStruct()));
   py_prcCountsStruct = PyObject_New(PyPRCPrcCountsStruct, &PyPRCPrcCountsStruct_Type);
   py_prcCountsStruct->flags = PYBINDGEN_WRAPPER_FLAG_NONE;
   py_prcCountsStruct->obj = new PRC::prcCountsStruct(retval);
   PyPRCPrcCountsStruct_wrapper_registry[(void *) py_prcCountsStruct->obj] = (PyObject *) py_prcCountsStruct;
   py_retval = Py_BuildValue((char *) "N", py_prcCountsStruct);
   return py_retval;
}

