# Physical Communication 暂定投稿计划 v1.0.3

## 投稿定位

- **首选期刊：** *Physical Communication*（候选，分区证据待机构门户核验）
- **备选顺序：** AEÜ；*Digital Signal Processing*
- **论文类型：** Original Research，最终选项以 Elsevier 投稿系统为准
- **论文题目：** *Source-free pilot adaptation for RIS-assisted wideband MIMO channel estimation under explicit distribution shifts*
- **通信作者：** Changjiang Zhang，`zhangchangjiang@ccbupt.cn`
- **基金：** This research received no specific grant from any funding agency in the public, commercial or not-for-profit sectors.
- **致谢：** 无额外致谢
- **APC：** 按作者承担方案准备，金额和支付主体在投稿系统确认

## 科学主线

在显式 BS--RIS--UE 宽带模拟器中，目标 CSI 标签不可用、导频预算为两列
identity pilots 时，pilot-only adaptation 能否恢复冻结学习估计器在分布漂移下
的部分损失？恢复是否受 RIS 尺寸、beam squint、SNR、pilot budget 和更新容量限制？

主结论只覆盖已测的合成生成器：四个 canonical shifts 上 adapter 恢复冻结估计器的
部分 NMSE 损失，strict held-out support/evaluation 保留该方向；LS 仍是竞争性参考，
8-element beam-squint/5 dB 单元使三个通信指标同时恶化，full-model 以约 6.96 倍
可训练参数获得更低 NMSE，preregistered delay-tail 项未通过独立贡献门槛。
论文不宣称 measured-channel validity、universal superiority 或物理项已证实的独立机制贡献。

## 版本发布

1. v1.0.2 保持不变。
2. v1.0.3 增加三组 source-estimator 权重和四个 canonical shift 的 adapter 权重。
3. 权重使用 CPU 可加载的 `state_dict` 与 JSON 元数据；代码 MIT，权重和论文材料 CC BY 4.0。
4. 完成权重 reload、前向有限性、标签隔离、SHA-256、凭据扫描和 ZIP 完整性检查。
5. 创建 GitHub `v1.0.3` release，Zenodo 已预留 DOI `10.5281/zenodo.23121462`；发布后核对记录并回写最终材料。

## 投稿材料

- 主文：12 页，正文约 6,381 词，保留完整证据链和失败单元。
- Highlights：3--5 条，字符限制以投稿系统实时字段为准。
- Graphical abstract：使用可编辑的内部设计稿，提交资格和 AI/图像政策以期刊页面确认。
- Cover letter：突出 RIS 宽带信道估计、source-free pilot adaptation、held-out evaluation、
  通信指标和失败边界。
- Declarations：通信作者、无专项基金、无额外致谢、CRediT、AI-use、利益冲突和合成数据声明统一。

## 阶段验收

- [x] 权重导出与 CPU reload verifier 通过
- [x] v1.0.3 包含 SHA-256 manifest 和许可证
- [ ] GitHub tag/release `v1.0.3` 推送成功
- [x] Zenodo v1.0.3 草稿已预留 DOI `10.5281/zenodo.23121462`\n- [ ] 发布 Zenodo 草稿并核对公开版本记录
- [ ] Physical Communication 投稿指南和系统字段逐项确认
- [ ] Clarivate JCR/MJL 与 CAS 机构证据完成
- [ ] 干净环境编译主文和补充材料，主文 10--12 页、正文 6,000--10,000 词

在未完成最后三项之前，期刊状态保持“候选”，不写成“可提交”。
