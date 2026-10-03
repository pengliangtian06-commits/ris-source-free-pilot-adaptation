# DCN 投稿门槛核验 R034

## 核验范围

- **目标期刊：** Digital Communications and Networks（DCN）
- **投稿阶段：** 初次投稿
- **拟定文章类型：** Original Research
- **核验日期：** 2026-10-03
- **论文工作题目：** *Source-Free Pilot Adaptation for RIS-Assisted Wideband MIMO Channel Estimation under Explicit Distribution Shifts*

## 官方来源与可复核结果

| 项目 | 官方来源 | 结果 |
|---|---|---|
| 投稿指南 | <https://www.sciencedirect.com/journal/digital-communications-and-networks/publish/guide-for-authors> | 当前终端请求返回 HTTP 403，动态指南正文未能直接读取；因此本文档不把未读取的动态字段当作已确认要求。 |
| 期刊身份与 ISSN | Elsevier Serial Metadata API：<https://api.elsevier.com/content/serial/title/issn/23528648> | HTTP 200；返回刊名 Digital Communications and Networks、出版社 KeAi Communications Co.、pISSN 2468-5925、eISSN 2352-8648。 |
| 开放获取属性 | 同上 | API 返回 `openaccess=1` 和 `openaccessArticle=true`；APC 金额、减免政策和作者承担主体仍须在投稿系统确认。 |
| Scopus source record | 同上返回的官方链接：<https://www.scopus.com/source/sourceInfo.url?sourceId=21100823476> | 作为期刊身份交叉记录；不替代机构 JCR/CAS 分区证据。 |

## 本项目已有的期刊规则记录

`venue_guidelines_r026.md` 记录了 2026-10-02 对官方 DCN 指南的核验结果，包括 Original Research、可编辑源文件、最多 6 个关键词以及按当前指南/模板确定长度等工作约束。由于本次终端无法重新读取动态页面，提交前仍须在浏览器投稿系统中逐项复核这些字段。

当前工作稿的本地格式检查见 `dcn_format_validation_R034.txt`：PDF 共 11 页，处于本项目约定的 10–12 页范围；字体嵌入检查通过，但该工具不能替代 DCN 模板对字号、页边距和最终字段的判断。

## R034 结果来源一致性修复

提交包中的 held-out、robustness 和 physical-control per-seed JSON 已使用固定 seeds 在当前 CPU 环境重新生成，并由 `experiments/aggregate_cpu_artifacts.py` 重建汇总。所有纸面结果 JSON 的 `device` 字段现在为 `cpu`；物理控制的汇总为 3,072 个配对样本、差值 `+0.000885`、95% bootstrap CI `[+0.000710,+0.001078]`。旧的远端 CUDA 日志和带有 CUDA 标签的中间 artifact 不属于当前 paper-grade package。

## 尚未满足的机构和作者门槛

以下项目必须由作者或机构门户补齐，不能由公开网页元数据推断：

1. 机构认可的 JCR/MJL 年份、学科类别、JCR quartile、SCIE 状态和证据编号。
2. 机构认可的 CAS 分区年份、学科类别和证据编号。
3. 通信作者指定、最终联系邮箱、基金和致谢；作者姓名、单位、已提供的 ORCID、初步 CRediT 和利益冲突已记录在 `AUTHORS.md` 与 `submission_declarations_r029.md`。
4. 已完成公开仓库、许可证和 release tag；GitHub URL 为 <https://github.com/pengliangtian06-commits/ris-source-free-pilot-adaptation>，当前 tag 为 `v1.0.2`，Zenodo 概念 DOI 为 <https://doi.org/10.5281/zenodo.23118757>。Zenodo v1.0.1 版本 DOI 为 <https://doi.org/10.5281/zenodo.23118758>；v1.0.2 版本 DOI 待 Zenodo 索引后核对。是否公开模型权重仍需在投稿系统明确。
5. DCN 投稿系统中的 article type、highlights、graphical abstract、AI-use disclosure、declarations、figure uploads 和 APC 选项。

## 通过规则

在机构分区记录、通信作者/基金字段、投稿系统字段和 v1.0.2 版本 DOI 核验齐全后，才把 DCN 从“暂定目标”改为“可提交目标”。若任一门槛不满足，按 `DCN暂定投稿计划_R033.md` 中的备用期刊顺序重新执行同一核验流程。
