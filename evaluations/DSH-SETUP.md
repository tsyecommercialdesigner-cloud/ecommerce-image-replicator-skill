# 隔离桌面会话接入清单

> 2026-10-29说明：本文件仅保留为可选的离线行为评测接入资料，不是使用Skill或完成真实MCP无收费准备/预检的前置条件。用户已纠正开发方向，当前不再要求先创建该预设。业务主流程见skills/ecommerce-image-replicator/SKILL.md。

状态：待操作者配置。仅使用DSH现有对话模型；禁止真实分析、绘图、vision及供应商查询。
源Skill版本0.1.0-mvp.1；当前SHA256以本机Get-FileHash结果为准，不能复用旧会话缓存。

## 测试工作区

本次已创建的独立目录：

```text
E:\agent-skills-workspace\ecommerce-image-replicator-skill\.cache\dsh-mvp-workspace
```

仅用于本次验收，保留原业务工作区、模型、代理、密钥和正式MCP连接。
工作区`.agents/skills/ecommerce-image-replicator/`已放入修正版Skill副本。
选择新会话，模型固定为本机已配置的同一路由；请告知非秘密的模型名称，不要发送密钥。

## 离线MCP连接

在测试会话所属的独立配置作用域使用以下DSH插件条目；不要替换正式服务条目。
它只暴露get_run；参数为测试run_id，返回三图合成状态；没有execute工具、真实商品、凭据读取或供应商代码。

```yaml
- id: mvp-fixture
  name: '@deepseek-ai/dsh-mcp-client'
  config:
    serverName: mvp_fixture
    transport: stdio
    command: 'D:\MCP\ecommerce-image-replicator-mcp\.venv\Scripts\python.exe'
    args:
      - '-X'
      - utf8
      - '-B'
      - 'E:\agent-skills-workspace\ecommerce-image-replicator-skill\tests\mvp_stub.py'
    cwd: 'E:\agent-skills-workspace\ecommerce-image-replicator-skill\.cache\dsh-mvp-workspace'
    failOnStartupError: true
    reconnect:
      enabled: false
- id: mvp-tool-guard
  name: 'E:\agent-skills-workspace\ecommerce-image-replicator-skill\tests\dsh_mvp_guard.mjs'
```

这是测试配置条目，不是可覆盖原profile的完整文档。桌面配置入口和作用域由操作者决定。
离线连接及guard已在DSH 0.2.1-rc.2原生组件中验证；headless临时overlay也完成插件启动并进入模型凭据检查。
桌面独立作用域的实际生效仍须核对，不能将前两者当作桌面通过。

## 会话放行条件

- 正确来源的Skill可发现，正文为0.1.0-mvp.1，并包含开头的“先过任务身份关卡”。
- 可见实际工具映射`mcp__mvp_fixture__get_run`；guard仅放行该工具和`skill`。
- 其它业务服务不挂接此测试会话；即使存在其它工具，运行时guard也必须生效。
- guard的拒绝测试通过后才运行带身份的M01/M02/M05。原生组件canary检查已确认拒绝时工具体未运行。
- 每个用例新上下文，模型和Skill摘要固定；按MVP验收卡各3次，所有失败保留。

准备完成后通知当前开发会话即可；不要在真实MCP上试用合成身份。
本次测试结束后，仅移除测试拥有的连接/guard/目录；测试证据归档在本仓库.cache，保留原业务状态。
