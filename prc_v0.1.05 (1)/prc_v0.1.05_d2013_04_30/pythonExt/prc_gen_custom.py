
import pybindgen
import pybindgen.settings

pybindgen.settings.deprecated_virtuals = False

from pybindgen.typehandlers import base as typehandlers
from pybindgen import ReturnValue, Parameter, Module, Function, FileCodeSink
from pybindgen import CppMethod, CppConstructor, CppClass, Enum
from pybindgen.function import CustomFunctionWrapper
from pybindgen.cppmethod import CustomCppMethodWrapper


def customize_module(module):
    pybindgen.settings.wrapper_registry = pybindgen.settings.StdMapWrapperRegistry
    module.add_include('<Python.h>')
    module.add_include('<numpy/arrayobject.h>')
    module.add_include('<prc/pinch.h>')
    module.add_include('<prc/internal/internal_pinch.h>')
    module.add_include('<prc/denseNumpyStorage.h>')
    module.add_include('<prc/sparseCSCNumpyStorage.h>')
    fcc = open("cc_prcPinch.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('pinchRatioClustering', 'prc_prc', wrapper_body)
    fcc = open("cc_prcTILO.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('TILO', 'prc_tilo', wrapper_body)

    fcc = open("cc_prcSPTILO.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('sp_TILO', 'prc_sp_tilo', wrapper_body)


    fcc = open("cc_prcRefineTILO.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('RefineTILO', 'prc_refine_tilo', wrapper_body)


    fcc = open("cc_prcSPRefineTILO.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('sp_RefineTILO', 'prc_sp_refine_tilo', wrapper_body)


    fcc = open("cc_calcBoundaries.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('calcBoundaries', 'prc_CalcBoundaries', wrapper_body)


    fcc = open("cc_sp_calcBoundaries.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('sp_calcBoundaries', 'prc_sp_CalcBoundaries', wrapper_body)


    fcc = open("cc_prcSPPinch.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('sp_pinchRatioClustering', 'prc_sp_prc', wrapper_body)
    fcc = open("cc_prcTestSparseCSC.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('test_sp_csc_wrapper', 'prc_test_sp_csc', wrapper_body)
    fcc = open("cc_prcTestDenseNumpy.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('test_dense_numpy_wrapper', 'prc_test_dense_numpy', wrapper_body)

    fcc = open("cc_prcIVecAt.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('ivecAt', 'prc_ivecAt', wrapper_body)


    fcc = open("cc_prcDVecAt.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('dvecAt', 'prc_dvecAt', wrapper_body)


    fcc = open("cc_prcIVecSet.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('ivecSet', 'prc_ivecSet', wrapper_body)


    fcc = open("cc_prcDVecSet.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('dvecSet', 'prc_dvecSet', wrapper_body)


    fcc = open("cc_findSplitLocations.cc","r")
    wrapper_body = fcc.read()
    fcc.close()
    module.add_custom_function_wrapper('findSplitLocation', 'prc_findSplitLocation', wrapper_body)



    # just a compilation test, this won't actually work in runtime
#    module.add_class(name="FILE", foreign_cpp_namespace="", import_from_module="__builtin__ named file")
#    module.add_enum("reg_errcode_t",   ["REG_NOERROR", "REG_NOMATCH"], import_from_module="__builtin__")

