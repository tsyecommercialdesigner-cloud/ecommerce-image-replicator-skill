# 电商竞品图复刻 Skill 使用手册

版本 `0.1.0-mvp.11`，适配MCP契约 `0.1.7`。纯指令Skill，无Python或Node运行依赖；使用者需已有DSH及可用的ecommerce-image-replicator MCP连接。已验证Windows DSH Desktop 0.2.1-rc.2，界面模型claude-sonnet-5-5，其它Host未由本轮验收。

## 1. 获取与校验

发行入口：[v0.1.0-mvp.11](https://github.com/tsyecommercialdesigner-cloud/ecommerce-image-replicator-skill/releases/tag/v0.1.0-mvp.11)。发布状态以该页及本手册末尾的实际记录为准。使用页面上的完整技能ZIP，不使用自动生成的Source code ZIP替代。

| 附件 | 用途 |
|---|---|
| ecommerce-image-replicator-0.1.0-mvp.11.zip | 三份指令与MIT许可证 |
| manifest.json | 版本、完整来源提交、ZIP及包内各文件的SHA256 |
| SHA256SUMS.txt | 同一发行的全部附件摘要 |
| MANUAL.md / VALIDATION.md | 使用说明及验收范围 |

以下命令适用PowerShell 7，下载需已有GitHub CLI登录或公共下载权限，不在聊天中填写密钥。代码块按顺序在同一PowerShell会话执行。可修改下载目录；项目目录须已存在。

```powershell
$ErrorActionPreference = 'Stop'
$download = 'D:\Downloads\ecommerce-image-replicator-0.1.0-mvp.11'
New-Item -ItemType Directory -Path $download -Force | Out-Null
$repo = 'tsyecommercialdesigner-cloud/ecommerce-image-replicator-skill'
$tag = 'v0.1.0-mvp.11'
# 仅补缺失附件；已有文件仍需下面重新校验，不能沿用旧校验结果。
gh release download $tag --repo $repo --dir $download --skip-existing
if ($LASTEXITCODE -ne 0) { throw '下载失败' }
foreach ($line in Get-Content -LiteralPath (Join-Path $download 'SHA256SUMS.txt')) {
    if ($line -notmatch '^([a-f0-9]{64})  ([A-Za-z0-9_.-]+)$') { throw '摘要清单格式错误' }
    $expected = $Matches[1]; $file = Join-Path $download $Matches[2]
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $expected) { throw "摘要不符：$file；保留现场，移走损坏附件后重新下载" }
}
$manifest = Get-Content -LiteralPath (Join-Path $download 'manifest.json') -Raw | ConvertFrom-Json
if ($manifest.version -ne '0.1.0-mvp.11' -or $manifest.revision -notmatch '^[a-f0-9]{40}$') { throw '版本或来源提交不符' }
$zip = Join-Path $download $manifest.archive.name
if ((Get-FileHash -LiteralPath $zip).Hash -ne $manifest.archive.sha256) { throw 'ZIP摘要不符' }
$unpacked = Join-Path $download 'unpacked'
if (Test-Path -LiteralPath $unpacked) { throw 'unpacked已存在；保留并另选干净解压目录，避免合并旧文件' }
Expand-Archive -LiteralPath $zip -DestinationPath $unpacked
$skill = Join-Path $unpacked 'ecommerce-image-replicator'
$actualFiles = @(Get-ChildItem -LiteralPath $skill -File -Recurse)
if ($actualFiles.Count -ne $manifest.files.Count) { throw '文件数量不符' }
foreach ($item in $manifest.files) {
    if ($item.path -match '(^/|\\|\.\.|:)') { throw '清单含非法相对路径' }
    $file = Join-Path $skill $item.path
    if ((Get-FileHash -LiteralPath $file).Hash -ne $item.sha256) { throw "包内文件不符：$file" }
}
```

期望摘要应来自可信Release页面；从同一未知来源下载文件及摘要不能单独证明来源可信。下载失败或校验不符时先停止，不执行安装。

## 2. 安装与确认来源

默认采用DSH项目级作用域。源码的skills目录、下载目录和Host发现目录各有用途，不互相代用。将已核验目录安装到你选择的业务工作区，已有同名目录时停止并比较差异。

```powershell
$project = (Read-Host '已存在的业务工作区绝对路径').Trim()
if ($project.StartsWith('"') -and $project.EndsWith('"')) { $project = $project.Substring(1, $project.Length - 2) }
if ($project.Contains('"') -or !$project -or ![IO.Path]::IsPathFullyQualified($project) -or !(Test-Path -LiteralPath $project -PathType Container)) { throw '请输入已存在的工作区绝对路径' }
$parent = Join-Path $project '.agents/skills'
$target = Join-Path $parent 'ecommerce-image-replicator'
Write-Host "项目级安装位置：$target"
if (Test-Path -LiteralPath $target) { throw '已有同名技能；先比较、备份到扫描目录之外，不能覆盖定制' }
New-Item -ItemType Directory -Path $parent -Force | Out-Null
Copy-Item -LiteralPath $skill -Destination $target -Recurse
foreach ($item in $manifest.files) {
    if ((Get-FileHash -LiteralPath (Join-Path $target $item.path)).Hash -ne $item.sha256) { throw '安装后校验失败，保留现场' }
}
```

安装结果：

```text
<工作区>/.agents/skills/ecommerce-image-replicator/
  SKILL.md
  LICENSE
  references/input-deltas.md
  references/diagnostics-and-recovery.md
```

在DSH中打开该工作区并新建会话，确认可发现ecommerce-image-replicator，实际加载来源为该目录、版本为0.1.0-mvp.11。默认文件监视可刷新目录；不同提供方或禁用监视时重开会话后确认。发现同名用户级或插件副本时先排除来源遮蔽，不修改Host私有数据库。

本手册只提供项目级安装，空项目路径会拒绝；不自动改成用户级安装，也不修改MCP配置。

## 3. 使用

- 新任务：“依据这些竞品图和我的产品图复刻整套图片。已确认的产品事实如下……请先准备和预检，暂不调用收费工具。”不需要预先提供run_id。
- 已有结果：“接手此工作区中已有父/子任务，只整理当前结果，不新增收费分析、绘图或vision；最终业务效果由我验收。”提供实际任务身份即可。
- 局部修改：指出图片、要改的内容和本次授权范围，成功图片继续保留。

自然语言可自动触发，也可用DSH的显式技能选择入口。新任务一次合并缺少事实和授权；普通参数交MCP校验，不要求用户多轮引导核对。接手交付默认读状态、合并版本、一次批量核验实际SHA256、给出普通文件链接；点击链接在侧栏看图，不自动复制、打包、裁图或重审。

文件身份/hash不符不能通过。轻微视觉偏差由用户结合业务用途判断；review_required或needs_revision如实列待办，不为了交付而改成accepted。参数异常按MCP字段、阶段和错误码定点修复；未知提交先查原操作，不能重提可能收费的请求。

## 4. 检查、升级、回退与卸载

| 情况 | 处理 |
|---|---|
| 找不到技能或来源不对 | 核对项目作用域、目录大小写、SKILL.md及同名副本，重开会话后确认 |
| 摘要不符/额外文件 | 停止覆盖，保留现场，重新取得同版本完整包；不把现场摘要作为新的期望值 |
| MCP缺少能力或认证失败 | 核对现有连接返回的schema及权限；不要求提供密钥，不用收费执行探测 |
| 已有图待验收 | 先交付其它结果并列明待办，用户决定是否修订，不强制重绘整组 |

升级使用新版本独立下载目录，先核对旧安装与旧清单、比较本地修改，将旧副本保留到扫描目录之外后安装完整新包。回退恢复匹配的完整旧版本及资源，再确认DSH来源；技能回退不撤销MCP任务或收费。

卸载前核对安装目录、版本、文件清单和本地修改，再仅移走该技能目录到扫描范围外。重开会话确认不再发现此副本；产品图、产物、MCP状态、凭据和其它技能均保留。不要递归清空技能父目录。

## 5. 发布与验收记录

已于2026-10-29 12:59（Asia/Shanghai）发布为 **Prerelease**，不是Draft。

- Release：[v0.1.0-mvp.11](https://github.com/tsyecommercialdesigner-cloud/ecommerce-image-replicator-skill/releases/tag/v0.1.0-mvp.11)
- 标签完整提交：`276b354519caac537aad323c2b8cb3ecf25f40e7`（[合并PR #1](https://github.com/tsyecommercialdesigner-cloud/ecommerce-image-replicator-skill/pull/1)）。
- ZIP SHA256：`32dff2afab494b76334cb606bb8b193844bb1e5a27e2e41c9adb1fa4f6b9b03f`。
- [main CI](https://github.com/tsyecommercialdesigner-cloud/ecommerce-image-replicator-skill/actions/runs/40820721854)及[Release工作流](https://github.com/tsyecommercialdesigner-cloud/ecommerce-image-replicator-skill/actions/runs/40820762357)均成功。
- 实际附件共5份：上表列出的ZIP、manifest.json、SHA256SUMS.txt、MANUAL.md、VALIDATION.md。ZIP内部是四份文件（含许可证），manifest记录与下载后核对一致。
- 下载及安装命令已用实际发行附件在仓库内隔离目录执行：首次/重复下载、全部附件和包内摘要、带外层引号的中文及方括号项目路径、同名安装保护通过；空输入、相对路径、不存在路径均拒绝。测试目录已清理，正式Host安装及MCP配置未动；未重新执行Host发现、升级到其它版本或收费调用。

Release附件MANUAL/VALIDATION保留该标签构建时的快照；本节为发布后的实际结果，最新手册在[主分支MANUAL](https://github.com/tsyecommercialdesigner-cloud/ecommerce-image-replicator-skill/blob/main/MANUAL.md)。本次回填不移动标签或覆盖已发行附件，不把当前文档提交当作运行包来源。

行为证据：DSH已有结果交付单次1分9秒、4工具调用、无新增供应商调用，普通文件链接实际打开；最后通用示例整理只做静态检查。全部PRD、新任务全链路、其它Host及稳定性能未由此证明。详见VALIDATION.md及仓库[效率回归](https://github.com/tsyecommercialdesigner-cloud/ecommerce-image-replicator-skill/blob/main/evaluations/FLOW-PERFORMANCE.md)。
