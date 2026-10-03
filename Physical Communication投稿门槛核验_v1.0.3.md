# Physical Communication 投稿门槛核验 v1.0.3

## 核验范围

- **目标期刊：** *Physical Communication*
- **ISSN：** 1874-4907
- **文章类型：** 原创研究论文，最终名称以投稿系统为准
- **核验日期：** 2026-10-03
- **当前状态：** 候选期刊，尚未达到“可提交”门槛

## 已核验的官方公开记录

| 项目 | 来源 | 结果 |
|---|---|---|
| 期刊身份、ISSN、出版社 | Elsevier Serial Metadata API: <https://api.elsevier.com/content/serial/title/issn/18744907> | HTTP 200；刊名 *Physical Communication*，ISSN `1874-4907`，出版社 Elsevier B.V. |
| 开放获取属性 | 同一 API | 返回 `openaccess=0`、`openaccessArticle=false`、`openaccessType=None`。这不是 APC 金额或支付主体的最终确认。 |
| Scopus source 交叉记录 | API 返回的 source 链接: <https://www.scopus.com/source/sourceInfo.url?sourceId=11300153720> | 仅作期刊身份交叉记录，不能替代 JCR/MJL 或 CAS 分区证据。 |
| 投稿指南 | <https://www.sciencedirect.com/journal/physical-communication/publish/guide-for-authors> | 本次自动请求返回 HTTP 403，未把动态页面中未读取的字段当作已确认规则。 |

## 必须在提交前完成

1. 在学校认可的 Clarivate JCR/MJL 门户按 ISSN `1874-4907` 查询并记录
   年份、学科类别、JCR 分区、SCIE 状态、访问日期和证据编号。
2. 在学校认可的 CAS 门户记录年份、学科类别、CAS 分区、访问日期和证据编号。
3. 在普通浏览器的 Elsevier 投稿系统复核 article type、摘要长度、关键词、
   highlights、graphical abstract、图表上传、补充材料、数据/代码声明、AI
   声明、ORCID、CRediT、利益冲突和 APC 字段。
4. 将通信作者固定为张长江，邮箱
   `zhangchangjiang@ccbupt.cn`；基金声明为无专项基金，致谢无额外内容；
   CRediT 使用投稿材料中的最终版本。
5. 在 Zenodo 真实生成 v1.0.3 版本 DOI 后，回写主文、README、CITATION.cff、
   数据/代码声明和投稿信，并重新运行编译与 ZIP 完整性检查。

## 通过规则

在机构 JCR/CAS 证据、投稿系统字段和真实 v1.0.3 DOI 全部齐全前，
*Physical Communication* 只能标记为“候选”。公开网页元数据不能推断学校认可
的分区，也不能替代投稿系统中的最新字段。
