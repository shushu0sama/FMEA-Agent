# SysML Fact Snapshot Contracts (MVP-1B)

> 规范性契约文档 v1.0 — APPROVED（2026-09-04，Revision 2 + 最终 Review 澄清 A–D）
> 代码 schema 为准：`src/fmea_agent/adapters/sysml/contracts.py`

## 1. 目的与定位

`SysMLFactSnapshot` 是 parser/API 事实快照（source-native fact envelope），**不是**规范系统模型（Canonical System Model）。

约束：

- 不依赖 `opensysml` / gRPC / protobuf / 任何 parser runtime；
- 不含 runtime object（严格 JSON-safe）；
- 不包含 FMEA 字段；
- 不包含 Canonical 概念（System/Component/Function/SourceReference）；
- 不提前进行 Canonical Mapping；
- Snapshot 不得生成 Canonical ID（1D Mapping 职责）。

## 2. 设计原则

1. Source-native facts, minimal normalization；
2. Pure project-owned data（stdlib + pydantic v2 即可）；
3. Identity honesty：source identity 语义为 parser-neutral，OpenSysML-specific 事实归 adapter profile；
4. Facts-absence expressible：缺失事实用 `None` 表达，不推断；
5. Diagnostics first-class：partial Snapshot 必须能通过 diagnostics 表达数据不完整的原因；
6. Extensibility without domain churn：metatype / severity / relationship type 为自由字符串；
7. Open-world fact envelope：closed-world 端点校验不下沉到 Snapshot；
8. Parser-neutral contract：extraction scope / traversal / 排序属 adapter policy；
9. Strictly JSON-safe：字段类型即 JSON 类型（pydantic `JsonValue`）。

## 3. 契约模型

全部为 pydantic v2 `BaseModel`，`ConfigDict(extra="forbid")` —— 未知字段被拒绝，防止 runtime-specific data 穿透契约。

### 3.1 SysMLSource — 来源 provenance

| 字段 | 类型 | 必填 | 语义 |
|---|---|---|---|
| `source_type` | `str`（非空） | 必填 | 来源形态。MVP-1 唯一值 `"sysml_file"`；其他值（如 `"sysml_repository"`）延后 |
| `source_path` | `str \| None` | 条件必填 | 文件路径（原样保留）。`source_type=="sysml_file"` 时必填（V6） |
| `source_version` | `str \| None` | 可选 | source/repository revision identity（如 repo commit）。File Mode 无可靠版本时填 `None`，不得从文件内容自动推断 |
| `model_hash` | `str \| None` | 可选 | parser 对当前模型内容提供的内容 hash。OpenSysML 1C 用 `Model.hash` 填充。标识内容，**不是**跨版本 identity |
| `parser` | `str`（非空） | 必填 | 底层解析引擎名（如 `"opensysml"`） |
| `parser_version` | `str \| None` | 可选 | parser client 版本（如 `"0.4.0"`） |
| `runtime_version` | `str \| None` | 可选 | parser 服务版本（如 `"v0.4.3"`） |
| `adapter` | `str`（非空） | 必填 | 产出本快照的 project adapter 名（如 `"open_sysml_file"`） |

`source_version` 与 `model_hash` 语义分离，互不合并。

### 3.2 SysMLElementFact — 元素事实

| 字段 | 类型 | 必填 | 语义 |
|---|---|---|---|
| `source_id` | `str`（非空） | 必填 | **source-native element identity**。契约不验证/解析其格式；snapshot 内唯一（V1） |
| `metatype` | `str`（非空） | 必填 | source metatype 原样保留（如 `package`/`partDef`/`partUsage`/`actionDef`/`actionUsage`）。未知值必须可表示 |
| `name` | `str \| None` | 可选 | 短名 |
| `owner_id` | `str \| None` | 可选 | **owner element 的 source-native identity**。由 adapter 经真实 traversal/parent context 建立（1C policy）；契约不定义任何推导算法 |
| `type_facts` | `SysMLTypeFacts \| None` | 可选（默认 `None`） | typing 事实。`None` 或全 `None` = 未观察到，禁止推断（C4） |
| `properties` | `dict[str, JsonValue]` | 可选（默认 `{}`） | 其余 source facts 原始保留 |

**SysMLTypeFacts**：

| 字段 | 类型 | 语义 |
|---|---|---|
| `declared` | `str \| None` | 声明的类型短名 |
| `resolved_id` | `str \| None` | 解析后的类型 identity |
| `resolved_kind` | `str \| None` | 解析类型的 metatype |

1C 规范化规则：空串 `declared` → `None`；三项全 `None` → 整体置 `type_facts=None`。

### 3.3 SysMLRelationshipFact — 关系事实

| 字段 | 类型 | 必填 | 语义 |
|---|---|---|---|
| `type` | `str`（非空） | 必填 | 关系类型原样保留（MVP-1 观察到 `"typing"`）；未知值必须可表示 |
| `source_id` | `str`（非空） | 必填 | 源元素 source-native identity，**必须指向本 Snapshot 中的元素**（V2） |
| `target_id` | `str`（非空） | 必填 | **target element 的 source-native identity**。open-world：允许指向 Snapshot 外部 identity |
| `properties` | `dict[str, JsonValue]` | 可选（默认 `{}`） | 原始附加事实 |

### 3.4 SysMLDiagnostic — 诊断

**Project-owned normalized diagnostic envelope**（不定义为"只能来自 OpenSysML parser"）：

| 字段 | 类型 | 必填 | 语义 |
|---|---|---|---|
| `severity` | `str`（非空） | 必填 | 观察到 `"error"`；其他值原样保留 |
| `message` | `str`（非空） | 必填 | 诊断消息；1:1 保留，不改写 |
| `file` | `str \| None` | 可选 | 诊断所在文件 |
| `start_line` / `start_column` / `end_line` / `end_column` | `int \| None` | 可选 | locator |
| `span` | `JsonValue \| None` | 可选 | span 的 JSON-safe 表示 |

语义要求：

1. parser diagnostics 必须忠实保留；
2. adapter 发现明确的 unsupported / incomplete extraction 时，也允许产生 `SysMLDiagnostic`（adapter-origin）；
3. 本轮不含 category/origin 等字段；
4. 不静默修复 parser fact；
5. partial Snapshot 应通过 diagnostics 表达数据不完整的原因。

### 3.5 SysMLFactSnapshot — 快照

| 字段 | 类型 | 必填 | 语义 |
|---|---|---|---|
| `source` | `SysMLSource` | 必填 | 来源 provenance |
| `elements` | `list[SysMLElementFact]` | 可选（默认 `[]`） | Adapter 按 documented extraction scope 产出的 source element facts |
| `relationships` | `list[SysMLRelationshipFact]` | 可选（默认 `[]`） | 显式关系事实 |
| `diagnostics` | `list[SysMLDiagnostic]` | 可选（默认 `[]`） | 全部诊断；永不静默丢弃 |
| `load_status` | `Literal["ok", "partial"]` | 必填 | `"ok"` = 无 error 诊断；`"partial"` = Snapshot 已产生但事实可能不完整（parse error 或其他显式 incomplete-extraction 原因）。仅强制单向蕴含（V5） |

## 4. Identity Semantics（parser-neutral）

- `source_id` = source-native element identity（非空字符串，snapshot 内唯一）。契约**不验证、不解析其格式**（不要求 FQN 形状）。
- `owner_id` = owner element 的 source-native identity；由 adapter 经真实 traversal/parent context 建立；契约不定义字符串推导算法。
- relationship `target_id` = target element 的 source-native identity；open-world。
- Snapshot 不得生成 Canonical ID；1D Mapping 自铸 canonical id，并把 source identity 保留至 `SourceReference.source_element_id`。

**当前 OpenSysML evidence（1C Adapter Profile，非永久契约语义）**：

- OpenSysML `Symbol.id` 为 name-derived FQN（如 `PerformProbe::hydraulicPump::motor`）— CONFIRMED_RUNTIME；
- rename/move 改变 id（官方文档："A rename is a delete plus a create"）— CONFIRMED_SOURCE；
- 因此 OpenSysML source identity 不声称跨版本稳定（C3）。未来其他 SysML Adapter 的 identity 语义由其自身 profile 声明，不修改本契约。

## 5. Relationship Semantics

- `type` 自由字符串；MVP-1 观察到 `"typing"`。Mapping 不认识的 kind 按 unsupported 处理。
- `source_id` 必须在本 Snapshot 内可解析；`target_id` open-world（external/imported identity 允许）。**closed-world endpoint validation 属于 Canonical Model 层，不下沉到 Snapshot**。
- containment 由 `owner_id` 承载，不物化为 relationship。
- typing relationship 与元素 `type_facts.resolved_id` 并存时不得矛盾。

## 6. Serialization

- pydantic v2；`model_dump_json()` / `model_validate_json()` 往返语义相等（`==`）。
- `properties` / `span` 以 `JsonValue` 类型化，Schema 层拒绝任意 runtime object；无自定义 encoder/decoder。
- 不承诺 byte-identical dump（排序属 adapter policy；canonical deterministic serialization 延后）。
- 无新依赖（`JsonValue` 为 pydantic v2 自带）。

## 7. Validation Rules

| 编号 | 规则 | 强制方式 |
|---|---|---|
| V1 | `source_id` 非空且 snapshot 内唯一 | model_validator |
| V2 | relationship `source_id` 必须指向 `elements` 中已存在元素；`target_id` 不校验（open-world） | model_validator |
| V3 | `owner_id` 不强制解析。完整 standalone extraction 应尽量可解析（1C 测试覆盖）；partial Snapshot 不得仅因 owner target 缺失而整体 ValidationError | 文档化 invariant + 1C 测试 |
| V4 | typing relationship 与 `type_facts.resolved_id` 并存时不得矛盾 | 文档化 invariant |
| V5 | `load_status` 为 `Literal["ok","partial"]`；仅强制 `"ok"` ⇒ 不得存在 `severity=="error"` 诊断。`"partial"` 无 iff 约束 | model_validator |
| V6 | `source_type=="sysml_file"` ⇒ `source_path` 非空 | model_validator |
| V7 | `metatype`/`severity`/relationship `type` 自由字符串——未知值合法、不得拒绝 | 设计约束 |
| V8 | `properties`/`span` 类型即 JSON 类型；runtime object 被 Schema 拒绝 | 类型系统 + 测试 |
| V9 | 所有模型 `extra="forbid"`——未知字段 → ValidationError | 类型系统 + 测试 |
| V10 | 必填字符串非空（`min_length=1`）：source_type/parser/adapter、source_id/metatype、type/source_id/target_id、severity/message | 类型系统 + 测试 |

## 8. OpenSysML Adapter Profile（1C 预定，供参考）

以下属 MVP-1C `OpenSysMLFileAdapter` extraction policy，**不属于本 parser-neutral 契约**：

- dependency pin：`opensysml==0.4.0`（PyPI）+ `sysml-grpc v0.4.3` windows-amd64（SHA-256 见 Spike 报告）；
- 单文件子集：用户文件 import 不支持，unresolved import 产出 error 诊断 + `load_status="partial"`；
- `Symbol.children` 是方法（非属性）；
- owner_id 经真实 traversal/parent context 建立（禁止 FQN 前缀字符串推导）；
- RootNamespace 排除、元素排序、partial extraction 触发条件由 1C 明确；
- performed ActionUsage typing facts 缺失：`type_facts=None`，不推断。

## 9. C1–C4 覆盖

| Condition | 契约落实点 |
|---|---|
| C1 single-file subset | unresolved import ⇒ error 诊断 + `load_status="partial"` 显式表达；adapter 禁止静默降级（Diagnostic Semantics） |
| C2 dependency pin | `parser_version` + `runtime_version` 独立字段（1C contract test 断言）；`model_hash` 与 `source_version` 语义分离 |
| C3 identity 语义 | `source_id` 为 source-native identity；OpenSysML rename⇒新 identity 为 adapter profile 证据；Snapshot 不铸 Canonical ID |
| C4 performed action | `type_facts` 可选 + absence 语义（absence ≠ 无类型）；禁止推断；Mapping 按 UNKNOWN/NEEDS_RESEARCH |

## 10. Out of Scope

- OpenSysMLFileAdapter（1C）；
- Canonical Mapping（1D）；
- 异常边界（`SysMLLoadError` 等，1C）；
- Repository API / 多文件 import；
- FMEA / Canonical 字段、SourceReference（canonical 层）。
