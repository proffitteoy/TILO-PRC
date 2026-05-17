from __future__ import print_function # so print in 2.7 behaves like print in 3.2
import prc

import numpy
import scipy
import scipy.sparse


A = numpy.array([[0,1,1,0,1,0],
                 [1,0,0,1,0,1],
                 [1,0,0,1,1,0],
                 [0,1,1,0,0,1],
                 [1,0,1,0,0,0],
                 [0,1,0,1,0,0]],dtype=float)

print("Testing pinchRatioClustering with dense numpy matrix A =\n{}".format(A))
curOrder = prc.OrderObject(6)   
print("curOrder = {}".format(curOrder.Print()))
curLabels = prc.ivec([0]*6)
print("curLabels = {}".format( [i for i in curLabels]))
curPolicy = prc.prcPolicyStruct()
print("curPolicy = \n{}".format( curPolicy.Print("     ") ))

# print("Testing dense numpy matrix wrapper")
# prc.prc_impl.test_dense_numpy_wrapper(A,curOrder)

print("Calling prc.pinchRatioClustering(A,curOrder,curLabels,2,curPolicy) ")
res = prc.pinchRatioClustering(A,curOrder,curLabels,2,curPolicy)

print("result =\n{}".format(res.Print("   ")))
print("After run, curOrder = {}".format(curOrder.Print()))
print("After run, curOrder, boundary = {}".format(curOrder.b.Print()))
print("After run, curOrder, min/max marks = {}".format(prc.PrintMarks(curOrder.m)))
print("After run, curLabels = {}".format( [i for i in curLabels]))

print("\n-------------------------------------------------------\n")

curOrder = prc.OrderObject(6)
curLabels = prc.ivec([0]*6)
curPolicy = prc.prcPolicyStruct()

Z = scipy.sparse.csc_matrix(A)
Z.sort_indices() 

print("Testing pinchRatioClustering with Sparse matrix Z  =\n{}".format(Z))
print("Initial curOrder = {}".format(curOrder.Print()))
print("curLabels = {}".format( [i for i in curLabels]))
print("curPolicy =\n{}".format( curPolicy.Print("     ") ))

# print("Testing sparse scipy matrix wrapper")
# prc.prc_impl.test_sp_csc_wrapper(6,Z.nnz,Z.data,Z.indices,Z.indptr,curOrder)

print("Calling prc.sparse_pinchRatioClustering(Z,curOrder,curLabels,2,curPolicy) ")
res = prc.sparse_pinchRatioClustering(Z,curOrder,curLabels,2,curPolicy)

print("result =\n{}".format(res.Print("     ")))
print("After run, curOrder = {}".format(curOrder.Print()))
print("After run, curOrder, boundary = {}".format(curOrder.b.Print()))
print("After run, curOrder, min/max marks = {}".format(prc.PrintMarks(curOrder.m)))
print("After run, curLabels = {}".format( [i for i in curLabels]))


print("\n-------------------------------------------------------\n")

print("Testing TILO example using dense adjacency matrix")

tmpV = numpy.arange(6)
numpy.random.shuffle(tmpV)
curOrder = prc.createOrder(tmpV)
print("order is a random shuffle: curOrder = {}".format(curOrder.Print()))
print("Note: initially the boundary is empty : curOrder, boundary = {}".format(curOrder.b.Print()))
print("Can calculate boundaries of an order by calling prc.calcBoundaries(A,curOrder,tPolicy) ")
prc.calcBoundaries(A,curOrder)
print("curOrder, boundary = {}".format(curOrder.b.Print()))
tPolicy = prc.tiloPolicyStruct()
print("using default tilo policy, tPolicy  =\n{}".format(tPolicy.Print("   ")))
print("Calling prc.TILO(A,curOrder,tPolicy) ")
res = prc.TILO(A,curOrder,tPolicy)
print("result =\n{}".format(res.Print("     ")))
print("After TILO run, curOrder = {}".format(curOrder.Print()))
print("After TILO run, curOrder, boundary = {}".format(curOrder.b.Print()))
print("After TILO run, curOrder, min/max marks = {}".format(prc.PrintMarks(curOrder.m)))


print("\n-------------------------------------------------------\n")

print("Testing TILO example using sparse adjacency matrix")

numpy.random.shuffle(tmpV)
curOrder = prc.createOrder(tmpV)
print("order is a random shuffle: curOrder = {}".format(curOrder.Print()))
tPolicy = prc.tiloPolicyStruct()
print("using default tilo policy, tPolicy  =\n{}".format(tPolicy.Print("   ")))
print("Calling prc.sparse_TILO(Z,curOrder,tPolicy) ")
res = prc.sparse_TILO(Z,curOrder,tPolicy)
print("result =\n{}".format(res.Print("     ")))
print("After TILO run, curOrder = {}".format(curOrder.Print()))
print("After TILO run, curOrder, boundary = {}".format(curOrder.b.Print()))
print("After TILO run, curOrder, min/max marks = {}".format(prc.PrintMarks(curOrder.m)))


print("\n-------------------------------------------------------\n")


import StringIO

loop4c4_s11 = StringIO.StringIO("""
0.0 1.0 1.0 1.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0
1.0 0.0 1.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
1.0 1.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
1.0 1.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
1.0 0.0 0.0 0.0 0.0 1.0 1.0 1.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
0.0 0.0 0.0 0.0 1.0 0.0 1.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
0.0 0.0 0.0 0.0 1.0 1.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
0.0 0.0 0.0 0.0 1.0 1.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 1.0 1.0 1.0 0.0 0.0 0.0
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 1.0 1.0 0.0 0.0 0.0 0.0
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 1.0 0.0 1.0 0.0 0.0 0.0 0.0
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 1.0 1.0 0.0 0.0 0.0 0.0 0.0
1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 1.0 1.0
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 1.0 1.0
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 1.0 0.0 1.0
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 1.0 1.0 1.0 0.0
""")

A = numpy.loadtxt(loop4c4_s11)

print("Testing returning metric values from pinchRatioClustering with dense numpy matrix A =\n{}".format(A))
tmpV = numpy.arange(16)
numpy.random.shuffle(tmpV)
curOrder = prc.createOrder(tmpV)
print("Using random initial order. curOrder = {}".format(curOrder.Print()))
curLabels = prc.ivec([0]*16)
curPolicy = prc.prcPolicyStruct()
print("Setting prcReturnMetrics to True in curPolicy")
print("Setting prcEvalAllMetrics to True in curPolicy")
curPolicy.prcReturnMetrics = True
curPolicy.prcEvalAllMetrics = True
print("curPolicy = \n{}".format( curPolicy.Print("     ") ))

print("Calling prc.pinchRatioClustering(A,curOrder,curLabels,4,curPolicy) ")
res = prc.pinchRatioClustering(A,curOrder,curLabels,4,curPolicy)

print("result =\n{}".format(res.Print("   ",",")))
print("After run, curOrder = {}".format(curOrder.Print()))
print("After run, curOrder, boundary = {}".format(curOrder.b.Print()))
print("After run, curOrder, min/max marks = {}".format(prc.PrintMarks(curOrder.m)))
print("After run, curLabels = {}".format( [i for i in curLabels]))
print("Pinch Ratio values in order of splits:")
for m in res.mvalues:
   print("    split loc = {} with pinch ratio {}".format(m.loc,m.pinchRatio))


print("\nExample of running value,loc,mvalues = prc.findSplitLocation(A,curOrder,prc.prcMetricEnum.PinchRatio(),False)")
v,loc,mvalues = prc.findSplitLocation(A,curOrder,prc.prcMetricEnum.PinchRatio(),False)
print("""
   split value, v = {}  
   split location, loc = {}
   metric values, mvalues = {}""".format(v,loc,mvalues.Print(" ",",") ))
print("note: if not evaluating all metrics then default values are max double values.")

print("\nExample of running value,loc,mvalues = prc.findSplitLocation(A,curOrder,prc.prcMetricEnum.NCut(),True)")
v,loc,mvalues = prc.findSplitLocation(A,curOrder,prc.prcMetricEnum.NCut(),True)
print("""
   split value, v = {}  
   split location, loc = {}
   metric values, mvalues = {}""".format(v,loc,mvalues.Print(" ",",") ))

