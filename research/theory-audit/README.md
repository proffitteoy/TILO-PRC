# TILO / PRC Theory Audit

本目录不继续扩展应用实验，而是对 TILO（Topologically Intrinsic Lexicographic Ordering）与 PRC（Pinch Ratio Clustering）进行一次独立理论审判。

目标是回答：

[
oxed{	ext{TILO/PRC 到底优化了什么，能保证什么，最坏能坏到什么程度？}}
]

只有出现明确的理论对象、近似界、复杂性结论或严格分离例，才继续把它作为研究线；否则保留为已有算法实现，不再投入研究算力。

## 1. 基本对象

给定加权图 (G=(V,E,w)) 和顶点排序

[
o=(v_1,ldots,v_n),
]

定义前缀

[
A_i={v_1,ldots,v_i},
]

以及前缀边界代价

[
b_i=w(partial A_i).
]

TILO 将所有 (b_i) 排序后形成 width vector，并按字典序比较 order。因而其全局目标首先最小化

[
max_i b_i,
]

随后在这一最优层上继续最小化第二大、第三大等边界值。

因此第一个必须严格审查的桥梁是：

> TILO 的 global thin ordering 是否可被表述为 cutwidth 目标的字典序细化；现有 local shift / strong irreducibility 与经典 graph-layout local search 有何精确关系？

“看起来像 cutwidth”不能作为结论，必须按定义证明映射并注明加权/无权版本差异。

## 2. 四条理论主线

### T1. Cutwidth / layout bridge

研究：

- global thin ordering 与 minimum cutwidth ordering 的精确关系；
- strong irreducibility 是否对应某种局部最优 ordering；
- pathwidth / cutwidth / linear arrangement 文献中的结构定理能否迁移；
- 哪些经典 hard instances 对 TILO 仍然困难。

最低交付：一个对象级定义对照和至少一个严格 theorem / separation statement。

### T2. Pinch cluster 作为离散能量势垒

令

[
E(A)=w(partial A).
]

Pinch cluster 的核心不是普通 one-flip local minimum，而是：若通过连续单点增删最终降低边界，则路径中必须先跨越更高边界。

因此把它与以下对象逐项比较：

- metastable local minimum；
- energy barrier / communication height；
- local-search basin；
- submodular cut-energy landscape。

研究问题：

[
	ext{pinch cluster}
stackrel{?}{Longleftrightarrow}
	ext{某种 cut-energy metastability}.
]

若不能等价，则寻找最小严格分离例。

### T3. Cheeger / NCut / spectral sweep approximation

对同一个图精确计算或近似高精度计算：

- minimum conductance / Cheeger cut；
- normalized cut；
- spectral sweep cut；
- TILO/PRC 返回切分。

定义固定 objective 下的 ratio，例如

[
R(G)=
rac{F(operatorname{PRC}(G))}
{min_A F(A)}.
]

机器研究只接受两类有价值结果：

1. 找到统一上界 (R(G)le C) 或参数化上界；
2. 构造 (R(G)	oinfty) 的显式 graph family。

“在 Iris 上效果不错”不属于本理论审计证据。

### T4. Complexity and exact solvability

分别研究：

- global thin ordering 的计算复杂性；
- strong-irreducible local optimum 的求取复杂性；
- PRC split selection 的复杂性；
- tree、cycle、bounded treewidth、series-parallel、planar 等图类是否可精确求解。

任何 hardness / FPT / polynomial claim 都必须对应明确的问题版本和输入编码。

## 3. 48-hour kill-or-revive experiment

第一轮只研究小图，优先使用无标号 connected graphs。

建议规模：

- 完整枚举 (nle 8)；
- 资源允许时扩到 (n=9)；
- 无权图先行，再加入小整数边权。

每个图至少记录：

- exact cutwidth；
- lexicographically optimal boundary vector；
- TILO 实际输出；
- strong irreducibility；
- PRC split；
- optimal conductance / NCut；
- spectral sweep；
- 各 objective ratio；
- automorphism/canonical graph id。

然后自动搜索：

- 最小 TILO ≠ global-thin 例；
- 最小 PRC ≠ optimal-cut 例；
- 最大 approximation ratio；
- pinch cluster 与普通 local minimum 的最小分离例；
- cutwidth 相同但 lexicographic width 不同的最小图。

## 4. Agent protocol

同一问题至少并行四类 agent：

- **Equivalence agent**：寻找精确等价；
- **Approximation agent**：寻找统一界；
- **Separation agent**：专找反例和发散 family；
- **Prior-art agent**：判断命题是否已经存在于 graph layout / clustering / metastability 文献。

只有可以被写成清楚数学命题的输出才进入候选结果。

## 5. Kill criteria

48 小时理论审判后，若同时满足：

- 没有新的 exact equivalence；
- 没有 approximation guarantee；
- 没有有解释力的 strict separation family；
- 主要性质已被现有 graph-layout/clustering 理论直接覆盖；

则停止将 TILO-PRC 作为独立研究线，仓库继续只承担历史算法复现和应用工具角色。

## 6. Revive criteria

出现下列任意一项即可继续：

- lexicographic cutwidth 的新结构结果；
- pinch cluster 的新 metastability characterization；
- PRC 对经典 cut objective 的非平凡 approximation theorem；
- 明确的 unbounded separation theorem；
- 某个重要图类上的 exact/FPT algorithm；
- 一个能解释原算法经验表现、且不只是重新命名已有概念的结构定理。

实验规范见 [EXPERIMENT_SPEC.md](EXPERIMENT_SPEC.md)。
