# 方向纠正与真实MCP基线

日期2026-10-29。用户明确：Skill目标是指导Agent通过竞品图复刻MCP完成业务任务。

## 本次纠正

此前把只读接手作为唯一MVP，错误地拦截了提供产品图和竞品图的新任务；又把离线替身/预设配置变成主线。
当前0.1.0-mvp.2已改为新任务与已有任务分别路由：新任务由prepare_run产生run_id；只有明确查询旧任务却缺身份时才询问身份。
入口增加输入、事实来源、逐图结构化增量、准备/预检、费用授权、执行查询、视觉验收及分阶段恢复方法。
独立替身和guard仅用于离线行为评测，不是Skill用户必须安装的组件。不继续要求用户配置新预设。
未完成的收费、视觉和恢复行为验收仍是未验证，方向纠正不等于验收放行。

## 实际调用结果

当前Codex的真实ecommerce-image-replicator MCP连接执行了inspect_inputs、prepare_run和preflight_run。
这是主开发Agent的真实工具证据，不冒充DSH模型完成同一流程的证据。

- 输入：用户工作区12张参考图、1张产品照片；仅看图并选中参考01做本地准备小样本，其余图未声称完成逐图分析。
- 核实：照片支持橙子花纹及浅米/橙/绿配色；参考图的抗菌等级、数量、规格和性能文案缺产品依据，保留为待确认。
- 补齐：在本次测试目录新增事实/授权brief、结构化design.json和12项prompts，仅第01项提供有图像依据的外观/主题增量。
- 契约：正式安装的Delta/ProductContext模型解析通过，prompts整组长度12；texts/scene保持null，没有空文案或占位场景绕过分析。
- inspect返回真实image_id；prepare只选参考01，返回run_id如下。
- preflight返回provider_requests=0、ready_for_generation=false；text/visual均analysis_required且attempts=0；copy_status=pending_text_analysis。
- 没有execute、reconcile、供应商分析、绘图或vision调用；没有成品，不能称视觉验收通过。

```text
<PRIVATE_RUN_ID>
```

本run是明确标记不可收费执行的准备/预检草稿，不交给Agent自动execute。
未知事实和文案核实后，按真实新输入准备正式任务，不改数据库、伪造缓存或通过反复execute推进旧草稿。
证据在`.cache/real-mcp-mvp/preflight.json`和测试工作区brief/prompts内，不将用户图片或业务快照纳入发行包。
用户新增references/products须保留，不能把整个.cache测试工作区当作本次生成物递归清理。

## DSH历史试运行补充

修正版0.1.0-mvp.1的新上下文试运行实际加载skill，最终要求提供run_id，未继续扫描目录。
轨迹还显示一次list_agents，故不能称其满足此前仅skill/get_run的严格受控工具范围；亦未完成三次独立复验。
之后用户在旧会话补充素材路径，模型沿旧上下文调用正式inspect/get_run并搜索任务；已停止该旧轮次，不能计为新任务基线通过。
这些记录保留为失败/有限证据，不作为当前0.1.0-mvp.2的放行结果。
