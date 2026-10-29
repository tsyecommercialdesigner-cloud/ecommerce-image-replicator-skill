---
name: ecommerce-image-replicator
description: 通过 ecommerce-image-replicator MCP，依据用户产品照片与事实复刻竞品参考图，指导输入准备、逐图增量、授权执行、验收和失败恢复。用户提供产品图与竞品图要求复刻，或要求接手、查询、修订已有复刻任务时使用；不用于通用海报创作、独立供应商 API 调用或 MCP 安装维护。
metadata:
  version: 0.1.0-mvp.11
  mcp-baseline: 0.1.7
---

# 轻量完成竞品图复刻

Agent负责输入、调度、文件完整性和清楚交付；MCP的LangGraph负责转录、场景分析、校验、生成及后处理；用户负责最终业务验收。默认平衡时效、推理成本和业务可用性，接受无损用途的视觉偏差，不追求像素一致或强制Agent精审全套。

## 快速路由

- 新任务不索要旧run_id；已有run_id先get_run，不扫描缓存/数据库猜身份。旧thread_id按实际schema兼容或import_run绑定已有任务，不换workspace。
- **只整理交付/查看现成效果：** get_run→按image_id合并当前版本→一批文件hash核验→现有图片链接与已知待办，直接交用户验收。默认不复制图片、打包、新建HTML/长报告；用户明确要文件包才做。复用验收/尺寸记录，不再审图、比较父子优劣或裁图考证，不加载Python/读旧brief与参考图。
- 此短路径由当前Agent直接完成，不调用list_agents或查询团队状态。DSH在最终简表写普通Markdown文件链接，目标直接取当前artifact的工作区相对路径，点击即侧栏预览；不写内嵌图片语法或带额外前导斜线的盘符图片URL，不调用present。只批量核验当前选定文件，不扩查历史版本、目录、旧HTML/清单或新增read_image；不复制文件或新建HTML。其它Host使用其已支持的本地文件展示方式。
- 版本选择只用任务记录：accepted子图替换同image_id父图；未通过子图明确列待办、保留父图原状态，不重新评选或冒充通过。缺身份/记录才取缺的字段，不能靠文件名猜。
- 工具名称/schema以当前连接为准；首次连接或能力变化才核对版本、资源`replicator://input-contract`及Prompt `prepare_inputs`。Prompt不是Tool，桥接缺失用实际schema并简述；不扫描安装/Host配置或用收费execute探测。

## 默认短路径

1. **一次收齐输入。** inspect_inputs取得真实image_id与自然排序；看产品图及参考概览/代表图，合并询问真正缺少的产品事实和授权，直接复用已有回复。照片只证明外观，参考不自动成为本产品参数；普通标题/配色不逐项审批。
2. **一次写最小增量。** brief记录事实来源/范围，design.json的facts及defaults.design放公共属性/品牌文字色；组prompts保持整组长度，各项只写差异，无差异用{}。以事实适配为默认，texts/scene/text_replacements可省略，交MCP逐图分析，不手抄、OCR、裁小字或重写校验器；texts=[]是最终空文案，不能用来跳分析。
   需要字段合并、用户逐字要求或实际copy诊断时才读[references/input-deltas.md](references/input-deltas.md)。不预载精确换词指南，不把Agent旧草稿的猜测规则当用户要求；已指定的必要更正不能清空逃避校验。
3. **立即冻结预检。** 事实/输入/范围齐就prepare_run，保存身份与选项，再preflight_run。不要先探测Python/Pillow、另算全组尺寸或制作额外计划文档；analysis_required/pending_text_analysis是正常待办，授权充分且无已知阻塞就让MCP分析。
4. **一次执行，少量查询。** 分析/绘图/vision可能收费，已有授权覆盖就继续，不重复审批或强制小样本；只授权预检则不execute。execute_run一次，scheduled只报受理；按阶段时长/返回建议等待，在有用检查点get_run，无变化延长间隔，连续三次无变化就保留身份等待或交接。不忙循环execute或为每图另建等待任务；模型家族用实际schema的flare/sunburst，画布交MCP。
5. **先交付可用结果。** 复用MCP已有验收，新生成可快速抽看1–3张代表/异常图，不作为交付关卡；接手交付走上面的直接路径。已accepted不逐图get_design/record_review，review_required如实列待办。只有用户要求重新审图/精修才扩大，不为抽查另造渲染脚本或付费复检。

## 轻量验收的边界

- 无损业务用途的构图微移、光影/纹理、小装饰、非关键字形和轻微色差接受即可，不自动重绘。关键产品事实冲突、核心表达丢失或实质报告数据失真列明影响；先交付其它结果，需修时才在授权/预算内prepare_revision受影响图。默认不因小偏差阻塞整组。
- **文件完整性不放宽：** 按真实image_id、来源run及当前artifact绑定文件；用现成工具一次批量核对实际SHA256与对应MCP记录，不手抄哈希或扫全局design缓存猜父子归属。实际哈希不符/混图不通过。精确宽高优先用绑定产物的后处理记录，缺失/异常再读尺寸。
- 仅需补验、实际发现问题或用户要求精审时取相关get_design。写record_review仍需实际artifact/design/reference三哈希、全部check ID各一次及一句关键观察；不复述整段标准，不造未观察的pass。已有服务记录可转述，没看过不能声称本次独立逐图验收。
- 按image_id简表交付来源run、当前路径/尺寸、MCP状态、抽查范围和已知待办；区分已生成/已验收/空缺，附现成预览或文件链接供用户最终选择。raw不是成品，downloaded不是accepted。不要为了制作长报告延迟交付。

## 出错才定位、最小修复

参数拒绝看工具字段路径；执行异常看phase/error_code、image_id/index、schema_errors.path/type或replacement_indexes，按[references/diagnostics-and-recovery.md](references/diagnostics-and-recovery.md)对应行处理，不用多轮交互式指挥Agent核对。
- copy问题只修本图规则/默认继承，优先用MCP的transcription，不重抄整组或改scene猜原因；未冻结输入修后重试准备，已冻结用对应恢复入口。
- 无绘图receipt的分析/文案blocked→prepare_analysis_recovery；已有成图需改→prepare_revision；downloaded的本地后处理失败→recover_postprocess原run，不重跑成功图。updates是完整delta，保留其它事实/增量；跟随已有恢复子run，稳定request_id不换参数碰运气。
- unknown/submitting保留原操作，核实task_id归属后reconcile，不新prepare/POST；pending/下载失败复用原任务。报告元数据误填只重取正确值修报告；实际文件完整性冲突保留现场，不改hash。环境/权限或缺事实/授权才交操作者。
同一明确原因自行修一次并复验；同因仍失败且无新证据就停该分支、列具体待办，不循环猜改。保留成功图、缓存和父子身份；不读私有DB/Host配置，不另写绘图客户端，不外发密钥、签名URL或原始供应商响应。

示例：产品图+N张竞品图→一次事实确认、公共defaults+N项差异→prepare/preflight/授权执行→文件批量核验、代表抽查、交付用户验收；接手部分失败run→查原任务，只处理必要失败分支；通用咖啡店海报不使用本技能。
