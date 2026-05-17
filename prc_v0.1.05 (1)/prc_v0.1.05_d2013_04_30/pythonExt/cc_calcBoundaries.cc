PyObject * prc_CalcBoundaries(PyObject * PYBINDGEN_UNUSED(dummy), PyObject *args, PyObject *kwargs, PyObject **return_exception)
{
    PyArrayObject *m;
    PyPRCOrderObject *order;
    const char *keywords[] = {"adjMatrix", "order", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, (char *) "O!O!", (char **) keywords, &PyArray_Type, &m, &PyPRCOrderObject_Type, &order)) {
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
   PRC::OrderObject &oo = *((PyPRCOrderObject *) order)->obj;
   PRC::calcBoundaries(oo.boundary(),dns,  oo);
   Py_INCREF(Py_None);
   return Py_None;
}
