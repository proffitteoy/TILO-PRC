# Theory Audit Experiment Specification

## 1. Graph universe

M0 使用 connected simple unlabeled graphs。

每个图必须有稳定 canonical id。建议保存 graph6/canonical adjacency 表示，并记录：

```json
{
  "graph_id": "...",
  "n": 8,
  "m": 11,
  "weighted": false,
  "source": "unlabeled-enumeration"
}
```

加权实验必须作为独立 universe 版本，不与无权结果混算。

## 2. Exact quantities

小图阶段优先 exact：

### 2.1 Boundary sequence

对 ordering (o) 计算

[
b_i=w(partial A_i).
]

保存：

- 原序列 ((b_1,ldots,b_{n-1}))；
- 降序 width vector；
- 最大值（cutwidth of this ordering）。

### 2.2 Global lexicographic optimum

完整枚举 ordering 或使用经 oracle 核对的 exact solver，得到：

- minimum cutwidth；
- lexicographically minimum width vector；
- 一个 canonical optimal ordering；
- optimal ordering 数量。

TILO 输出必须与 global optimum 分开记录；不能把 local algorithm 的结果当作 exact thin position。

### 2.3 Cut objectives

至少计算：

[
operatorname{cut}(A,A^c),
]

[
phi(A)=
rac{operatorname{cut}(A,A^c)}
{min(operatorname{vol}A,operatorname{vol}A^c)},
]

以及仓库 PRC 实际使用的 PinchRatio / NCut 定义。

所有 ratio 必须显式注明 numerator 与 denominator 的 objective，禁止跨 objective 比较。

## 3. Baselines

M0 至少包含：

- exact best cut under the selected objective；
- spectral ordering / sweep；
- TILO ordering；
- PRC selected split；
- random ordering control。

后续可加入 Kernighan–Lin、minimum linear arrangement 等，但不能让 baseline 扩张阻塞第一轮理论扫描。

## 4. Minimal-counterexample reduction

发现异常后必须自动做：

1. 删除不必要顶点；
2. 删除不必要边；
3. 若为加权图，降低权重复杂度；
4. quotient by obvious symmetry when valid；
5. 重新 exact verify。

报告只引用最小化后的 witness，同时保留原始发现 provenance。

## 5. Initial searches

### S1
寻找 TILO local result 与 global lexicographic optimum 不同的最小图。

### S2
寻找相同 cutwidth、不同 lexicographic width vector 的最小 graph pair/order pair。

### S3
寻找 PRC 在 conductance 或 NCut 下 ratio 最大的小图。

### S4
寻找 pinch-cluster 与 ordinary one-vertex local-minimum 的双向严格分离例。

### S5
在 tree / cycle / complete / complete bipartite / barbell / lollipop / grid / expander-like families 上生成参数扫描，寻找可外推的 closed-form pattern。

## 6. Claim ledger

所有理论候选统一记录：

```json
{
  "claim_id": "TILO-C-0001",
  "statement": "...",
  "scope": "...",
  "status": "PROPOSED|FINITE_VERIFIED|REFUTED|PROVED",
  "witnesses": [],
  "counterexample": null,
  "prior_art": []
}
```

`FINITE_VERIFIED` 只表示当前 graph universe 内无反例。

## 7. Acceptance after 48 hours

输出一份 THEORY_AUDIT_REPORT，必须明确属于以下哪一种：

- **REVIVE / equivalence**；
- **REVIVE / approximation**；
- **REVIVE / separation**；
- **KILL / prior-art dominated**；
- **KILL / no stable structure found**。

不允许用“还可以继续做更多实验”作为最终结论。
