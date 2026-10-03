# DCN 暂定投稿计划 R033

## 当前决策

- **暂定第一投稿目标：** Digital Communications and Networks（DCN）。
- **论文定位：** Original Research，主题是无线通信中的 source-free pilot adaptation、RIS 宽带信道估计、通信指标和失效边界。
- **工作题目：** *Source-Free Pilot Adaptation for RIS-Assisted Wideband MIMO Channel Estimation under Explicit Distribution Shifts*。
- **投稿策略：** 先完成可复现证据和 DCN 格式化，再提交；DCN 的 JCR/CAS 分区仍需用机构 Clarivate JCR/MJL 与 CAS 门户核验。用户提供的新锐截图只作为筛选记录，不作为 JCR 证据。

## R033 最终验证状态（2026-10-03）

- 主文 `paper-draft-r025.tex` 已用本地 `latexmk` 编译通过，作者信息版 PDF 为 12 页。
- `texcount` 统计正文 6,381 词，标题 132 词，图注/浮动体 320 词，满足 6,000–10,000 词和 10–12 页目标。
- `supplementary_tables_r032.tex` 已强制重编译通过，生成 3 页补充表 PDF。
- 已检查 PDF 文本、LaTeX 日志、交叉引用/引用和第 10 页版式；未发现 undefined reference/citation、旧 Tesla/P100 表述或凭据泄露。
- 内置 `compile_latex_document` 因当前编辑器环境返回 `Unable to find standard directories for platform`，因此以本地成功编译结果作为可核验编译证据，源文件保持不变。
- `submission_package_v1.0.2.zip` 已重新生成，共 108 个 allowlisted 文件，credential scan 通过，主文源文件哈希与 manifest 一致；包内包含作者、许可证、CITATION.cff、GitHub tag 和 Zenodo DOI 信息。

## Phase 4 最新检查点（2026-10-03）

- 已运行 `experiments/final_novelty_pass.py`；五条 DOI 邻近记录均成功解析，Semantic Scholar 元数据请求均返回成功或可解释的 DOI 重定向状态。机器可读记录保存在 `refine-logs/FINAL_NOVELTY_PASS_20261002.json`。
- DOI 核验只支持“已检查记录可解析”的范围性结论，不构成全局新颖性证明；论文中的 search-bounded 表述保持不变。
- 作者姓名、单位、公开联系邮箱和一作 ORCID 已由作者提供并写入 `AUTHORS.md`；机构 JCR/CAS 记录、通信作者指定、基金/致谢和 DCN 投稿系统字段仍待补齐，因此 DCN 继续保持“暂定投稿目标”。

## 已锁定的科学主线

在显式 BS–RIS–UE 宽带模拟器中，目标 CSI 标签不可用、导频预算为两列 identity pilots 时，pilot-only adaptation 能否恢复冻结学习估计器在分布漂移下的部分损失？恢复是否受 RIS 尺寸、beam squint、SNR、pilot budget 和更新容量限制？

主结论保持证据边界：四个 canonical shifts 上 adapter 恢复冻结估计器的部分 NMSE 损失，strict held-out support/evaluation 协议保留该方向；LS 仍是竞争性参考，8-element beam-squint/5 dB 单元使三个通信指标同时恶化，full-model 以约 6.96 倍可训练参数获得更低 NMSE，preregistered delay-tail 项未通过独立贡献门槛。论文不声称 universal superiority、measured-channel validity 或物理项导致收益。

## R033 完成状态

1. 主文已按 Nature-style evidence ladder 重排，目标正文 6,000–10,000 英文词、10–12 页。
2. canonical sweep 已改为显式 prequential batch-level adaptation：512 个目标样本分为四个 128 样本批次，每批 ten optimizer updates，adapter 状态跨批次延续，更新后才评分。
3. target CSI label isolation 已落实到 adapter API；适配函数只接收 pilot features，标签仅用于评分。
4. 生成器公式已统一为 `h_UE.T @ diag(reflection) @ h_BS`，并加入 `ris_cascaded_generator_consistency_test.py`。
5. canonical、held-out、robustness、physics-control、capacity 和 CPU cost artifacts 已按当前代码在 CPU 上重跑；主表新增 LS BER/SE；Figure 5 改为五位小数显示。
6. 模拟器参数边界、统计实验单位、block-conditional interval 和 multiplicity 定位已写入主文与复现 README。
7. Nature audit、claim–evidence map、supplementary map 和 R033 复现包已同步；剩余工作只属于投稿元数据和机构核验。

## 阶段计划与验收条件

### Phase 1：证据冻结（已完成）

- 固定 seeds `20261002`, `20261003`, `20261004`。
- 固定 source training、四个 canonical shifts、512/512 held-out split、OMP/LS、18-cell robustness 和 negative physical control。
- 固定独立重复单位为 training/data seed；channel-level paired intervals 只作为 block-conditional summaries。

**验收：** 每个主张都能回溯到 JSON、表格和图；没有 target label 进入适配优化器。

### Phase 2：主文与图表定稿（已完成）

- 编译 `paper-draft-r025.tex`，确认正文词数、总词数和页数。
- 运行 `texcount`、`pdfinfo`、`pdftotext`，检查 undefined references/citations、表格宽度和图注。
- 编译 `supplementary_tables_r032.tex`，确认 S1–S3 与主文引用一致。
- 用五张最终图重新运行 Nature figure alignment/collision QA。

**验收：** 已通过。作者信息版主文 12 页、正文 6,381 词；图 4 不再声称有未展示的 held-out NMSE panel；图 5 使用五位小数，未隐藏小效应。

### Phase 3：数据、统计与复现包（已完成）

- 运行 `experiments/ris_cascaded_generator_consistency_test.py`。
- 运行 `experiments/export_latex_tables.py`、`experiments/plot_paper_figures.py`。
- 运行 `experiments/aggregate_cpu_artifacts.py`、`experiments/create_submission_package.py`，生成 `submission_package_v1.0.2.zip` 与 manifest；包中只保留当前 CPU 设备元数据、脚本、JSON、表格和五张最终图。
- 对 manifest 做私密信息扫描；不放入 SSH 地址、密码、私有主机路径或旧 CUDA artifacts。

**验收：** 已通过。manifest 哈希可重建，credential scan 通过，README 给出环境、参数边界和重跑命令；当前 release 的所有纸面结果 per-seed JSON 和汇总均记录为 CPU。

### Phase 4：DCN 投稿门槛（需要作者输入）

- 已完成自动化官方来源核验，记录见 `DCN投稿门槛核验_R034.md`；Elsevier Serial Metadata API 返回 DCN 身份、ISSN/eISSN 和开放获取属性。
- ScienceDirect 动态 Guide for Authors 本次终端请求返回 HTTP 403，未读取到的动态字段不作已确认要求；提交前必须在浏览器投稿系统复核。
- 当前作者信息版工作稿的 venue-templates 格式检查见 `dcn_format_validation_R034.txt`，12 页和字体嵌入检查通过。
- 在机构 Clarivate JCR/MJL 与 CAS 门户按 ISSN `2352-8648`、`2468-5925` 查询并记录访问日期、年份、类别、JCR quartile、CAS quartile、SCIE 状态和导出/截图编号。
- 填写作者姓名、单位、通信邮箱、ORCID、CRediT、基金、致谢、利益冲突和预印本/会议版本信息。
- 已完成公开仓库（GitHub + Zenodo）、双许可证、`v1.0.2` release tag、Zenodo v1.0.2 版本 DOI `10.5281/zenodo.23119393`、概念 DOI 和数据代码声明。
- 核对 DCN 当前 Guide for Authors 的 article type、editable source、highlights、figure uploads、AI-use disclosure、declarations 和 graphical abstract 字段。
- 确定 APC 支付主体及是否需要补充材料单独上传。

**当前验收：** 自动核验和公共发布已完成；`AUTHOR_INPUT_NEEDED` 仍未清零。DCN 继续作为“暂定目标”，直到机构分区、通信作者/基金字段和投稿系统字段全部完成。

### Phase 5：提交前两轮检查

**T−7 至 T−3 天：** 由作者核对所有元数据和 JCR/CAS 记录；我根据最终字段更新标题页、Data/Code Availability、Declarations、cover letter 和 highlights。

**T−2 至 T−1 天：** 在干净目录中重新编译主文和 SI，核验 PDF、图文件、BibTeX、zip manifest、引用、交叉引用、字数、页数和 credential scan。

**T−0：** 只在作者确认投稿系统字段、分区记录、仓库 DOI 和 APC 决策后提交 DCN。若门槛不满足，按已核验的备用顺序转向 Computer Networks、IEEE Access 或 Physical Communication，并重新检查其官方指南和机构分区。

## 需要作者补齐的信息

1. 作者与通信作者信息：姓名、单位、邮箱、ORCID、CRediT。
2. 基金、致谢、利益冲突、预印本/会议重叠情况。
3. 机构认可的 JCR/CAS 年份、类别、分区和收录记录。
4. 通信作者指定、最终联系邮箱、基金和致谢；公开仓库 URL、许可证、v1.0.2 版本 DOI、概念 DOI 和 release tag 已完成；是否公开模型权重。
5. DCN APC 预算、graphical abstract/highlights 要求和最终软件版本披露偏好。
