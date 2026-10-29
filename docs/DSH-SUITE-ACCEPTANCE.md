# DSH 全套真实任务验收

日期：2026-10-29。首要 Host：DSH Desktop 0.2.1-rc.2，会话模型显示为 `claude-sonnet-5-5`。mvp.2在准备阶段停止；mvp.3及mvp.4旧草稿接续失败；mvp.4新输入已完成12图首轮生成。本记录不表示全套最终验收通过。

## 范围和来源

- 用户要求隔离工作区中的 DSH 自动触发 Skill，经现有竞品图复刻 MCP 完成全套并查看效果。本次已明确授权整套所需真实分析和绘图，覆盖此前的无收费限制。
- 工作区：`E:/agent-skills-workspace/ecommerce-image-replicator-skill/.cache/dsh-mvp-workspace`。
- 输入：`references/detailpages/` 中 12 张参考图，`products/my-product.png` 一张用户产品图。原图必须保留。
- Skill：`0.1.0-mvp.2`；源码与隔离部署副本 SHA256 均为 `1EFB54AD099F420AAD682DCBAEEBCDB903D9011509BAF766017091D831B6AF28`。
- DSH 新会话实际标题为“竞品详情图整套复刻”；起始请求未点名 Skill。

## mvp.2历史证据

| 检查点 | 观察 | 结论 |
|---|---|---|
| 自动选择 | UI 轨迹出现 `skill {"name":"ecommerce-image-replicator"}`，正文开头为当前完整业务流程 | 本次自然语言正例通过；不是多次稳定性结论 |
| 工作区 | 轨迹 runtime context 的 cwd 指向隔离业务工作区 | 已核对 |
| 输入实图 | `read_image` 读取产品图及参考 01–12 | 已观察实际调用 |
| 工具契约 | 读取 `replicator://input-contract`；真实 `inspect_inputs` 返回 12 个 image_id | 已核对；inspect 不代表冻结完成 |
| 事实确认 | 用户分两次确认规格、宣称和名称；均已转交 DSH | 已记录来源，等待逐图增量核验 |
| 旧草稿 | 归档至工作区 `archive/2026-10-29-single-image-precheck/` | 不直接执行旧单图预检 run |
| 冻结、预检、执行 | 尚未取得本次全套 run 的成功返回 | 待验证 |
| 成图、尺寸、视觉验收 | 尚无本次成图 | 待验证 |

DSH 对话模型曾一次自动重试，UI 原因为 `Connection error.`；之后恢复并继续。它不构成绘图请求失败证据。
最后观测运行38分07秒仍未prepare；保存轨迹后停止了这个准备轮次，未观察到本次全套execute/绘图提交。后续效率改进与复验见[流程效率回归](../evaluations/FLOW-PERFORMANCE.md)，保留原图、事实、增量草稿和历史单图预检身份。

输入准备中的自检与开发者干预：DSH 首次生成的第 12 项同时使用 `25x25cm` 与 `25cm` 字面规则，存在子串重叠；第 08 项还写入待核实是否实际存在的包装参数规则。后续 UI 轨迹确认，DSH 在开发者反馈进入上下文前已自行指出第 12 项重叠并删除该项 `25cm` 规则。主开发 Agent 同期提交具体位置及第 08 项匹配核验反馈，要求保留完整增量，反馈保存在 `developer-contract-feedback.txt`。删除规则后的两条尺寸箭头仍须通过完整文案及实图检查；本轮不能声称完全无人干预，也不能把 DSH 已自行发现的问题错误记为它从未自检。

## mvp.4真实全套首轮

- 入口源码与隔离副本SHA256：`BC4C9B5D558F4537C063FA441C95FF9665CA100D6EA80FC508E34CBC60A8253D`。会话实际标题“请把 E:/agent-skills-workspace/ecommer”；自然语言请求未点名Skill，轨迹自动加载当前完整正文。
- 模型/Host配置未变；仅归档Agent旧草稿和裁图，用户13张原图与MCP状态保留，逐图SHA256核对未变。事实及全套授权一次给齐。
- 当前run：`<PRIVATE_RUN_ID>`，thread：`<PRIVATE_THREAD_ID>`。
- `image_model=gpt-image-2.5-flare`、`review_mode=vision`、`concurrency=4`；实际12图全部选择。公共属性6项，显式texts/scene/换词规则0项。
- 实际prepare→preflight→execute一次，scheduled后查询原run；未因跨进程get_run显示interrupted_or_other_process而重新提交。该状态在DSH后台执行期间出现，随后各图继续推进，不是失败证明。
- 请求10:53:59.920；约10–11分钟进入prepare；14分49秒内观察到execute受理；11:19:07.717观察到12图downloaded。计时为观察界限，完整性能说明见[流程效率回归](../evaluations/FLOW-PERFORMANCE.md)。
- 首轮12个artifact的实际两维均精确匹配原参考，文件SHA256均匹配MCP记录。该次服务端vision为9张accepted/3张review_required，不等于全套独立实图通过。

开发者独立实际查看全部12张输出：01/02/03/04/06/07/10/11未见实质问题；05和09残留青苹果身份；05把原检测报告日期、正文和表格/结论重画改动；08包装出现无本产品确认依据的50次水洗宣称；12注意事项错字未纠正。10保留双手用抹布握锅两侧的动作，04本产品230g/m²与对照30g/m²角色正确。

DSH自行读完12图后识别05/09身份问题。11:27开发者一次汇总反馈05/08/09/12实际缺陷，属于成图验收反馈，未以多轮交互指挥参数校验。本轮不能声称全程无人干预。

DSH沿父任务调用prepare_revision，仅选择05/08/09/12；子run为`<PRIVATE_RUN_ID>`。子任务四图继承完整六项产品属性和既定主题，execute一次，没有重做其余8图。11:30:30.526已观察到四图downloaded。

修订后独立看图：08删除了无来源水洗次数宣称、09改成用户产品身份、12纠正了远离火源高温，均未见实质问题；05标签虽改，嵌入报告仍失真（日期出现2004年、编号/规格/结论不等同原报告）。DSH修订instruction还自行写了AAAAAA级，未能保留原报告。服务端vision对此给accepted，说明自动裁判存在漏判，不能用其作为报告内容真实性证明。

11:32开发者反馈该页一次定向修订仍失败，要求停止进一步收费重绘、如实记录未通过并完成其余11图交付。此为有界修订后的具体质量结论，不靠继续加长提示词循环生成。最终报告页不能交作可用检测证明；当前MCP路径尚未证明能保真保留嵌入文档。未修改MCP源码或使用外部绘图/手工成图绕过。

最新12图的实际宽高与artifact SHA256再次全通过；这只证明文件/后处理正确。独立实图判断为11张无实质问题、05未通过；MCP最终显式验收写入结果另行核对。最新清单与预览为latest-run.json、latest-file-checks.json、latest-contact-sheet.jpg，05在预览中标为FAILED。父子16个artifact均保留。

真实收尾异常：DSH请求67对02的record_review返回error（轨迹摘要没有展开具体异常正文）；请求68自行说明“刚才误写参考哈希，纠正后重报”，随后同图写入成功。独立get_run确认02的reviewer=agent_or_operator、accepted，三个哈希与实际记录相符；开发者没有就此提供修复参数。该证据只覆盖一次验收报告元数据纠错，不能泛化为LangGraph分析/文案参数异常恢复全部通过。轨迹clean-mvp4-review-trace.txt保留失败及更正，错误码没有观察到就不补造。

最终12份显式验收已落盘：父run保留01/02/03/04/06/07/10/11共8张accepted，子run08/09/12共3张accepted、05为needs_revision（elements/copy/identity/change_scope为fail）。全部实际三哈希及完整check ID与对应plan匹配，证据final-mvp4-review-bindings.json。它们不代表用户已完成业务终验。

旧轮累计至少1小时13分仍在生成收尾，首轮约25分钟已经全部落盘；后半段包含重复读图、定位设计、12次显式写入的长载荷/全量返回、上下文压缩及最后再算尺寸。不能把这些都归因于MCP参数校验或供应商速度。按用户最新轻量目标，在持久记录完成后停止旧轮冗余收尾，未删除产物或取消未完成的供应商任务。旧F01保留原标准下的未达标，不按新标准追溯改判。

首轮证据：`.cache/dsh-suite-acceptance/first-pass-run.json`、`first-pass-file-checks.json`、`first-pass-contact-sheet.jpg`、`independent-visual-findings.md`、`first-pass-visual-feedback.txt`和`clean-mvp4-execution-trace.txt`。输出均在原业务工作区artifacts中保留，没有覆盖原图或成功图。

## 用户确认的产品信息

来源为本次用户明确回复，不把参考图片自行提升为产品事实：

- 产品名称：橙子10A抗菌周抛抹布；照片支持橙子/橙切片、绿叶、小花和浅米底的外观。
- 10A 抗菌；用户确认参考图检测报告与本产品一致，可以沿用。
- 克重 230g/㎡，单片 30×30cm，30片/卷，超细纤维，具有隔热功能。
- 用户进一步确认周抛/可用一周、干湿两用、吸水吸油、断点手撕、隔热防烫和日常清洁用途均适用，名称可用。
- 必须替换参考中的 180g/㎡、25×25cm、20片/卷以及青苹果产品身份；艺术媒介、主要构图和关键互动按参考保留。

## 证据与边界

本地生成证据在 `.cache/dsh-suite-acceptance/`：自然语言请求、实际 UI 轨迹、用户事实转交记录、输入尺寸及 SHA256 清单。它们不进入 Skill 发行包。

全部参考宽 790 像素，高度按 01–12 顺序为 1357、857、1079、1517、1334、1337、1317、1300、1188、1300、1188、1301。尺寸核验须逐图匹配两维。

不把本次正例扩展为全部 PRD 场景或恢复路径通过；未提交、推送、合并或发布代码，未变更 Host 配置。后续记录以 MCP 实际 run、receipt 和产物为准。
