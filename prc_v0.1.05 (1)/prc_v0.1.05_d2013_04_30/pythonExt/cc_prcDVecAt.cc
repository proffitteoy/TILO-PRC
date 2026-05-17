static
PyObject * prc_dvecAt(PyObject * PYBINDGEN_UNUSED(dummy), PyObject *args, PyObject *kwargs, PyObject **return_exception)
{
    Pystd__vector__lt___double___gt__ *vec;
    int loc;
    const char *keywords[] = {"vec","loc", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, (char *) "O!i", (char **) keywords,  &Pystd__vector__lt___double___gt___Type , &vec, &loc)) 
    {
       {
            PyObject *exc_type, *traceback;
            PyErr_Fetch(&exc_type, return_exception, &traceback);
            Py_XDECREF(exc_type);
            Py_XDECREF(traceback);
        }
        return NULL;
    }
   std::vector<double> &lv = *((Pystd__vector__lt___double___gt__ *)vec)->obj;
   if (long(lv.size()) <= long(loc) )
   {
        PyErr_SetString(PyExc_TypeError, "Location out of range");
        return NULL;
   }

   return Py_BuildValue( "d", lv[loc]);
}

