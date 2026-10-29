# 异常定位与恢复：出错时只读对应行

先检查工具 isError 及业务 status/jobs，不能只因返回 JSON 就报成功。get_run 只读本地，不主动查供应商。
用返回字段定位，不要求操作者反复带 Agent 核对：记录 run_id、image_id、实际0基index、phase/error_code、kind/attempts、receipt及已有恢复关联。

## 诊断 → 参数/文件位置 → 最小修复

| 返回的实际诊断 | 锚定位置与直接动作 |
|---|---|
| 调用参数的 ValidationError/字段路径 | 修该工具参数路径的类型、枚举、必填项或互斥项；工具未成功创建身份时不要当成已冻结 |
| inspect/prepare 的 ToolError 只给 ValueError/ValidationError 类型 | 一次对照已知路径、整组长度与schema；无具体正文就报告证据缺口，不能猜唯一原因或反复裁图 |
| copy_input_conflict | 对应图完整 delta 的 texts 与有效 text_replacements 二选一，同时核对 defaults 继承 |
| copy_replacements_overlap | 用 replacement_indexes/原规则定位重复或互含的 old，改为本图语义明确且不重叠的规则；不只删必要改词 |
| copy_replacements_chain | 修命中规则的 new，确保不再包含任何有效 old；不靠调整顺序重试 |
| copy_replacement_unmatched | 读取本图 transcription，按0基 replacement_indexes修正实际 old或删不适用规则，保留其它更正 |
| analysis_schema_validation_failed | 看 kind 与 schema_errors.path/type；这是分析结果字段/框错误，不是scene构图不受支持的证据 |
| analysis_json_validation_failed / analysis_identity_validation_failed | 定位失败kind及次数；不改真实image_id迎合错误结果，不手工伪造成功缓存 |
| design_validation_failed / resolve_design_failed | 对照 effective_delta、facts、禁用claim、最终文字和主题字段，只修被拒内容，不放宽构图边界 |
| preprocess_failed / input_preflight / local_preflight_failed | 冻结图的路径/hash/读取/预处理前提；恢复合法文件/访问条件，不改hash或换scene |
| analysis_http_failure / LLMHTTPFailure | 保存http_status/diagnostic_id；400/401/403/404/413/415/422为终态，交操作者修确定原因 |
| analysis_provider_request_failed / analysis_retry_exhausted / invalid_analysis_cache | preflight 查失败kind、retry_available/blocked及更具体failure_code，再按下表选恢复；不重开成功kind |
| analysis_response_storage_failed / PermissionError / StartupError / sqlite3.OperationalError | 指向存储/权限/环境；操作者处理明确对象，不删库/锁、全盘放权或改提示词 |
| phase=provider_initialization | 网络客户端/代理/CA等初始化问题；交操作者，不凭ValueError猜唯一根因 |
| generate_failed / SubmissionUnknown / 查询下载错误 | 先看receipt/task_id/result，未知提交不重提；按下表复用原操作 |
| provider_canvas_aspect_mismatch / CanvasMismatch | postprocess的actual/requested画布比例偏差>1%；保留raw与尺寸，不能强拉伸 |
| downloaded_receipt_required / image_operation_missing | 本地恢复缺receipt/操作前提，核对原index和下载状态，不用外部raw补造 |
| local_file_missing / local_permission_denied | 指向raw/冻结快照的本地文件或权限，交操作者恢复，不自动下载绕过 |
| artifact_hash_mismatch / frozen_reference_hash_mismatch / stored_geometry_conflict | 产物/原图/几何完整性冲突；不覆盖或改hash，保存证据交操作者 |
| record_review 的报告hash/检查项拒绝 | 重新取本run的get_run/get_design原值，定位report对应字段或缺失/重复check ID；若只是填错元数据，只修报告后重报，不改产物、plan、原图或重绘。实际文件哈希不符仍按上一行处理 |
| RecoveryRejected / LockException / active execution | 选择、状态、request_id或并发前提不符；读安全消息与原状态，等待或改合法参数，不删锁 |
| review_required / review_error | 已生成但待验收，可标待办先交付；业务需要补验才看相关图并record_review，不因此重绘、不强制整套重写验收 |

## 按已有状态选择修复入口

- 尚未冻结的参数/文件拒绝：修对应调用/输入，再调用被拒的准备步骤。已经返回run_id后，磁盘修改不会更新旧run；不能靠再次prepare重开失败任务。
- retry_available：原因已排除且授权仍覆盖时沿原run使用剩余次数，不开scope。MCP的有限分析重试由它管理，不重置或叠加Agent重试循环。
- 无任何绘图receipt、generation_status=blocked、phase为analysis/copy_preflight/resolve_design/design_preflight：prepare_analysis_recovery只选失败图。copy修正通常复用成功分析；retry_kinds只重开失败text/visual（scene对应visual）。
- 终态HTTP：操作者修确定原因后才显式allow_terminal_http_retry=true，不原样循环。
- 已有recovery_run_id：跟随子run，在子run诊断，不回父run开平行分支。
- unknown/submitting：原请求可能受理；task_id归属核实后，以原run返回的实际0基index做reconcile_submission，不新prepare/POST。
- pending/success或下载失败：原run复用task_id/result继续，恢复execute仍须在授权内，不换模型重绘。
- failed/exhausted绘图receipt：交操作者核对，不冒用分析恢复、删receipt或承诺自动重开。
- downloaded、本地raw保留、v2后处理失败：recover_postprocess(原run_id,image_ids)，无网络/供应商调用；保留recovered/generated_preserved，逐图报告rejected。
- 缺raw、>1%比例异常、artifact/reference hash或几何冲突：保留现场交操作者，不用外部raw、强拉伸、改hash或直接下载绕过。
- downloaded+generated但视觉不合格：prepare_revision(parent_run_id,updates)只选失败图，保留父图与谱系额度；子run授权执行并复验。

分析恢复使用稳定request_id和相同updates，响应丢失时同参数重放，不换ID碰运气。preflight_failed不建子run；要完整转录/delta就另调preflight。
not_submitted只表示未观察到绘图提交，不证明没有分析费用。已有accepted可转述服务记录；没看图不能声称本次独立验收。
恢复/修订updates是完整逐图delta替换，不是patch：复制原有效delta后改命中字段，保留其余产品/文案/主题及默认继承。
历史error与有效成功result共存时按schema/ID核验复用成功缓存；partial只恢复失败图并列空缺。
本地后处理成功后直接核对精确两维并重新验收，不为“收尾”execute其它图。needs_revision不重标旧图通过，uncertain仍待验收。
同一明确诊断做一次针对性修复后仍同因失败且无新证据，就停受影响分支、报告实际字段和缺口；不靠多轮交互式指挥、扫源码/DB/私有配置或换工具绕过。
