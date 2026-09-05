# 2026-09-05 — Credential Exposure Remediation

Status: REPOSITORY_REMEDIATED / USER_CONFIRMED_REVOKED_OR_ROTATED

> 2026-09-05 最终独立 C-1 复审：`ACCEPTED`。
> [复审证据](../G0A_R_FINAL_C1_REVIEW.md)不改变下方 provider 状态的用户确认边界。

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
- Provider-side revocation/rotation：USER_CONFIRMED_REVOKED_OR_ROTATED。
- History rewrite：NOT_PERFORMED。

用户已于 2026-09-05 确认：历史暴露 credential 已在 provider 侧完成撤销或轮换，
旧 credential 已被失效处理。本记录仅记载用户确认；Codex 未验证 credential，亦未通过
API 或 provider 独立验证该状态。

## 历史处理决定

本次不执行 `git filter-repo`、`git filter-branch`、BFG、force push、tag rewrite
或任何 commit SHA rewrite。Provider 侧撤销 / 轮换用于使已暴露 credential 失效；
未经独立治理批准重写历史会破坏 MVP-0/MVP-1 release tag、Records 与审计证据中
已有的 commit SHA 锚点。

基于用户确认、current tracked tree 已清理，且历史重写会破坏已有 release / audit SHA
锚点，本次保持 `History rewrite: NOT_PERFORMED`。该决定不表示 Codex、API 或 provider
已独立验证撤销或轮换状态。

## 后续预防

- Project-owned config 不得提交非占位 credential。
- 个人 token 通过本机环境变量或 secret store 配置，不进入 Git tracked files。
- `.codex/config.toml` 保持 ignored。
- 可在未来治理任务中评估 CI secret scanning；本次不引入 dependency、pre-commit
  framework、GitHub Action 或新的安全子系统。
