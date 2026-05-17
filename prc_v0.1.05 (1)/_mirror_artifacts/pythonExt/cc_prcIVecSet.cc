static
PyObject * prc_ivecSet(PyObject * PYBINDGEN_UNUSED(dummy), PyObject *args, PyObject *kwargs, PyObject **return_exception)
{
    Pystd__vector__lt___int___gt__ *vec;
    int loc;
    int value;
    const char *keywords[] = {"vec","loc","value", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, (char *) "O!ii", (char **) keywords,  &Pystd__vector__lt___int___gt___Type , &vec, &loc,&value)) 
    {
       {
            PyObject *exc_type, *traceback;
            PyErr_Fetch(&exc_type, return_exception, &traceback);
            Py_XDECREF(exc_type);
            Py_XDECREF(traceback);
        }
        return NULL;
    }
   std::vector<int> &lv = *((Pystd__vector__lt___int___gt__ *)vec)->obj;
   if (long(lv.size()) <= long(loc) )
   {
        PyErr_SetString(PyExc_TypeError, "Location out of range");
        return NULL;
   }
   lv[loc] = value;
   Py_INCREF(Py_None);
   return Py_None;
}

