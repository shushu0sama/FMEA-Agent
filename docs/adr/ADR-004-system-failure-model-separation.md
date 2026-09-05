# ADR-004: 分离 System Model 和 Failure Model

**Status:** ACCEPTED  
**基线:** Bootstrap v0.1

## 背景

工程结构 / 功能事实与失效分析知识具有不同的生命周期、语义和证据要求。

## 决策

保持 System Model 和 Failure Model 在逻辑上分离，通过显式映射 / 引用连接两者。

## 影响

Schema 保持更清晰，多种失效分析方法可以演进而不破坏工程模型语义。

## 重新评估条件

仅当实验、标准、兼容性约束或工程需求表明当前决策实质性阻碍项目目标时，才重新评估。
