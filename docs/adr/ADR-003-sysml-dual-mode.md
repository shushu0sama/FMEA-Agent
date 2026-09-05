# ADR-003: 保留 SysML File Mode 和 Repository Mode

**Status:** ACCEPTED  
**基线:** Bootstrap v0.1

## 背景

离线基准和研究需要基于文件的模型，而工程场景需要具备仓库 / 版本感知能力的访问方式。

## 决策

在共同的系统模型端口之后同时保留 File Mode 和 Repository Mode。

## 影响

必须维护两个适配器，跨适配器一致性成为基准关注点。

## 重新评估条件

仅当实验、标准、兼容性约束或工程需求表明当前决策实质性阻碍项目目标时，才重新评估。
