# ~/src/prc/prc/pinchRatioClustering --initOrderFile testData/randOrder_150.txt --dataInput testData/iris_all.txt_simMatrix_PS_1  --fileType  3  --useSparseMatrix 1 --numpart 2 --verbose 11 --adjNodeOffset 0

echo "Iris dense rand F F F F"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 0 --numpart 3 --verbose 2  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 0 --policyReverseOrderOnSplit 0 --policyReturnRecursiveOrder  0 --policyPRCMetric  0 --policyRefineTILO 0  >& runlog_iris_randorder_denses.txt 

echo "Iris dense lin F F F F"
..//prc/pinchRatioClustering --initOrderFile ../../testData/linOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 0 --numpart 3 --verbose 2  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 0 --policyReverseOrderOnSplit 0 --policyReturnRecursiveOrder  0 --policyPRCMetric  0 --policyRefineTILO 0  >& runlog_iris_linorder_dense.txt  
# defaults to false :  --policyEvalAllMetrics 0 --policyReturnMetrics  0 


echo "Iris sparse rand F F F F"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 2  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 0 --policyReverseOrderOnSplit 0 --policyReturnRecursiveOrder  0 --policyPRCMetric  0 --policyRefineTILO 0  >& runlog_iris_randorder_sparseFFFF.txt 

echo "Iris sparse rand T F F F"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 2  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 1 --policyReverseOrderOnSplit 0 --policyReturnRecursiveOrder  0 --policyPRCMetric  0 --policyRefineTILO 0  >& runlog_iris_randorder_sparseTFFF.txt 


echo "Iris sparse rand T F T F"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 2  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 1 --policyReverseOrderOnSplit 0 --policyReturnRecursiveOrder  1 --policyPRCMetric  0 --policyRefineTILO 0  >& runlog_iris_randorder_sparseTFTF.txt 

echo "Iris sparse rand T F T T"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 2  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 1 --policyReverseOrderOnSplit 0 --policyReturnRecursiveOrder  1 --policyPRCMetric  0 --policyRefineTILO 1  >& runlog_iris_randorder_sparseTFTT.txt 

echo "Iris sparse rand T T T T"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 2  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 1 --policyReverseOrderOnSplit 1 --policyReturnRecursiveOrder  1 --policyPRCMetric  0 --policyRefineTILO 1  >& runlog_iris_randorder_sparseTTTT.txt 

echo "Iris sparse rand T T T T v 11"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 11  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 1 --policyReverseOrderOnSplit 1 --policyReturnRecursiveOrder  1 --policyPRCMetric  0 --policyRefineTILO 1  >& runlog_iris_randorder_sparseTTTTv11.txt 

echo "Iris sparse rand T T T T v 51"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 51  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 1 --policyReverseOrderOnSplit 1 --policyReturnRecursiveOrder  1 --policyPRCMetric  0 --policyRefineTILO 1  >& runlog_iris_randorder_sparseTTTTv51.txt 

echo "Iris sparse rand F F F T v 51"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 51  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 0 --policyReverseOrderOnSplit 0 --policyReturnRecursiveOrder  0 --policyPRCMetric  0 --policyRefineTILO 1  >& runlog_iris_randorder_sparseFFFTv51.txt 

echo "Iris sparse rand T F F T v 51"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 51  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 1 --policyReverseOrderOnSplit 0 --policyReturnRecursiveOrder  0 --policyPRCMetric  0 --policyRefineTILO 1  >& runlog_iris_randorder_sparseTFFTv51.txt 

echo "Iris sparse rand T T F T"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 2  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 1 --policyReverseOrderOnSplit 1 --policyReturnRecursiveOrder  0 --policyPRCMetric  0 --policyRefineTILO 1  >& runlog_iris_randorder_sparseTTFT.txt 


echo "Iris sparse rand T T F F"
../prc/pinchRatioClustering --initOrderFile ../../testData/randOrder_150 --dataInput ../../testData/iris_all.txt  --fileType 0  --useSparseMatrix 1 --numpart 3 --verbose 2  --saveOrder 0 --saveLabels  0 --useMultiLevelPRC 0 --tagLoc 1 --policyPRCRecurseTILO 1 --policyReverseOrderOnSplit 1 --policyReturnRecursiveOrder  0 --policyPRCMetric  0 --policyRefineTILO 0  >& runlog_iris_randorder_sparseTTFF.txt 


