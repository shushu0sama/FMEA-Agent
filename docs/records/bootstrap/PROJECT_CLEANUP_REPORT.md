# 项目清理报告

## 来源

原始归档： `FMEA Agent 2026.9.3.zip`

## 清理操作

1. 将 Bootstrap Pack 项目文件提升到实际仓库根目录：
   - `CLAUDE.md`
   - `PROGRESS.md`
   - `.claude/rules/`
   - `docs/`
2. 移除外层 `FMEA_Agent_Bootstrap_Pack_v0.1/` 包装目录。
3. 移除第二层嵌套的重复目录树 `FMEA_Agent_Bootstrap_Pack_v0.1/FMEA_Agent_Bootstrap_Pack_v0.1/`。
4. 移除根目录中的重复副本：
   - `FMEA_AGENT_FOUNDATION_GUIDE_UPDATED_v0.2.md`
   - `FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE_UPDATED_v0.2.md`
   它们的 SHA-256 哈希与 `docs/foundation/` 下的规范文件一致。
5. 移除仅用于打包的文件：
   - `MANIFEST.json`
   - `README_BOOTSTRAP_PACK.md`
   这些文件由面向项目的根目录 `README.md` 替代。
6. 未复制 `.claude/settings.local.json`，因为其中包含明文认证 token 和宽松的本地执行设置。
7. 新增 `.gitignore`，防止误提交本地 Claude 设置、秘密信息、缓存、环境和运行时输出。

## 规范文档位置

```text
docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md
docs/foundation/FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md
docs/domain/FMEA_PROFILE_V1.md
docs/domain/FMEA_GLOSSARY.md
docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md
docs/evaluation/BENCHMARK_SPEC.md
docs/research/DEPENDENCY_INVENTORY.md
docs/specs/MVP_0_RUNNABLE_AGENT_SKELETON.md
docs/plans/MVP_0_IMPLEMENTATION_PLAN.md
```

## 当前开发状态

本次清理未新增源代码实现。项目仍处于规划中的 Bootstrap/MVP-0 起点。
