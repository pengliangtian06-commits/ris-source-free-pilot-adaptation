# DCN 暂定投稿计划 R032

> Historical snapshot. R033 supersedes this plan; current repository and DOI
> details are recorded in `DCN暂定投稿计划_R033.md`.

## 1. 目标、定位与当前决策

- **暂定投稿目标：** Digital Communications and Networks（DCN）。
- **文章形态：** Original Research，定位为可复现的无线通信/AI 基准与失效边界研究。
- **工作题目：** *Source-Free Pilot Adaptation for RIS-Assisted Wideband MIMO Channel Estimation under Explicit Distribution Shifts*。
- **主问题：** 在 RIS 宽带分布漂移、目标 CSI 标签不可用且导频预算受限时，source-free pilot adaptation 能恢复冻结估计器多少性能，恢复是否依赖几何、SNR、pilot budget 和 adaptation capacity？
- **核心结论边界：** 在当前显式 BS–RIS–UE 模拟器和测试漂移范围内，pilot-only adaptation 可恢复冻结估计器的部分损失；该收益受小 RIS、beam squint、SNR 和更新容量限制。结果不支持 universal superiority，也不把失败的 delay-tail penalty 写成物理机制。
- **暂定状态：** 当前证据支持把 DCN 作为第一格式化目标。用户提供的截图属于新锐分区参考，不是 Clarivate JCR/MJL 记录；投稿前必须用机构账号核验最新 JCR/CAS 的 ISSN、类别、分区和收录状态。

## 2. R032 已完成项

- 重构主文论证链：问题 → 显式漂移协议 → canonical sweep → held-out support/evaluation → classical/pilot sensitivity → failure cell → negative physical control → cost and deployment implication。
- 保留五张主图，并完成 Nature figure 的 Python backend、source validation、panel alignment、PDF font floor 和 collision audit。
- 完成三种 seed 的 CPU/CUDA 结果、OMP 基线、held-out split、robustness、cost 和 negative-control 记录。
- 将相关工作矩阵、逐 seed 配对明细和 18-cell robustness 明细路由到 SI，主文保留改变解释的边界证据。
- 当前主文目标为 6,000–10,000 个英文词和 10–12 页；修订后使用 `texcount` 与 PDF 页数双重验收。

## 3. 分阶段执行计划

### Phase A：证据锁定（已完成，R032）

1. 固定 source/target generator、four canonical shifts、two-pilot canonical setting、three seeds 和 held-out support/evaluation split。
2. 固定 primary endpoint 为 NMSE，BER 和 spectral efficiency 为 communication-facing outcomes。
3. 固定 independent replication unit 为 training/data seed；不把 channel realizations 或 paired observations 当成独立 seed。
4. 对每条主张记录结果文件、表格、图和边界，避免把 canonical batch adaptation 写成完整 held-out 证明。

**退出条件：** JSON artifacts、table exporters、figure source 和 verifier manifests 能回溯到相同 seed/config；目标标签隔离检查通过。

### Phase B：Nature-style 主文整合（当前完成）

1. 按 Nature-style evidence ladder 排列 Results，确保每个小节只推进一个 claim。
2. 把 main text 限定为 core discovery、necessary support 和 conclusion-changing edge case；secondary intervals、full robustness matrix 和 search matrix 放入 SI。
3. 把 Discussion 改为综合解释，明确 alternative explanation、negative control、cost trade-off 和 simulator-to-hardware boundary。
4. 用术语表锁定 source-free pilot adaptation、canonical shift sweep、held-out support/evaluation、adapter-only、full-model adaptation、beam squint、NMSE、BER、spectral efficiency。

**退出条件：** 主文 10–12 页；正文 6,000–10,000 词；摘要、Results、Discussion 和 Conclusion 的数字与表格一致。

### Phase C：统计、引用、数据和图表审计（下一步）

1. `nature-statistics`：核对 n 的含义、paired unit、seed-level SD、2,000-resample bootstrap、Wilcoxon test、multiple-comparison wording 和图注统计说明。
2. `nature-citation`：逐段检查引用是否支持对应主张；Crossref/出版社元数据作为优先来源；保留 search-bounded 说明。
3. `nature-data`：建立生成数据、JSON summaries、source data、code、model/config 和 figure provenance 清单；确定公开仓库与 DOI 方案后再改写 availability statement。
4. `nature-figure`：复用已通过的五图 QA，重新确认最终 PDF 没有改变图源、尺寸、字体和布局。

**退出条件：** 生成 `nature_workflow_audit_R032.md`，所有 P0/P1 风险已关闭；作者信息和软件版本等事实缺口单列，不用猜测填补。

### Phase D：DCN 投稿材料与机构核验

1. 对照 DCN 官方 Guide for Authors，检查 article type、editable LaTeX/source、highlights、figure uploads、declarations、AI-use disclosure 和 data/code statement。
2. 由作者提供并核对姓名、单位、邮箱、ORCID、基金、CRediT contributions、corresponding author 和 competing interests。
3. 从机构 Clarivate JCR/MJL 和 CAS portal 记录 DCN 的访问日期、ISSN（2352-8648 / 2468-5925）、类别、JCR quartile、CAS quartile、收录状态和截图/导出记录。
4. 解决 open-access 预算、APC 承担主体和是否需要 graphical abstract 的最终决策。

**退出条件：** `venue_verification_template` 完整；DCN 作为主投目标的分区和收录门槛由机构记录确认；所有投稿字段不再有 AUTHOR_INPUT_NEEDED。

### Phase E：最终 package 与投稿

- 主文：`paper-draft-r025.tex`、PDF、BibTeX、五张 PDF/SVG/TIFF 图、SI tables。
- 伴随材料：cover letter、highlights、graphical abstract（若当前指南要求）、data/code availability、AI-use statement、declarations、suggested reviewers（若系统要求）。
- 送审前执行：latex compile、texcount、PDF page count、PDF text extraction、cross-reference grep、citation check、figure QA、zip manifest 和 private credential scan。
- 仅在作者完成元数据、机构分区核验、公开仓库/补充材料路径确认后提交；此前保持“暂定投稿目标”表述。

## 4. 主要风险与处理规则

| 风险 | 处理 |
|---|---|
| JCR/CAS 分区未由机构 portal 核验 | 不把截图或商业聚合站标记为 JCR 证据；保留 DCN 暂定状态 |
| simulator-only external validity | 在摘要、Discussion、Limitations 中明确；下一步为 measured/ray-traced channel 的同协议验证 |
| canonical adaptation 被误写成 held-out proof | 统一使用 canonical batch-level adaptation 与 strict held-out support/evaluation 两个术语 |
| 物理 penalty 失败 | 报告为 negative control；不声称 physics consistency causes the gain |
| lightweight 误读为 always faster/equally accurate | 同时报告参数量、CPU/CUDA 计时和 full-model accuracy；不外推硬件速度 |
| source data/repository 尚未公开 | 暂不声称 public availability；完成 DOI/仓库后再替换占位语句 |
| 作者/基金/ORCID 等缺失 | 在投稿前清单中标记 AUTHOR_INPUT_NEEDED；不生成虚假信息 |

## 5. 作者需要补齐的事实

1. 作者姓名、单位、通信作者邮箱、ORCID 和 CRediT roles。
2. 基金、致谢、利益冲突和是否存在相关预印本/会议版本。
3. Python/PyTorch/CUDA/驱动版本及最终硬件描述。
4. 公开仓库或 Zenodo 等持久化仓库、许可证、DOI 和 release tag。
5. 机构接受的 JCR/CAS 年份、类别和分区记录，以及 DCN APC 预算。

## 6. 当前下一步

先完成 Phase C 的统计、引用、数据和一致性审计，再做 Phase D 的机构 portal 核验。审计通过后再把主文切换到 DCN 的最终模板，并生成投稿包；在此之前不把 DCN 分区写成已确认事实。
