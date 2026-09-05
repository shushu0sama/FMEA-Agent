# 会话交接模板

> 仅在上下文过长或当前会话无法安全继续，导致同一正式 Stage 必须换会话时使用。
> Stage 关闭后，不将本文件作为永久的当前状态文件。
> 正文使用简体中文；技术标识符、状态、路径、命令和输出保持原形。

## Stage

MVP / Stage ID:

Stage 名称：

Stage 状态：

## Branch

仓库：

Branch:

预期 HEAD：

工作区状态：

未提交/未跟踪文件及各自用途（保留现状，不自动丢弃）：

当前写入会话与交接后写入责任（避免同时修改同一 checkout）：

## HEAD

最近确认的 Commit：

相关 tag：

## 已完成工作

-

## 当前状态

-

当前 Spec / Plan / 上一阶段记录的路径：

本次明确授权的范围与已确认用户决定（链接权威文档，不复制整段聊天）：

本地资料与环境恢复：输入位置、是否 Git 跟踪、工具版本、服务是否需重启、配置变量名。
不得记录密钥、连接密码或敏感配置值；新 worktree 中需要重新核对可用性。

## 测试

```text
pytest:
ruff:
mypy:
integration:
benchmark:
git diff --check:
```

证据分类：

```text
LOCAL / CI / EXTERNAL_REVIEW
```

验证对应的 HEAD / 未提交差异：

未运行、失败或被中断的检查及具体原因：

## 决策

-

## 剩余工作

-

## 已知问题

-

## 下一步具体动作

先核对实际 checkout 与上述状态，再执行。若已被后续 Stage Record 取代，使用最新记录。
本交接文件保存到所属 Stage 目录，并由 PROGRESS 链接；恢复后记录接手情况，
阶段收尾时标为 HISTORICAL，不继续作为另一个当前状态入口。

执行：

```text

```
