# 输入增量：构造复杂字段时读取

以本次工具 schema 为准。利用 MCP 的契约与 LangGraph 校验，不建立另一套手工 OCR 或交互式参数核查。

## 公共字段只写一次

输入目录为 references/<group>/*.png|*.jpg、products/*.png|*.jpg、至少一份 brief/*.md；.jpeg 不在发现集合。保护原图与已有成果。
brief/design.json 提供 facts（每项 value/source 非空）、forbidden_claims 与 defaults（Delta）；Markdown 只作来源，不自动转成属性、换词和颜色。
公共产品属性与主题放 defaults.design；组 JSON 是自然排序数组，长度始终等于整组参考，包括未选图片。各项 {} 继承 defaults。

design.product_attributes 每项含 property/value/source；property 只能 name/dimensions/material/color/pattern/texture/specification，同 property 唯一。克重等不造新枚举字段，按实际文字增量表达。
主题用 brand_style.palette/tone；统一文字主题须明确 text_color=#RRGGBB。art_style 仅在用户要求换媒介时填写。
默认合并：逐图 texts/scene/text_replacements 非 null 才覆盖；instruction 取逐图非空值，否则继承；design 浅合并，brand_style 按非 null 字段再合并。
product_attributes 数组整体替换，不按 property 合并；逐图覆盖时保留仍需的属性。不填非空 objects/layout_regions/forbidden_elements 放宽原图边界。

## 默认事实适配；需要逐字约束才精确换词

MCP允许基于产品事实/属性适配参考文案；未提供显式texts或有效text_replacements时，text_role为reference_transcription，原转录是分析辅助，生成指令允许有依据的尺寸/材质等对应文案适配。
因此普通产品替换写facts、公共产品属性、主题及必要逐图instruction即可，不要求把每个参考旧值转成old→new。克重等不在属性枚举中的事实写入facts及明确适配指令。
精确texts/规则用于用户要求的字面锁定或已知具体copy修正，会切换为explicit_replacement。不要在默认路径读取旧裁图、逐字确认标签、创建第二套OCR或校验流程来凑齐可选规则。
准备未冻结的Agent草稿时，可保留事实与编辑意图、撤回非用户要求的冗余猜测规则；MCP已经报错或用户指定了精确更正时，必须按诊断修复，不能清空全部规则逃避要求。

text_replacements 每项 old/new/source 非空，匹配忽略大小写的字面子串，不支持正则。old 必须在本图转录出现，不能把一份规则铺满无该文字的整组。
禁止 old 重复/互相包含/重叠，或任意 new 包含任意 old 导致链式/残留。有有效规则时不能同时给显式 texts。
已知可读的必要换词直接写；未确定的旧词不猜，不为补齐微小标签穷举裁图。MCP 分析后若返回 copy 诊断，就用 transcription、0 基 replacement_indexes、delta/effective_delta 和来源直接修对应规则。
事实适配不是精确文案已通过的证据；成图仍有旧规格就不能验收通过。未提供逐字规则时，不因plan中的参考转录保留旧参数就自行抄图重建整组；对照产品属性、生成指令和实际成品判断。精确分支则核对最终texts/规则，不清空更正或改scene回避诊断。

示例仅解释规则：短词与包含它的完整规格不能同时作为两条 old，否则匹配重叠。
只有确认本图该短词的全部出现都表示同一待改事实时，才可用一条替换覆盖，并在source写真实依据；混有报告号或其它含义时不能这样简化。
需区分含义就用确实存在且互不包含的完整文字片段；不猜空格、不用正则、不删除必要改词。复杂度超出已知证据时按 MCP 具体诊断处理，不持续加大裁图倍数。

## 手工文字是例外

默认 texts/scene 省略或 null。texts=[] 是最终空文案，不是自动提取；不能用空文字、占位 scene/框绕过分析。
只有用户提供最终文字和布局，或明确诊断无法由 MCP 分析解决且有实图依据时，才手工构造 TextBlock。
content 非空，css 为字符串，box 用 EXIF 校正后原图归一到 0..1000：x=1000*x_px/W、y=1000*y_px/H，宽高同理，不能越界或直接填像素。
真正无法取得的必要事实/文字保持未知并报告具体缺口，不伪造转录或假称更正完成。
