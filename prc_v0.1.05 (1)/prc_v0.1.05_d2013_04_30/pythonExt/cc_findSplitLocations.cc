PyObject * prc_findSplitLocation(PyObject * PYBINDGEN_UNUSED(dummy), PyObject *args, PyObject *kwargs, PyObject **return_exception)
{
    PyArrayObject *m;
    PyPRCOrderObject *order;
    int metric=0;
    bool evalAll = 0;
    PyObject *evalObj= NULL;
    const char *keywords[] = {"adjMatrix", "order","metric","evalAllMetrics", NULL};

    // 'p' has been added for predicates in python 3.3, but using an object until 'p' is back ported to 2.7 
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, (char *) "O!O!i|O", (char **) keywords, 
             &PyArray_Type, &m, 
             &PyPRCOrderObject_Type, &order,
             &metric,&evalObj)) {
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

   if (evalObj != NULL)
      evalAll = PyObject_IsTrue(evalObj);

   if (metric <0 || metric >3)
   {
        PyErr_SetString(PyExc_TypeError, "unknown prcMetric value.");
        return NULL;
   }
   PRC::prcMetricEnum metricType = PRC::prcMetricEnumFromInt(metric); 
   PRC::DenseNumpyStorage dns(m);
   PRC::OrderObject &oo = *((PyPRCOrderObject *) order)->obj;
   long loc;
   double value;
   PRC::prcMetricValues res = PRC::findSplitLocation(oo,loc,value,dns,oo,metricType,evalAll);

   PyPRCPrcMetricValues *py_prcMetricValues;
   py_prcMetricValues = PyObject_New(PyPRCPrcMetricValues, &PyPRCPrcMetricValues_Type);
   py_prcMetricValues->flags = PYBINDGEN_WRAPPER_FLAG_NONE;
   py_prcMetricValues->obj = new PRC::prcMetricValues(res);
   PyPRCPrcMetricValues_wrapper_registry[(void *) py_prcMetricValues->obj] = (PyObject *) py_prcMetricValues;
   return Py_BuildValue("dlN",value,loc,py_prcMetricValues);
}
