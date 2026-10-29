# DSH MVP 验收记录

当前交付版本及范围以[mvp.11最终交付与验收记录](MVP11-DELIVERY.md)为准。下方协议、组件和早期模型入口记录保留为历史，不代表最终候选已通过全部场景或已经发布。

日期：2026-10-29，Asia/Shanghai。首要Host为用户指定的DSH；仍禁止真实业务供应商调用。
用户已额外允许DSH对话模型评测的token用量。没有获得提交、推送、合并或发布授权。

## 当前连接与正式安装

- Codex重启后当前连接可见12工具，包含recover_postprocess；replicator://input-contract可读。
- 当前资源指纹：reference-creative-v1、explicit-pre-image-child-v1、downloaded-local-v1、canvas-normalize-v1、opt-in-v1；画布比例容差0.01；proxy_mode=environment，httpx-bracketed-ipv6-v1。
- 当前桥接不提供serverInfo.version，不把资源能力指纹推断为精确版本号。
- D盘正式安装Python发行元数据为0.1.7；使用该解释器和安装模块的独立stdio探针也报告serverInfo.version=0.1.7、12工具/1资源/1Prompt，5个合成任务本地调用通过。
- 独立连接不是当前Codex或DSH连接；当前Prompt桥接入口未暴露，未伪装为已从当前连接读取Prompt。
- 证据：`.cache/current-connection.json`、`.cache/mvp-protocol.json`。

## DSH原生组件集成：通过，范围受限

使用本机已安装DSH 0.2.1-rc.2的Cordis、SkillRegistry、文件系统提供方、ToolRuntime和MCP客户端；未安装依赖、未读写Host私有配置。
在本仓库.cache临时目录加载Skill副本，关闭默认用户根扫描和目录监视。
真实解析元数据并发现完整目录、加载正文、核对modelInvocable/userInvocable；真实DSH工具注册表通过stdio调用离线替身。
合法身份成功与错误身份失败各3次，共6次。首次测试因结果未携带structuredContent而失败，修正测试消费者从text内容解析后通过，未改变业务断言。
这不是自然语言选择或模型行为测试；不能用6次组件调用替代15次MVP对话或96次首版评测。
证据：`.cache/dsh-components.json`。临时组件目录和MCP子进程已清理。

## Headless模型前置检查：阻塞

CLI版本0.2.1-rc.2；使用临时--patch关闭真实工具入口，并由运行时guard仅放行skill和离线get_run。
模型默认路由deepseek-official/deepseek-flash。首次Windows shim拒绝多行命令参数，改用官方stdin入口后进入实际Host。
M04第1次随后在模型请求前报MISSING_CREDENTIAL，未产生业务供应商调用；不是Skill行为通过或行为失败。
不重试相同凭据错误，不复制桌面凭据或绕过Electron专管的desktop profile。
证据：`.cache/dsh-M04-1/`（启动失败）、`.cache/dsh-M04-1-5hhc124i/`（凭据前置失败）。

## Desktop M04第1次：未通过，已停止

测试工作区：本仓库`.cache/dsh-mvp-workspace/`，仅放入本次MVP副本；原有业务会话保留。
桌面已配置模型显示为claude-sonnet-5-5；精确后端模型版本未由UI提供。
输入：“接手这个竞品图复刻任务，帮我查进度。”
原Skill文件SHA256：99be3883334a43e243b139f89661416f6a10ef75cda4c86f113c0bb522a7361c。

实际可见首个工具为“加载技能 ecommerce-image-replicator”，说明该次自然语言选择和加载确实发生。
随后模型读取MCP资源，运行“List workspace root contents”，并进一步运行“Inspect cache and repo root directories”和“Check MCP state directory listing”。
没有先向用户索取缺少的run_id，不满足M04预期；已点击停止并观察到“已停止”。
未观察到execute/绘图/分析/vision调用；没有完整供应商计费账单，不能将观察范围扩写成供应商侧审计结论。
本桌面会话未确认只挂接替身，因此不继续在其中运行带合成run_id的M01/M02/M05。

## 修正与待办

原入口把缺身份处理放在能力发现之后，给模型留下先搜索任务身份的执行路径。
已在0.1.0-mvp.1入口顶部增加任务身份关卡：当前上下文缺run_id时先询问并结束分支，不调用工具或遍历目录寻找身份。
修正版已在核对旧摘要无漂移后同步到隔离工作区；SHA256为d614bbfb2df16764fc2d299dc4ddf2cc6f36b2b66160292aa8f3b934277aaf61。
修正版结构检查、quick_validate和原生组件检查通过；guard的canary拒绝测试确认工具体调用为0。
不在旧会话中续测；后续须新上下文、固定新摘要后重验，保留上述失败。
用户已选择自行准备只连接离线替身的桌面会话；接入清单为evaluations/DSH-SETUP.md，不索取密钥内容。
MVP仍未通过，完整恢复资源、其它Host和首版A01–A32暂不扩展。
