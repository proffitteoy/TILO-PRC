import prc_impl
from prc_impl import RefineTILO
from prc_impl import TILO
from prc_impl import calcBoundaries
from prc_impl import pinchRatioClustering
from prc_impl.PRC import findLocalMinAndMax
from prc_impl.PRC import PrintMarks
from prc_impl import findSplitLocation
from prc_impl.PRC import OrderObject
from prc_impl.PRC import FlatStruct
from prc_impl.PRC import Std__vector__lt___int___gt__ as ivec
from prc_impl.PRC import PRC__FlatStructVec as FlatStructVec
from prc_impl.PRC import prcPolicyStruct
from prc_impl.PRC import tiloPolicyStruct
from prc_impl import ivecAt, ivecSet,dvecAt,dvecSet

# a python layer between the external interface of prc and the actual c++ implementation.
#

import numpy
import scipy
import scipy.sparse
#from scipy.sparse import isspmatrix_csc, isspmatrix_csr, isspmatrix, SparseEfficiencyWarning, csc_matrix

import logging
logger = logging.getLogger(__name__)

def sparse_pinchRatioClustering(A,order,labels,k,policy):
   if not scipy.sparse.isspmatrix_csc(A):
      A = scipy.sparse.csc_matrix(A)
      logger.warning('sparse_pinchRatioClusterng requires CSC matrix format, converting to format, inefficient.')
   A.sort_indices()
   A = A.asfptype()  #upcast to a floating point format
   M, N = A.shape
   if (M != N):
      raise ValueError("Adjacency matrix must be square")
   return prc_impl.sp_pinchRatioClustering(N, A.nnz, A.data, A.indices, A.indptr,order,labels,k,policy)

def sparse_TILO(A,order,policy=tiloPolicyStruct()):
   if not scipy.sparse.isspmatrix_csc(A):
      A = scipy.sparse.csc_matrix(A)
      logger.warning('sparse_TILO requires CSC matrix format, converting to format, inefficient.')
   A.sort_indices()
   A = A.asfptype()  #upcast to a floating point format
   M, N = A.shape
   if (M != N):
      raise ValueError("Adjacency matrix must be square")
   return prc_impl.sp_TILO(N, A.nnz, A.data, A.indices, A.indptr,order,policy)


def sparse_calcBoundaries(A,order):
   if not scipy.sparse.isspmatrix_csc(A):
      A = scipy.sparse.csc_matrix(A)
      logger.warning('sparse_calcBoundaries requires CSC matrix format, converting to format, inefficient.')
   A.sort_indices()
   A = A.asfptype()  #upcast to a floating point format
   M, N = A.shape
   if (M != N):
      raise ValueError("Adjacency matrix must be square")
   return prc_impl.sp_calcBoundaries(N, A.nnz, A.data, A.indices, A.indptr,order)

def createOrder(values):
   size = len(values)
   try:
      v = ivec(values)  # values can be a list of integers or a std::vector of integers
   except TypeError:
      v = ivec(values.tolist())  # values can be a numpy array of integers
   order = OrderObject(size)
   order.setFrom__lt__std__vector__lt__int__std__allocator__lt__int__gt_____gt____gt__(v)
   return order

def setOrder(order,values):
   logger.debug("setting order with values = {}".format(values))
   try:
      v = ivec(values)  # values can be a list of integers or a std::vector of integers
   except TypeError:
      v = ivec(values.tolist())  # values can be a numpy array of integers
   order.setFrom__lt__std__vector__lt__int__std__allocator__lt__int__gt_____gt____gt__(v)
   logger.debug("finished setting order")



class prcMetricEnum:
   """wrapper to organize the prcMetricEnum values.
      Values are accessed through static class functions
   """
   @staticmethod
   def CrossRatio():
      return prc_impl.PRC.CrossRatio

   @staticmethod
   def RelRatio():
      return prc_impl.PRC.RelRatio

   @staticmethod
   def PinchRatio():
      return prc_impl.PRC.PinchRatio

   @staticmethod
   def NCut():
      return prc_impl.PRC.NCut

class KNN_ADJ_MODE:
   """wrapper to organize enum values.
      Values are accessed through static class functions
   """
   @staticmethod
   def KNN_EITHER_ADJ_ONE():
      return prc_impl.PRC.KNN_EITHER_ADJ_ONE

   @staticmethod
   def KNN_BOTH_ADJ_ONE():
      return prc_impl.PRC.KNN_BOTH_ADJ_ONE

   @staticmethod
   def KNN_BOTH_EITHER_ONE_ONEHALF():
      return prc_impl.PRC.KNN_BOTH_EITHER_ONE_ONEHALF

   @staticmethod
   def KNN_EITHER_ADJ_GAUSS():
      return prc_impl.PRC.KNN_EITHER_ADJ_GAUSS


class GAUSSSIM_ADJ_MODE:
   """wrapper to organize enum values.
      Values are accessed through static class functions
   """
   @staticmethod
   def GS_ADJ_THRESHOLD():
      return prc_impl.PRC.GS_ADJ_THRESHOLD

   @staticmethod
   def GS_ADJ_ALL():
      return prc_impl.PRC.GS_ADJ_ALL



class TagModeEnum:
   """wrapper to organize enum values.
      Values are accessed through static class functions
   """
   @staticmethod
   def NO_TAGS():
      return prc_impl.PRC.NO_TAGS

   @staticmethod
   def FRONT_TAGS():
      return prc_impl.PRC.FRONT_TAGS

   @staticmethod
   def REAR_TAGS():
      return prc_impl.PRC.REAR_TAGS



class FileStructureEnum:
   """wrapper to organize enum values.
      Values are accessed through static class functions
   """
   @staticmethod
   def POINT_DATA():
      return prc_impl.PRC.POINT_DATA

   @staticmethod
   def ADJACENCY_DATA():
      return prc_impl.PRC.ADJACENCY_DATA



class PointSimilarityEnum:
   """wrapper to organize enum values.
      Values are accessed through static class functions
   """
   @staticmethod
   def UNDEFINED_ADJ_SIM():
      return prc_impl.PRC.UNDEFINED_ADJ_SIM

   @staticmethod
   def GAUSS_ADJ_SIM():
      return prc_impl.PRC.GAUSS_ADJ_SIM

   @staticmethod
   def KNN_ADJ_SIM():
      return prc_impl.PRC.KNN_ADJ_SIM

   @staticmethod
   def PRECALC_ADJ_SIM():
      return prc_impl.PRC.PRECALC_ADJ_SIM



