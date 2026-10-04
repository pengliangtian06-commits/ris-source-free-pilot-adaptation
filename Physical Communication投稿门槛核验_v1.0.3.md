# Physical Communication 投稿门槛核验 v1.0.3

## 核验范围

- **目标期刊：** *Physical Communication*
- **ISSN：** 1874-4907
- **文章类型：** 原创研究论文，最终名称以投稿系统为准
- **核验日期：** 2026-10-04
- **当前状态：** 候选期刊，尚未达到“可提交”门槛

## 已核验的官方公开记录

| 项目 | 来源 | 结果 |
|---|---|---|
| 期刊身份、ISSN、出版社 | Elsevier Serial Metadata API: <https://api.elsevier.com/content/serial/title/issn/18744907> | HTTP 200；刊名 *Physical Communication*，ISSN `1874-4907`，出版社 Elsevier B.V. |
| 开放获取属性 | 同一 API | 返回 `openaccess=0`、`openaccessArticle=false`、`openaccessType=None`。这不是 APC 金额或支付主体的最终确认。 |
| Scopus source 交叉记录 | API 返回的 source 链接: <https://www.scopus.com/source/sourceInfo.url?sourceId=11300153720> | 仅作期刊身份交叉记录，不能替代 JCR/MJL 或 CAS 分区证据。 |
| 投稿指南与 OA/APC 页面 | [Guide for authors](https://www.sciencedirect.com/journal/physical-communication/publish/guide-for-authors); [Open access options](https://www.sciencedirect.com/science/journal/18744907/publish/open-access-options) | 已核验摘要不超过 250 词、关键词 1--7 个、Highlights 3--5 条且每条不超过 85 字符、Graphical abstract 建议尺寸 531 x 1328 像素（高 x 宽）、LaTeX 源文件、Option C 数据政策、声明字段和 OA APC 页面。详见 `venue_live_verification_20261004.md`。 |

## 必须在提交前完成

1. 在学校认可的 Clarivate JCR/MJL 门户按 ISSN `1874-4907` 查询并记录
   年份、学科类别、JCR 分区、SCIE 状态、访问日期和证据编号。
2. 在学校认可的 CAS 门户记录年份、学科类别、CAS 分区、访问日期和证据编号。
3. 由作者登录 Elsevier 投稿系统复核个性化的 article type、摘要长度、关键词、
   highlights、graphical abstract、图表上传、补充材料、数据/代码声明、AI
   声明、ORCID、CRediT、利益冲突和 APC 字段；公共规则已记录在
   `venue_live_verification_20261004.md`。
4. 将通信作者固定为张长江，邮箱
   `zhangchangjiang@ccbupt.cn`；基金声明为无专项基金，致谢无额外内容；
   CRediT 使用投稿材料中的最终版本。
5. 在 Zenodo 真实生成 v1.0.3 版本 DOI 后，回写主文、README、CITATION.cff、
   数据/代码声明和投稿信，并重新运行编译与 ZIP 完整性检查。

## 通过规则

在机构 JCR/CAS 证据、作者登录后的投稿系统字段、完整邮政地址和最终作者确认全部齐全前，
*Physical Communication* 只能标记为“候选”。公开网页元数据不能推断学校认可
的分区，也不能替代作者登录后投稿系统中的最终字段。
