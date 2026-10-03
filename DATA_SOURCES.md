# 数据与仿真资源

## 主资源：DeepMIMO

- 官方入口：[DeepMIMO](https://deepmimo.net/)
- 适用任务：mmWave/massive-MIMO 信道、用户位置变化、RIS 辅助场景、宽带 OFDM 研究。
- 使用原则：按场景和用户位置划分 source/target，不能随机打散同一几何场景中的相邻样本到训练和测试集。
- 需要保存：场景名称、天线/RIS 配置、子载波数、用户范围、路径数、随机种子和生成脚本版本。

## Fallback：可复现几何仿真

当前仓库中的 `experiments/ris_ofdm_baseline_smoke.py` 和
`experiments/ris_sparse_omp_smoke.py` 提供 NumPy 级 fallback，用于：

- 检查复数信道、宽带频率响应和 AWGN 注入；
- 检查稀疏导频下的 LS/OMP 指标；
- 在没有 PyTorch 或 GPU 时验证数据形状和指标实现。

该 fallback 不能替代真实射线追踪数据，也不能单独支撑论文的泛化结论。

## 数据泄漏控制

1. 目标域的真实 CSI 只用于最终评估，不能进入在线适配损失。
2. 源域和目标域按用户位置、传播环境或信道老化区间划分，而不是按样本随机划分。
3. 所有预处理统计量只从源域训练集估计。
4. 每次实验保存配置、随机种子、数据版本和代码提交状态。
