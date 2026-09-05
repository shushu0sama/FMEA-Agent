# ADR-002: Canonical System Model 作为集成边界

**Status:** ACCEPTED  
**基线:** Bootstrap v0.1

## 背景

FMEA 必须从多个可能来源获取工程事实，同时不将领域逻辑绑定到 OpenSysML、REST payload、PLM 或其他供应商模型。

## 决策

引入项目自有的 Canonical System Model。外部模型来源通过适配器映射到该模型。

## 影响

额外工程来源可以通过适配器集成。项目必须投入规范语义设计和映射测试。

## 重新评估条件

仅当实验、标准、兼容性约束或工程需求表明当前决策实质性阻碍项目目标时，才重新评估。
