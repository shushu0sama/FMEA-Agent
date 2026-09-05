# <Stage ID> — <Stage Name> 阶段收尾记录

> 正文以简体中文（zh-CN）为主体；Status、技术标识符、路径、命令、Git 标识符和原始输出保持 canonical form。

Status:
日期：

## 1. 目标

本阶段原始目标。

## 2. 范围

范围内：

范围外：

## 3. Git

Branch:

起始 Commit：

实现 Commit：

收尾 Commit：

最终 Commit：

## 4. 实际交付

实际交付能力。

## 5. 关键决策

本阶段真正形成的重要决定。仅记录实际决策。
长期架构决定应链接 ADR / architecture document。

## 6. 证据

引用：

- 测试
- 研究报告
- 运行探测
- 基准测试
- 架构文档

不要复制大型研究报告。

## 7. 验证

pytest:
ruff:
mypy:
integration:
benchmark:
regression:

说明哪些为本机执行（LOCAL），哪些为 CI，哪些为 EXTERNAL_REVIEW。

## 8. 开发中发现的问题

记录：

- RED 测试失败
- 契约不一致
- 上游限制
- 发现的缺陷
- 收尾修正

## 9. 已知限制

明确尚未解决的问题。

## 10. 延后内容

明确推迟到后续 MVP 的内容。

## 11. 受影响文件与契约

列出主要文件，不需要列全部 diff。

## 12. 最终评估

ACCEPTED / CONDITIONAL / BLOCKED / CHANGES_REQUIRED / COMPLETE

## 13. 下一阶段

下一阶段及进入条件。
