# 2026-09-05 — Credential Exposure Remediation

Status: REPOSITORY_REMEDIATED / PROVIDER_ROTATION_PENDING

## 检测

- Detection source：G0A + G0A-L Independent Review。
- Affected path：`.codex/config.toml`。
- Credential type：provider authentication token。
- Credential value in this record：NEVER RECORDED。
- First known historical presence：
  `5826eb63524f2c1e0da2429527eeee5c4e42ed16`。

本记录不包含、验证、使用或复制旧 credential。

## 当前处置

- `.codex/config.toml` 已从当前 Git tracked tree 移除，本机文件保留。
- `.gitignore` 已加入 `.codex/config.toml`，防止再次提交个人配置。
- Provider-side revocation/rotation：PENDING USER CONFIRMATION。
- History rewrite：NOT_PERFORMED。

## 历史处理决定

本次不执行 `git filter-repo`、`git filter-branch`、BFG、force push、tag rewrite
或任何 commit SHA rewrite。Provider 侧撤销 / 轮换用于使已暴露 credential 失效；
未经独立治理批准重写历史会破坏 MVP-0/MVP-1 release tag、Records 与审计证据中
已有的 commit SHA 锚点。

此决定不表示历史中的 credential 风险已自动消失。Provider 侧状态在用户明确确认前
保持 `PENDING USER CONFIRMATION`。

## 后续预防

- Project-owned config 不得提交非占位 credential。
- 个人 token 通过本机环境变量或 secret store 配置，不进入 Git tracked files。
- `.codex/config.toml` 保持 ignored。
- 可在未来治理任务中评估 CI secret scanning；本次不引入 dependency、pre-commit
  framework、GitHub Action 或新的安全子系统。
