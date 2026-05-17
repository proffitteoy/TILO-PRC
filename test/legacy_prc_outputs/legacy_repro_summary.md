# Legacy PRC Reproduction Attempt

## 结论

- 这次不能在当前工作区里用提供的旧版源码完整复现论文图。
- 旧版 `pythonExt` 自带说明已经明确写明“Currently, the extension does not build with python3.”
- 旧版 C++ CLI 的实际构建在 `Eigen/Core` 头文件缺失处失败，见 `legacy_cmake_build.log`。

## 这次实际做过的事

- 在 `F:\prc_v1_d2026_04_24\test\legacy_prc_build` 对 `prc_v0.1.05_d2013_04_30` 做了 out-of-source CMake 配置。
- 尝试编译 `pinchRatioClustering` 和 `genSimMatrix`。
- 把配置日志和编译日志保存到当前目录。
- 将现有 Python 版图复现结果拷贝到当前目录作为对照参考。

## 关键阻塞点

- 旧版源码包本身不包含 Eigen 头文件，而 CMake 也没有在当前环境里找到系统 Eigen。
- 旧版 `tests/test_iris.sh` 引用了 `../../testData/randOrder_150` 与 `../../testData/linOrder_150`，但提供的源码包旁边没有这套 `testData` 目录。
- 这意味着即使解决 Python 3 问题，当前拿到的旧版包也还不是一个“开箱即跑”的完整复现实验包。

## 当前 Python 版与论文差得最明显的地方

### Iris

- `TILO-PRC(K Means)`: result=`0.518760`, delta=`-0.241240`
- `Spectral`: result=`0.759199`, delta=`+0.229199`
- `TILO-PRC(Spectral)`: result=`0.707363`, delta=`-0.182637`
- `Aff. Prop.`: result=`0.598823`, delta=`+0.408823`

### Vote

- `Aff. Prop.`: result=`0.122694`, delta=`+0.082694`
- `DBScan`: result=`-0.010921`, delta=`-0.080921`
- `Spectral`: result=`0.557197`, delta=`-0.042803`
- `K Means`: result=`0.585018`, delta=`-0.024982`

## 产物

- 旧版配置日志：`F:\prc_v1_d2026_04_24\test\legacy_prc_outputs\legacy_cmake_configure.log`
- 旧版编译日志：`F:\prc_v1_d2026_04_24\test\legacy_prc_outputs\legacy_cmake_build.log`
- 当前 Python 版诊断拷贝：`F:\prc_v1_d2026_04_24\test\legacy_prc_outputs\current_pyprc_paper_fig_diagnostics.json`
- 当前 Python 版图像拷贝：`F:\prc_v1_d2026_04_24\test\legacy_prc_outputs\current_pyprc_paper_fig.png`
- 自动化脚本草稿：`F:\prc_v1_d2026_04_24\test\run_legacy_prc_repro.py`

## 说明

- 这次没有重新执行 Python 版 `reproduce_paper_fig_ari.py`，因为本地 Python 执行在桌面沙箱审批上超时；所以当前 Python 版结果是从现有 `experiments/output` 复制过来的参考件。
- 如果后续补齐 Eigen 依赖，下一步就可以继续用 `test/run_legacy_prc_repro.py` 或一个等价 CLI 驱动脚本，真正把旧版 `pinchRatioClustering` 接到 `K Means / Spectral / DBSCAN / Aff. Prop. / Mean Shift` 的初始化标签上，完成整张图的 legacy 复现实验。
