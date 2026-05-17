from pybindgen import Module, FileCodeSink, param, retval, cppclass, typehandlers


import pybindgen.settings
import warnings

class ErrorHandler(pybindgen.settings.ErrorHandler):
    def handle_error(self, wrapper, exception, traceback_):
        warnings.warn("exception %r in wrapper %s" % (exception, wrapper))
        return True
pybindgen.settings.error_handler = ErrorHandler()


import sys

def module_init():
    root_module = Module('prc_impl', cpp_namespace='::')
    root_module.add_include('"prc/Ordering.h"')
    root_module.add_include('"prc/OrderObject.h"')
    root_module.add_include('"prc/VirtualOrderObject.h"')
    root_module.add_include('"prc/FlatStruct.h"')
    root_module.add_include('"prc/BoundaryObject.h"')
    root_module.add_include('"prc/FlatStruct.h"')
    root_module.add_include('"prc/prcPolicies.h"')
    root_module.add_include('"prc/runConfigs.h"')
    root_module.add_include('"prc/prcReturnStruct.h"')
    root_module.add_include('"prc/prcMetricValues.h"')
    root_module.add_include('"prc/prcCountsStruct.h"')
    root_module.add_include('"prc/pythonHelpers.h"')
    return root_module

def register_types(module):
    root_module = module.get_root()
    
    
    ## Register a nested module for the namespace PRC
    
    nested_module = module.add_cpp_namespace('PRC')
    register_types_PRC(nested_module)
    
    
    ## Register a nested module for the namespace std
    
    nested_module = module.add_cpp_namespace('std')
    register_types_std(nested_module)
    

def register_types_PRC(module):
    root_module = module.get_root()
    
    module.add_enum('GAUSSSIM_ADJ_MODE', ['GS_ADJ_THRESHOLD', 'GS_ADJ_ALL'])
    module.add_enum('prcMetricEnum', ['PinchRatio', 'RelRatio', 'CrossRatio', 'NCut'])
    module.add_enum('KNN_ADJ_MODE', ['KNN_EITHER_ADJ_ONE', 'KNN_BOTH_ADJ_ONE', 'KNN_BOTH_EITHER_ONE_ONEHALF', 'KNN_EITHER_ADJ_GAUSS'])
    module.add_enum('TagModeEnum', ['NO_TAGS', 'FRONT_TAGS', 'REAR_TAGS'])
    module.add_enum('FileStructureEnum', ['POINT_DATA', 'ADJACENCY_DATA'])
    module.add_enum('PointSimilarityEnum', ['UNDEFINED_ADJ_SIM', 'GAUSS_ADJ_SIM', 'KNN_ADJ_SIM', 'PRECALC_ADJ_SIM'])
    module.add_class('BoundaryObject')
    module.add_class('FlatStruct')
    module.add_enum('FlatType', ['LocalMin', 'LocalMax'], outer_class=root_module['PRC::FlatStruct'])
    module.add_class('Ordering', template_parameters=['PRC::OrderObject'])
    module.add_class('Ordering', template_parameters=['PRC::VirtualOrderObject'])
    module.add_class('VirtualOrderObject', parent=root_module['PRC::Ordering< PRC::VirtualOrderObject >'])
    module.add_class('adjDataConfigStruct')
    module.add_class('dataConfigStruct')
    module.add_class('gaussAdjPolicyStruct')
    module.add_class('knnAdjPolicyStruct')
    module.add_class('pointDataConfigStruct')
    module.add_class('prcCountsStruct')
    module.add_class('prcMetricValues')
    module.add_class('prcPolicyStruct')
    module.add_class('prcReturnStruct')
    module.add_class('runConfigStruct')
    module.add_class('tiloPolicyStruct')
    module.add_class('OrderObject', parent=root_module['PRC::Ordering< PRC::OrderObject >'])
    module.add_container('std::vector< PRC::FlatStruct >', 'PRC::FlatStruct', container_type='vector')
    module.add_container('PRC::FlatStructVec', 'PRC::FlatStruct', container_type='vector')
    module.add_container('std::vector< double >', 'double', container_type='vector')
    module.add_container('std::vector< PRC::prcMetricValues >', 'PRC::prcMetricValues', container_type='vector')
    module.add_container('std::vector< int >', 'int', container_type='vector')
    module.add_container('std::map< int, int >', ('int', 'int'), container_type='map')
    typehandlers.add_type_alias('std::vector< PRC::FlatStruct, std::allocator< PRC::FlatStruct > >', 'PRC::FlatStructVec')
    typehandlers.add_type_alias('std::vector< PRC::FlatStruct, std::allocator< PRC::FlatStruct > >*', 'PRC::FlatStructVec*')
    typehandlers.add_type_alias('std::vector< PRC::FlatStruct, std::allocator< PRC::FlatStruct > >&', 'PRC::FlatStructVec&')

def register_types_std(module):
    root_module = module.get_root()
    
    
    ## Register a nested module for the namespace rel_ops
    
    nested_module = module.add_cpp_namespace('rel_ops')
    register_types_std_rel_ops(nested_module)
    

def register_types_std_rel_ops(module):
    root_module = module.get_root()
    

def register_methods(root_module):
    register_PRCBoundaryObject_methods(root_module, root_module['PRC::BoundaryObject'])
    register_PRCFlatStruct_methods(root_module, root_module['PRC::FlatStruct'])
    register_PRCOrdering__PRCOrderObject_methods(root_module, root_module['PRC::Ordering< PRC::OrderObject >'])
    register_PRCOrdering__PRCVirtualOrderObject_methods(root_module, root_module['PRC::Ordering< PRC::VirtualOrderObject >'])
    register_PRCVirtualOrderObject_methods(root_module, root_module['PRC::VirtualOrderObject'])
    register_PRCAdjDataConfigStruct_methods(root_module, root_module['PRC::adjDataConfigStruct'])
    register_PRCDataConfigStruct_methods(root_module, root_module['PRC::dataConfigStruct'])
    register_PRCGaussAdjPolicyStruct_methods(root_module, root_module['PRC::gaussAdjPolicyStruct'])
    register_PRCKnnAdjPolicyStruct_methods(root_module, root_module['PRC::knnAdjPolicyStruct'])
    register_PRCPointDataConfigStruct_methods(root_module, root_module['PRC::pointDataConfigStruct'])
    register_PRCPrcCountsStruct_methods(root_module, root_module['PRC::prcCountsStruct'])
    register_PRCPrcMetricValues_methods(root_module, root_module['PRC::prcMetricValues'])
    register_PRCPrcPolicyStruct_methods(root_module, root_module['PRC::prcPolicyStruct'])
    register_PRCPrcReturnStruct_methods(root_module, root_module['PRC::prcReturnStruct'])
    register_PRCRunConfigStruct_methods(root_module, root_module['PRC::runConfigStruct'])
    register_PRCTiloPolicyStruct_methods(root_module, root_module['PRC::tiloPolicyStruct'])
    register_PRCOrderObject_methods(root_module, root_module['PRC::OrderObject'])
    return

def register_PRCBoundaryObject_methods(root_module, cls):
    cls.add_constructor([param('PRC::BoundaryObject const &', 'arg0')])
    cls.add_constructor([])
    cls.add_constructor([param('int', 'size'), param('double', 'inFixed')])
    cls.add_method('Print', 
                   'std::string', 
                   [], 
                   is_const=True)
    cls.add_method('Print', 
                   'void', 
                   [param('std::ostream &', 'out')], 
                   is_const=True)
    cls.add_method('at', 
                   'double &', 
                   [param('int', 'i')])
    cls.add_method('at', 
                   'double const &', 
                   [param('int', 'i')], 
                   is_const=True)
    cls.add_method('data', 
                   'double const *', 
                   [], 
                   is_const=True)
    cls.add_method('data', 
                   'double *', 
                   [])
    cls.add_method('dataAsVector', 
                   'std::vector< double > const &', 
                   [], 
                   is_const=True)
    cls.add_method('findLocalMinAndMax', 
                   'void', 
                   [param('PRC::FlatStructVec &', 'm')], 
                   is_const=True)
    cls.add_method('py_at', 
                   'double', 
                   [param('int', 'i')])
    cls.add_method('resize', 
                   'void', 
                   [param('int', 'size'), param('double', 'inFixed')])
    cls.add_method('size', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('operator()', 
                   'double &', 
                   [param('int', 'i')], 
                   custom_name='__call__')
    cls.add_method('operator()', 
                   'double const &', 
                   [param('int', 'i')], 
                   is_const=True, custom_name='__call__')
    cls.add_instance_attribute('b', 'std::vector< double >', is_const=False)
    cls.add_instance_attribute('fixedBoundary', 'double', is_const=False)
    return

def register_PRCFlatStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::FlatStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_constructor([param('int', 'begin'), param('int', 'end'), param('PRC::FlatStruct::FlatType', 't')])
    cls.add_method('Print', 
                   'std::string', 
                   [], 
                   is_const=True)
    cls.add_method('Print', 
                   'void', 
                   [param('std::ostream &', 'out')], 
                   is_const=True)
    cls.add_instance_attribute('start', 'int', is_const=False)
    cls.add_instance_attribute('stop', 'int', is_const=False)
    cls.add_instance_attribute('type', 'PRC::FlatStruct::FlatType', is_const=False)
    return

def register_PRCOrdering__PRCOrderObject_methods(root_module, cls):
    cls.add_constructor([])
    cls.add_constructor([param('PRC::Ordering< PRC::OrderObject > const &', 'arg0')])
    cls.add_method('Print', 
                   'std::string', 
                   [], 
                   is_const=True)
    cls.add_method('PrintInverse', 
                   'std::string', 
                   [], 
                   is_const=True)
    cls.add_method('at', 
                   'int const &', 
                   [param('int', 'i')], 
                   is_const=True)
    cls.add_method('baseStart', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('boundary', 
                   'PRC::BoundaryObject &', 
                   [])
    cls.add_method('boundary', 
                   'PRC::BoundaryObject const &', 
                   [], 
                   is_const=True)
    cls.add_method('derived', 
                   'PRC::OrderObject &', 
                   [])
    cls.add_method('derived', 
                   'PRC::OrderObject const &', 
                   [], 
                   is_const=True)
    cls.add_method('haveCache', 
                   'bool', 
                   [], 
                   is_const=True)
    cls.add_method('invAt', 
                   'int', 
                   [param('int', 'i')], 
                   is_const=True)
    cls.add_method('marks', 
                   'std::vector< PRC::FlatStruct > &', 
                   [])
    cls.add_method('marks', 
                   'std::vector< PRC::FlatStruct > const &', 
                   [], 
                   is_const=True)
    cls.add_method('setAt', 
                   'void', 
                   [param('int', 'index'), param('int', 'value')])
    cls.add_method('size', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('updateInverseOrder', 
                   'void', 
                   [])
    cls.add_method('operator()', 
                   'int const &', 
                   [param('int', 'i')], 
                   is_const=True, custom_name='__call__')
    return

def register_PRCOrdering__PRCVirtualOrderObject_methods(root_module, cls):
    cls.add_constructor([])
    cls.add_constructor([param('PRC::Ordering< PRC::VirtualOrderObject > const &', 'arg0')])
    cls.add_method('Print', 
                   'std::string', 
                   [], 
                   is_const=True)
    cls.add_method('PrintInverse', 
                   'std::string', 
                   [], 
                   is_const=True)
    cls.add_method('at', 
                   'int const &', 
                   [param('int', 'i')], 
                   is_const=True)
    cls.add_method('baseStart', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('boundary', 
                   'PRC::BoundaryObject &', 
                   [])
    cls.add_method('boundary', 
                   'PRC::BoundaryObject const &', 
                   [], 
                   is_const=True)
    cls.add_method('derived', 
                   'PRC::VirtualOrderObject &', 
                   [])
    cls.add_method('derived', 
                   'PRC::VirtualOrderObject const &', 
                   [], 
                   is_const=True)
    cls.add_method('haveCache', 
                   'bool', 
                   [], 
                   is_const=True)
    cls.add_method('invAt', 
                   'int', 
                   [param('int', 'i')], 
                   is_const=True)
    cls.add_method('marks', 
                   'std::vector< PRC::FlatStruct > &', 
                   [])
    cls.add_method('marks', 
                   'std::vector< PRC::FlatStruct > const &', 
                   [], 
                   is_const=True)
    cls.add_method('setAt', 
                   'void', 
                   [param('int', 'index'), param('int', 'value')])
    cls.add_method('size', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('updateInverseOrder', 
                   'void', 
                   [])
    cls.add_method('operator()', 
                   'int const &', 
                   [param('int', 'i')], 
                   is_const=True, custom_name='__call__')
    return

def register_PRCVirtualOrderObject_methods(root_module, cls):
    cls.add_constructor([])
    cls.add_constructor([param('PRC::VirtualOrderObject const &', 'voo')])
    cls.add_constructor([param('PRC::VirtualOrderObject *', 'voo')])
    cls.add_constructor([param('PRC::OrderObject *', 'p')])
    cls.add_constructor([param('PRC::OrderObject *', 'p'), param('int', 'start'), param('int', 'size')])
    cls.add_method('Data', 
                   'int const *', 
                   [], 
                   is_const=True)
    cls.add_method('Data', 
                   'int *', 
                   [])
    cls.add_method('Print', 
                   'std::string', 
                   [], 
                   is_const=True)
    cls.add_method('PrintInverse', 
                   'std::string', 
                   [], 
                   is_const=True)
    cls.add_method('at', 
                   'int const &', 
                   [param('int', 'index')], 
                   is_const=True)
    cls.add_method('baseStart', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('boundary', 
                   'PRC::BoundaryObject &', 
                   [])
    cls.add_method('boundary', 
                   'PRC::BoundaryObject const &', 
                   [], 
                   is_const=True)
    cls.add_method('haveCache', 
                   'bool', 
                   [], 
                   is_const=True)
    cls.add_method('invAt', 
                   'int', 
                   [param('int', 'id')], 
                   is_const=True)
    cls.add_method('marks', 
                   'PRC::FlatStructVec &', 
                   [])
    cls.add_method('marks', 
                   'PRC::FlatStructVec const &', 
                   [], 
                   is_const=True)
    cls.add_method('origsize', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('setAt', 
                   'void', 
                   [param('int', 'index'), param('int', 'value')])
    cls.add_method('size', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('split', 
                   'void', 
                   [param('int', 'loc'), param('PRC::VirtualOrderObject &', 'a'), param('PRC::VirtualOrderObject &', 'b'), param('bool', 'reverseB', default_value='false')], 
                   is_const=True)
    cls.add_method('start', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('updateInverseOrder', 
                   'void', 
                   [])
    cls.add_method('operator()', 
                   'int const &', 
                   [param('int', 'index')], 
                   is_const=True, custom_name='__call__')
    return

def register_PRCAdjDataConfigStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::adjDataConfigStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""')])
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""')])
    cls.add_method('checkCmdLineOption', 
                   'int', 
                   [param('int', 'i'), param('int', 'argc'), param('char const * *', 'argv')])
    cls.add_method('cmdLineUsage', 
                   'void', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""')])
    cls.add_instance_attribute('nodeOffset', 'int', is_const=False)
    return

def register_PRCDataConfigStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::dataConfigStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""')])
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""')])
    cls.add_method('checkCmdLineOption', 
                   'int', 
                   [param('int', 'i'), param('int', 'argc'), param('char const * *', 'argv')])
    cls.add_method('cmdLineUsage', 
                   'void', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""')])
    cls.add_instance_attribute('adjDataConfig', 'PRC::adjDataConfigStruct', is_const=False)
    cls.add_instance_attribute('commaSeparated', 'bool', is_const=False)
    cls.add_instance_attribute('commentDelimiter', 'std::string', is_const=False)
    cls.add_instance_attribute('fileType', 'PRC::FileStructureEnum', is_const=False)
    cls.add_instance_attribute('inputFileName', 'std::string', is_const=False)
    cls.add_instance_attribute('pointDataConfig', 'PRC::pointDataConfigStruct', is_const=False)
    cls.add_instance_attribute('useSparseMatrix', 'bool', is_const=False)
    return

def register_PRCGaussAdjPolicyStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::gaussAdjPolicyStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_method('ModeFromInt', 
                   'PRC::GAUSSSIM_ADJ_MODE', 
                   [param('int', 'm')], 
                   is_static=True)
    cls.add_method('ModeName', 
                   'char const *', 
                   [param('PRC::GAUSSSIM_ADJ_MODE', 'm')], 
                   is_static=True)
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('checkCmdLineOption', 
                   'int', 
                   [param('int', 'i'), param('int', 'argc'), param('char const * *', 'argv')])
    cls.add_method('cmdLineUsage', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('cmdLineUsage', 
                   'void', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_instance_attribute('mode', 'PRC::GAUSSSIM_ADJ_MODE', is_const=False)
    cls.add_instance_attribute('sigma', 'double', is_const=False)
    cls.add_instance_attribute('threshold', 'double', is_const=False)
    return

def register_PRCKnnAdjPolicyStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::knnAdjPolicyStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_method('ModeFromInt', 
                   'PRC::KNN_ADJ_MODE', 
                   [param('int', 'm')], 
                   is_static=True)
    cls.add_method('ModeName', 
                   'char const *', 
                   [param('PRC::KNN_ADJ_MODE', 'm')], 
                   is_static=True)
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('checkCmdLineOption', 
                   'int', 
                   [param('int', 'i'), param('int', 'argc'), param('char const * *', 'argv')])
    cls.add_method('cmdLineUsage', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('cmdLineUsage', 
                   'void', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_instance_attribute('k', 'int', is_const=False)
    cls.add_instance_attribute('mode', 'PRC::KNN_ADJ_MODE', is_const=False)
    cls.add_instance_attribute('sigma', 'double', is_const=False)
    return

def register_PRCPointDataConfigStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::pointDataConfigStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""')])
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""')])
    cls.add_method('checkCmdLineOption', 
                   'int', 
                   [param('int', 'i'), param('int', 'argc'), param('char const * *', 'argv')])
    cls.add_method('cmdLineUsage', 
                   'void', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""')])
    cls.add_instance_attribute('simType', 'PRC::PointSimilarityEnum', is_const=False)
    cls.add_instance_attribute('tagLoc', 'PRC::TagModeEnum', is_const=False)
    return

def register_PRCPrcCountsStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::prcCountsStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_constructor([param('long int', 'shifts'), param('long int', 'inversions'), param('long int', 'iterations')])
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_instance_attribute('numberOfInversions', 'long int', is_const=False)
    cls.add_instance_attribute('numberOfIterations', 'long int', is_const=False)
    cls.add_instance_attribute('numberOfShifts', 'long int', is_const=False)
    return

def register_PRCPrcMetricValues_methods(root_module, cls):
    cls.add_constructor([param('PRC::prcMetricValues const &', 'arg0')])
    cls.add_constructor([])
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_instance_attribute('crossRatio', 'double', is_const=False)
    cls.add_instance_attribute('dA', 'double', is_const=False)
    cls.add_instance_attribute('dB', 'double', is_const=False)
    cls.add_instance_attribute('extA', 'double', is_const=False)
    cls.add_instance_attribute('extB', 'double', is_const=False)
    cls.add_instance_attribute('intA', 'double', is_const=False)
    cls.add_instance_attribute('intB', 'double', is_const=False)
    cls.add_instance_attribute('loc', 'int', is_const=False)
    cls.add_instance_attribute('mincut', 'double', is_const=False)
    cls.add_instance_attribute('minmaxcutA', 'double', is_const=False)
    cls.add_instance_attribute('minmaxcutB', 'double', is_const=False)
    cls.add_instance_attribute('ncut', 'double', is_const=False)
    cls.add_instance_attribute('pinchRatio', 'double', is_const=False)
    cls.add_instance_attribute('relA', 'double', is_const=False)
    cls.add_instance_attribute('relB', 'double', is_const=False)
    cls.add_instance_attribute('relRatio', 'double', is_const=False)
    return

def register_PRCPrcPolicyStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::prcPolicyStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('checkCmdLineOption', 
                   'int', 
                   [param('int', 'i'), param('int', 'argc'), param('char const * *', 'argv')])
    cls.add_method('cmdLineUsage', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('cmdLineUsage', 
                   'void', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_instance_attribute('metric', 'PRC::prcMetricEnum', is_const=False)
    cls.add_instance_attribute('prcEvalAllMetrics', 'bool', is_const=False)
    cls.add_instance_attribute('prcRecurseTILO', 'bool', is_const=False)
    cls.add_instance_attribute('prcRefineTILO', 'bool', is_const=False)
    cls.add_instance_attribute('prcReturnMetrics', 'bool', is_const=False)
    cls.add_instance_attribute('prcReturnRecursiveOrder', 'bool', is_const=False)
    cls.add_instance_attribute('reverseOrderOnSplit', 'bool', is_const=False)
    cls.add_instance_attribute('tiloPolicy', 'PRC::tiloPolicyStruct', is_const=False)
    return

def register_PRCPrcReturnStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::prcReturnStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_constructor([param('PRC::prcCountsStruct', 'c'), param('double', 'awcq'), param('double', 'acq'), param('double', 'wgm'), param('double', 'gm'), param('std::vector< PRC::prcMetricValues > const &', 'mv')])
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('PrintVerbose', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('PrintVerbose', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_instance_attribute('averageClusterQuality', 'double', is_const=False)
    cls.add_instance_attribute('averageWeightedClusterQuality', 'double', is_const=False)
    cls.add_instance_attribute('counts', 'PRC::prcCountsStruct', is_const=False)
    cls.add_instance_attribute('geometricMean', 'double', is_const=False)
    cls.add_instance_attribute('mvalues', 'std::vector< PRC::prcMetricValues >', is_const=False)
    cls.add_instance_attribute('weightedGeometricMean', 'double', is_const=False)
    return

def register_PRCRunConfigStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::runConfigStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""')])
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""')])
    cls.add_method('checkCmdLineOption', 
                   'int', 
                   [param('int', 'i'), param('int', 'argc'), param('char const * *', 'argv')])
    cls.add_method('cmdLineUsage', 
                   'void', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""')])
    cls.add_instance_attribute('infoSuffix', 'std::string', is_const=False)
    cls.add_instance_attribute('initLabelsFile', 'std::string', is_const=False)
    cls.add_instance_attribute('initOrderFile', 'std::string', is_const=False)
    cls.add_instance_attribute('numberInitOrderings', 'int', is_const=False)
    cls.add_instance_attribute('numberOfPartitions', 'int', is_const=False)
    cls.add_instance_attribute('outputLabelSuffix', 'std::string', is_const=False)
    cls.add_instance_attribute('outputOrderSuffix', 'std::string', is_const=False)
    cls.add_instance_attribute('saveLabels', 'bool', is_const=False)
    cls.add_instance_attribute('saveMultipleRuns', 'bool', is_const=False)
    cls.add_instance_attribute('saveOrder', 'bool', is_const=False)
    cls.add_instance_attribute('seed', 'long int', is_const=False)
    cls.add_instance_attribute('seedSuffix', 'bool', is_const=False)
    cls.add_instance_attribute('useMultiLevelPRC', 'bool', is_const=False)
    cls.add_instance_attribute('useTransduction', 'bool', is_const=False)
    cls.add_instance_attribute('verboseLevel', 'int', is_const=False)
    return

def register_PRCTiloPolicyStruct_methods(root_module, cls):
    cls.add_constructor([param('PRC::tiloPolicyStruct const &', 'arg0')])
    cls.add_constructor([])
    cls.add_method('Print', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('Print', 
                   'std::ostream &', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('checkCmdLineOption', 
                   'int', 
                   [param('int', 'i'), param('int', 'argc'), param('char const * *', 'argv')])
    cls.add_method('cmdLineUsage', 
                   'std::string', 
                   [param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_method('cmdLineUsage', 
                   'void', 
                   [param('std::ostream &', 'out'), param('char const *', 'indent', default_value='""'), param('char const *', 'sep', default_value='"\\012"')], 
                   is_const=True)
    cls.add_instance_attribute('maxIterations', 'long int', is_const=False)
    cls.add_instance_attribute('tiloEpsilon', 'double', is_const=False)
    return

def register_PRCOrderObject_methods(root_module, cls):
    cls.add_constructor([])
    cls.add_constructor([param('int', 'size'), param('bool', 'prefixFlag', default_value='false')])
    cls.add_constructor([param('PRC::OrderObject const &', 'voo')])
    cls.add_constructor([param('std::vector< int > const &', 'origData'), param('bool', 'prefixFlag', default_value='false')])
    cls.add_method('Data', 
                   'int const *', 
                   [], 
                   is_const=True)
    cls.add_method('Data', 
                   'int *', 
                   [])
    cls.add_method('Print', 
                   'std::string', 
                   [], 
                   is_const=True)
    cls.add_method('Print', 
                   'void', 
                   [param('std::ostream &', 'out')], 
                   is_const=True)
    cls.add_method('PrintInverse', 
                   'std::string', 
                   [], 
                   is_const=True)
    cls.add_method('PrintInverse', 
                   'void', 
                   [param('std::ostream &', 'out')], 
                   is_const=True)
    cls.add_method('SetPrefixFlag', 
                   'void', 
                   [param('bool', 'flag')])
    cls.add_method('VData', 
                   'std::vector< int > const &', 
                   [], 
                   is_const=True)
    cls.add_method('at', 
                   'int const &', 
                   [param('int', 'i')], 
                   is_const=True)
    cls.add_method('baseStart', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('boundary', 
                   'PRC::BoundaryObject &', 
                   [])
    cls.add_method('boundary', 
                   'PRC::BoundaryObject const &', 
                   [], 
                   is_const=True)
    cls.add_method('copyTo', 
                   'void', 
                   [param('std::vector< int > &', 'dest')], 
                   is_const=True, template_parameters=['std::vector<int, std::allocator<int> >'])
    cls.add_method('getAt', 
                   'int', 
                   [param('int', 'i')])
    cls.add_method('haveCache', 
                   'bool', 
                   [], 
                   is_const=True)
    cls.add_method('invAt', 
                   'int', 
                   [param('int', 'i')], 
                   is_const=True)
    cls.add_method('marks', 
                   'PRC::FlatStructVec &', 
                   [])
    cls.add_method('marks', 
                   'PRC::FlatStructVec const &', 
                   [], 
                   is_const=True)
    cls.add_method('setAt', 
                   'void', 
                   [param('int', 'index'), param('int', 'value')])
    cls.add_method('setFrom', 
                   'void', 
                   [param('std::vector< int > const &', 'src')], 
                   template_parameters=['std::vector<int, std::allocator<int> >'])
    cls.add_method('size', 
                   'int', 
                   [], 
                   is_const=True)
    cls.add_method('split', 
                   'void', 
                   [param('int', 'loc'), param('PRC::OrderObject &', 'a'), param('PRC::OrderObject &', 'b'), param('bool', 'reverseB', default_value='false')], 
                   is_const=True)
    cls.add_method('updateInverseOrder', 
                   'void', 
                   [])
    cls.add_method('operator()', 
                   'int const &', 
                   [param('int', 'i')], 
                   is_const=True, custom_name='__call__')
    cls.add_instance_attribute('b', 'PRC::BoundaryObject', is_const=False)
    cls.add_instance_attribute('ivdata', 'std::map< int, int >', is_const=False)
    cls.add_instance_attribute('m', 'PRC::FlatStructVec', is_const=False)
    cls.add_instance_attribute('slopeCache', 'std::vector< double >', is_const=False)
    cls.add_instance_attribute('usePrefix', 'bool', is_const=False)
    cls.add_instance_attribute('validCache', 'bool', is_const=False)
    cls.add_instance_attribute('vdata', 'std::vector< int >', is_const=False)
    return

def register_functions(root_module):
    module = root_module
    register_functions_PRC(module.get_submodule('PRC'), root_module)
    register_functions_std(module.get_submodule('std'), root_module)
    return

def register_functions_PRC(module, root_module):
    module.add_function('EnumName', 
                        'char const *', 
                        [param('PRC::FileStructureEnum', 'v')])
    module.add_function('EnumName', 
                        'char const *', 
                        [param('PRC::PointSimilarityEnum', 'v')])
    module.add_function('EnumName', 
                        'char const *', 
                        [param('PRC::TagModeEnum', 'v')])
    module.add_function('FileStructureEnumFromInt', 
                        'PRC::FileStructureEnum', 
                        [param('int', 'v')])
    module.add_function('PointSimilarityFromInt', 
                        'PRC::PointSimilarityEnum', 
                        [param('int', 'v')])
    module.add_function('PrintMarks', 
                        'std::string', 
                        [param('PRC::FlatStructVec const &', 'm')])
    module.add_function('PrintMarks', 
                        'void', 
                        [param('std::ostream &', 'out'), param('PRC::FlatStructVec const &', 'm')])
    module.add_function('TagFromInt', 
                        'PRC::TagModeEnum', 
                        [param('int', 'v')])
    module.add_function('findLocalMinAndMax', 
                        'PRC::FlatStructVec', 
                        [param('PRC::BoundaryObject const &', 'b')])
    module.add_function('prcMetricEnumFromInt', 
                        'PRC::prcMetricEnum', 
                        [param('int', 'm')])
    module.add_function('prcMetricEnumName', 
                        'char const *', 
                        [param('PRC::prcMetricEnum', 'm')])
    return

def register_functions_std(module, root_module):
    register_functions_std_rel_ops(module.get_submodule('rel_ops'), root_module)
    return

def register_functions_std_rel_ops(module, root_module):
    return

def main():
    out = FileCodeSink(sys.stdout)
    root_module = module_init()
    register_types(root_module)
    register_methods(root_module)
    register_functions(root_module)
    root_module.generate(out)

if __name__ == '__main__':
    main()

