# hydraulicPump 演示设计说明

本文件为演示派生资料，仅从固定 SysML 教学夹具提取结构与动作。
它不是真实航空产品或经工程验证的液压系统设计，不构成工程批准或独立证据。

## 来源与已知结构

来源：`tests/fixtures/sysml/models/typed_inside_probe.sysml` 的原样副本 `system.sysml`。
SHA-256：`fb1637c8ae7ec620d77a10f65efa7d4e5a352523de8b110046c0b3043447f6e5`。
以下 FACT 仅指模型已表达的事实，不表示产品设计已审核。

| 类别 | 名称 | CSM ID | 归属 CSM ID | source_element_id |
|---|---|---|---|---|
| System | hydraulicPump | system-1 | — | TypedInsideProbe::hydraulicPump |
| Component | motor | component-1 | system-1 | TypedInsideProbe::hydraulicPump::motor |
| Function | pumpSpin | function-1 | system-1 | TypedInsideProbe::hydraulicPump::pumpSpin |
| Function | spin | function-2 | component-1 | TypedInsideProbe::hydraulicPump::motor::spin |

## 演示分析范围

首个目标：`motor`（`component-1`）/ `spin`（`function-2`）。
根动作 `pumpSpin` 在 CSM 中保留，但未纳入分析：当前 workflow 只分析组件功能。
这只是后续分析的范围声明；本资料包未执行失效生成。

## 未知信息

- 额定电压：UNKNOWN（模型未表达，不填数值或演示假设）。
- 转速：UNKNOWN（模型未表达，不填数值或演示假设）。
- 材料：UNKNOWN（模型未表达，不填数值或演示假设）。
- 数量：UNKNOWN（模型未表达，不填数值或演示假设）。
- 运行环境：UNKNOWN（模型未表达，不填数值或演示假设）。
- 运行阶段：UNKNOWN（模型未表达，不填数值或演示假设）。
- 工作循环：UNKNOWN（模型未表达，不填数值或演示假设）。
- 主要负载：UNKNOWN（模型未表达，不填数值或演示假设）。

BOM 只列实际映射的 Component；系统根以 parent_id 关联，不作为采购物料行。
quantity 留空、unit 为 UNKNOWN；一条部件声明不能推导物料数量。
类型定义不直接变成 Component，component_type 保持未知；映射通知保存在 manifest。

## 使用限制

不提供原始失效答案、已有控制、S/O/D/AP 或标准符合性结论。
Neo4j 历史案例与本模型独立；派生 BOM/设计说明不是工程正确率的独立 gold。
工况需在后续交互阶段补充或明确保留 UNKNOWN。
