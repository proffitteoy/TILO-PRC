import pybindgen
import sys
from pybindgen import FileCodeSink
from pybindgen.gccxmlparser import ModuleParser

import prc_gen_custom

ipaths = [".","..","/usr/include/python2.7"]
if (len(sys.argv)>1):
    ipaths.extend(eval(sys.argv[1]))

cfiles = [ "prc/Ordering.h",
          "prc/OrderObject.h",
          "prc/VirtualOrderObject.h",
          "prc/FlatStruct.h",
          "prc/BoundaryObject.h",
          "prc/FlatStruct.h",
          "prc/prcPolicies.h",
          "prc/runConfigs.h",
          "prc/prcReturnStruct.h",
          "prc/prcMetricValues.h",
          "prc/prcCountsStruct.h",
          "prc/pythonHelpers.h"
#           , "helper2.h"
#           ,"helper2.cc"
           ]
ifiles = [ '"'+i+'"' for i in cfiles ]
def my_module_gen():
    out = FileCodeSink(sys.stdout)
    pygen_file = open("prc_impl_auto.py", "wt")  
    #module_parser = ModuleParser('prc_impl', '::PRC')
    module_parser = ModuleParser('prc_impl', '::')
    module_parser.enable_anonymous_containers = True
    gccxml_options = dict(
        include_paths=ipaths,
        define_symbols=["PY_XML_GEN"],
        )
    module_parser.parse_init(cfiles, includes=ifiles,whitelist_paths=[".."], pygen_sink=FileCodeSink(pygen_file),
                             gccxml_options=gccxml_options)
#    module_parser.parse(cfiles,includes=ifiles,whitelist_paths=[".."],include_paths=[".","..","/home/drh/include/eigen3","/usr/include/python2.7"],pygen_sink=FileCodeSink(sys.stdout))
    module = module_parser.module
    module.add_exception('exception', foreign_cpp_namespace='std', message_rvalue='%(EXC)s.what()')
    module_parser.scan_types()
    module_parser.scan_methods()
    module_parser.scan_functions()
    module_parser.parse_finalize()
    pygen_file.close()
    prc_gen_custom.customize_module(module)
    module.generate(out)

if __name__ == '__main__':
    my_module_gen()


