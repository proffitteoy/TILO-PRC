============================================================================
Pinch Ratio Clustering from a Topologically Intrinsic Lexicographic Ordering
============================================================================

If you use the software in a scientific publication, please acknowledge with a citation to
**Pinch Ratio Clustering from a Topologically Intrinsic Lexicographic Ordering**,
*Proceedings of the SIAM International Conference on Data Mining (ICDM 2013)*, May 2-4, 2013.
Available at `prc_sdm13.pdf <http://www.cs.okstate.edu/~doug/publications/prc_sdm13.pdf>`_.

The source code is available using GNU General Public License version 3, see 
`http://www.gnu.org/licenses/ <http://www.gnu.org/licenses/>`_. If you
need to use the code under a different license, contact the author.


Building PRC code
=================

Code dependencies for prc include cmake for building, eigen for matrices, and a
reasonably new c++ compilier. The python binding require numpy and scipy. 

Build outside of the source code directories.  For example,
with source code in ``~/src/prc``, create a new directory
for the build at ~/build/prc.  cd into ``~/build/prc``.  Then run

``cmake ~/src/prc``

which will create the make files in linux.  Then use make to build. 

``make``

If Eigen is not in your default path, say you installed it in your home directory then
also pass that prefix to cmake:

``cmake . -DCMAKE_INSTALL_PREFIX=${HOME}  ${HOME}/src/prc``

and the include directories in the prefix path will also be searched.  Or
pass in the actual directory location.  Example on MS windows.

``cmake . -DCMAKE_INCLUDE_PATH=C:\Users\Doug\Documents\Working\eigen  ..\prc``

To create visual studio 11 win64 project files, add cmake option
``-G "Visual Studio 11 Win64"`` 
or for nmake files:
``-G "NMake Makefiles"``.


| Other options
|     ``-DCMAKE_BUILD_TYPE=Debug``
|     ``-DCMAKE_BUILD_TYPE=Release``
|     ``-DVERBOSE_PINCH=level``   : where level is integer corresponding to amount of output
|     ``-DPINCH_VERIFY_LEX=1``   : verifies that the width is reduced each iteration of TILO
|     ``-DHAVE_BENCH=path``      : times execution using eigen's benchmark timer, typically in eigen/bench
|     ``-Wdev``  or ``-Wno-dev``  : enable/disable developer warnings


Build with
``make VERBOSE=1``
for verbose compiler output


Building Python and prcVis Code
-------------------------------
see description in the individual directories.  Eventual build
system will be migrated to cmake.  But for now, python and qmake
are being used.

Cross compiling to MS Windows using mingw
-----------------------------------------

Create toolchain file and store in ``~/cmake/toolchain-minw32.cmake``
where the toolchain-minw32.cmake would contains (on debian wheezy)::

        # the name of the target operating system
        SET(CMAKE_SYSTEM_NAME Windows)
        # which compilers to use for C and C++
        SET(CMAKE_C_COMPILER i586-mingw32msvc-gcc)
        SET(CMAKE_CXX_COMPILER i586-mingw32msvc-g++)
        SET(CMAKE_RC_COMPILER i586-mingw32msvc-windres)
        # here is the target environment located
        SET(CMAKE_FIND_ROOT_PATH  /usr/i586-mingw32msvc /home/drh/mingw-32 )
        # adjust the default behaviour of the FIND_XXX() commands:
        # search headers and libraries in the target environment, search 
        # programs in the host environment
        SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
        SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
        SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

and  ``~/cmake/toolchain-minw64.cmake`` where the 
toolchain-minw64.cmake would contains (on debian wheezy)::

        # the name of the target operating system
        SET(CMAKE_SYSTEM_NAME Windows)
        # which compilers to use for C and C++
        SET(CMAKE_C_COMPILER amd64-mingw32msvc-gcc)
        SET(CMAKE_CXX_COMPILER amd64-mingw32msvc-g++)
        SET(CMAKE_RC_COMPILER amd64-mingw32msvc-windres)
        # here is the target environment located
        SET(CMAKE_FIND_ROOT_PATH  /usr/amd64-mingw32msvc /home/drh/mingw-64 )
        # adjust the default behaviour of the FIND_XXX() commands:
        # search headers and libraries in the target environment, search 
        # programs in the host environment
        SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
        SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
        SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)


| then when running cmake add:
| ``-DCMAKE_TOOLCHAIN_FILE=~/cmake/toolchain-minw32.cmake``
| or
| ``-DCMAKE_TOOLCHAIN_FILE=~/cmake/toolchain-minw64.cmake``



Commandline programs
====================

pinchRatioClustering
--------------------

The main driver program that reads a data file and attempts to determine 
clusters.  The executable is found in the prc directory of the build location.

usage: pinchRatioClustering [long options]  [filename [numberOfPartitions]]

will read data file ``filename`` and attempt to find ``numberOfPartitions`` clusters.
Possible long options include

      --dataInput string         Data file name.  The data file name be point data or and adjacency graph.
                                 May also be passed as a non-option.  That is, the first command line 
                                 parameter without the ``--`` is assumed to be the data file name.
                                 The structure of the data file is specified with the ``fileType`` option.
      --fileType integer         Specifies the data file type. 0 mean a point data file. 1 mean an adjacency matrix file.
                                 Point data files expect one data point per line.  The adjacency matrix file expects
                                 a sparse matrix format.
      --pointSimilarity integer  Specifies the similarity measure type to use for point data files.

                                     * 1 -> Gaussian similarity and  
                                     * 2 -> K nearest neighbor similarity.

      --seed long                Set the seed of the random number generator. Use 0 to set from current time.
      --numpart integer     Number of partitions to find. Must be >= 2.  May also be pass
                            as an option after the filename.   The program will find at most this
                            number of clusters, but it may find less.
      --verbose integer     Higher values generate more output. 
      --saveLabels boolean  Flag to control if the partition labels are saved to file.  
                            Labels are in the same order as the data file.  The label file name is 
                            the data filename + outputLabelSuffix + numParts + infoSuffux [+ seed].
      --saveOrder boolean   Flag to control if the TILO order and boundary are saved to file.  The order file name is 
                            the data filename + outputOrderSuffix + numParts + infoSuffux [+ seed].
      --seedSuffixFlag boolean    Flag to control if the seed value is added to output file names. 
      --outputLabelSuffix string  Text to add to saved label file name.  Default is ``"_part_"`` 
      --outputOrderSuffix string  Text to add to saved order file name.  Default is ``"_tilo_"``
      --infoSuffix string         Extra text to attached before seed in output file names.  Default is empty string.
      --initOrderFile string      Name of file containing an initial linear order to use instead of random order.
                                  Expects zero based indexing with whitespace separated integers.  If this option
                                  or the ``initLabelsFile`` option is not given then TILO will start with a random
                                  shuffle of the data point order.  
      --initLabelsFile string     Name of file containing an initial labels to use instead of random order. 
                                  Expects the labels to be in the same format as the saveLabels file.  That is,
                                  one label per line in the same order as the datafile.  An initial order
                                  is created by placing placing points with the same label adjacent to each other.
                                  Can be used to start TILO with an ordering generated by another algorithm.  
                                  If this option or the ``initOrderFile`` option is not given then 
                                  TILO will start with a random shuffle of the data point order.  
      --numInitOrderings integer  Number of times to run PRC with random initial orders 
                                  and return the one with the best total width.
      --saveMultipleRuns boolean  Save partition labels of each PRC run in addition to the best run. The number of
                                  multiple runs is set with the ``numInitOrderings`` option.  The tags ``"_multirun_labels"``
                                  and ``"_multirun_info"`` are added to the label and order files names.
      --useSparseMatrix boolean   Flag to control if PRC should store the adjacency matrix in a sparse matrix. Default is true.  
      --commaSeparated boolean    Flag to indicate if the data file is comma delimited.  Default is false.  
      --adjNodeOffset integer     Node index offset in an adjacency matrix data file. Default is 1.
                                  Needed when data file starts with one based instead of zero based indexing.
                                  Many of the example adjacency graphs on the web use one based indexing.
      --tiloMaxIteration  long    Limit on the maximum number of iterations that TILO will run.  Default is 10,000,000.
                                  Typically never reached.
      --tiloEpsilon double        Floating point precision value. Used when comparing the value of a shift to zero.  That
                                  is, the shift value must be > tiloEpsilon instead of > zero.  Also used to generate
                                  a combination of relative and absolute error of a value *v* by using (1+tiloEpsilon) \* *v*.
      --policyPRCRecurseTILO boolean  Flag to control if TILO is reran on a partition after is is moved to the front of
                                      the linear order.  This controls whether lines 13 and 14 of the PRC algorithm are
                                      used.  Default is false.
      --policyReverseOrderOnSplit boolean   Flag to control if the order of a partition is reversed when it is moved to the front.
                                            This option is only used if ``policyPRCRecurseTILO`` is true.  Default is false.
      --policyReturnRecursiveOrder boolean  Flag to control if the order created by the recursive use of TILO is returned
                                            or if the order from the initial TILO is returned.  
                                            This option is only used if ``policyPRCRecurseTILO`` is true.  Default is false.
      --policyPRCMetric integer   The metric to use to evaluate split locations.  Possible values are
                                       * 0 -> PinchRatio,
                                       * 1 -> RelRatio,
                                       * 2 -> CrossRatio, and 
                                       * 3 -> NCut.  
                                         
                                  Default is 0 for pinch ratio.  NCut refers to normalized cut and is well tested.
                                  The RelRatio and CrossRatio are experimental and are not well tested.
      --policyRefineTILO boolean  Flag to control if the boundary is complete reduced or if TILO stops as soon as the 
                                  local max and mins are set.  Typically used when conducting multiple runs on random initial
                                  orders and the best run is selected by the best total width.  Default is false.
      --policyEvalAllMetrics boolean  Flag to control the evaluation of cluster metrics.  Typically, only the metric
                                      that is being used to find split locations is evaluated.  If this option is true
                                      then all of the metrics are evaluated and returned.  The split locations are
                                      still determined by ``policyPRCMetric`` option.  Default is false.
      --policyReturnMetrics boolean  Flag to control is the metric values are all split locations are returned in an array.
                                     This extra information will be stored in the boundary and order output file.
                                     Default is false.
      --knnAdjMode int       The type of K nearest neighbor similarity to use for point data. 
                                   *  0 -> KNN_EITHER_ADJ_ONE, a value of 1.0 if either point is in the KNN of each other.
                                   *  1 -> KNN_BOTH_ADJ_ONE, a value of 1.0 only if both points are in the KNN of each other.
                                   *  2 -> KNN_BOTH_EITHER_ONE_ONEHALF, a value of 1.0 only of both points are in the KNN of each other, 
                                      a value of 1/2 if one point is in the KNN of the other point.
                                   *  3 -> KNN_EITHER_ADJ_GAUSS, if either point is in the KNN of the other then the value of Gaussian 
                                      similarity of the two points is used. 

                             The default is 3.
      --knnAdjK int          Number of nearest neighbors to use for KNN similarity mode. Use a value of -1 for the heuristic value of log(n)+1, 
                             where n is the number of data points.   Default is -1.
      --knnAdjSigma double   The value of sigma in knn's Gaussian similarity (i.e., mode 3 of ``knnAdjMode``).
                             Use -1 to estimate from average knn distance. Default is -1.
      --gausssimAdjMode int  The type of Gaussian similarity to use for point data.
                                    * 0 -> GS_ADJ_THRESHOLD, any Gaussian similarity values less than the threshold are set to zero.
                                    * 1 -> GS_ADJ_ALL,  the value of the similarity is the Gaussian similarity of the 
                                      two points.  With points **a** and **b**, then the similarity is 
                                      exp(-1.0 (a-b)^T (a-b) /( sigma^2)).

                             The default is 1.
      --gausssimAdjSigma double       The value of sigma in the Gaussian similarity.  Use -1 for heuristic 
                                      to calculate from average knn distance.  Default is -1.
      --gausssimAdjThreshold double   With ``gausssimAdjMode`` of 0, values less than this threshold are set to zero. Default is 1e-10.
      --commentDelimiter string       The charactoer representing the start of a comment in a data file.  Comments are ignored. Default is ``#`` 
      --tagLoc integer                Location of class labels in a data file.
                                          * 0 ->   no class tags,
                                          * 1 ->   front location.  Class label is first value in the line of data.
                                          * -1 ->  tail location.   Class label is last value in the line of data.

                                      Default is 0, no class labels.  Class labels are not used in clustering but 
                                      if available then purity and other performance measures of the clustering can be reported.
      --useTransduction boolean       Not implemented yet.  Value is ignored. 
      --useMultiLevelPRC boolean      Default false.  Multilevel is currently disabled as it is undergoing a rewrite.



genSimMatrix
------------
A helper program that creates adjacency matrices from point data and saves to an output file. 
The main use is to save the adjacency matrix that pinchRatioClustering  would create
for use in another algorithm.  The executable is found in the prc directory of the build location.

usage: prc/genSimMatrix [long options]  [filename outputFileName]


The options are the same as pinchRatioClustering, but most of them are ignored 
as the clustering algorithm is not conducted.

