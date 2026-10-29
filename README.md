# ecommerce-image-replicator-skill

通过现有ecommerce-image-replicator MCP，指导Agent依据产品图与已确认事实复刻竞品图，并接手、交付或修订已有任务。

当前版本：**0.1.0-mvp.11**（预发布候选）。适配MCP 0.1.7；已验证Windows DSH Desktop 0.2.1-rc.2，其它Host尚未行为验收。

## 使用入口

从[版本Release](https://github.com/tsyecommercialdesigner-cloud/ecommerce-image-replicator-skill/releases/tag/v0.1.0-mvp.11)获取完整Skill ZIP，按[MANUAL.md](MANUAL.md)校验并装入目标工作区的`.agents/skills/ecommerce-image-replicator/`，在DSH中打开该工作区。

提供产品图、竞品图和已确认事实即可自然语言触发；新任务先准备/预检，收费执行按实际授权。已有结果按任务记录合并版本、批量核验文件hash、给出图片链接，点击即DSH侧栏预览。默认不重复审图、查询团队、复制打包或制作HTML，最终业务用途由用户验收。

技能运行包仅含三份Markdown与MIT许可证，无运行脚本或额外运行依赖；使用者需已有可用MCP连接。仓库测试与CI设施不随Skill安装。

## 验证与开发

DSH单次已有结果交付实测1分9秒、4工具调用，无新增供应商调用；不代表全PRD、新任务全链路或其它Host通过。最后示例泛化未重新做Host测试，详见[交付审查](docs/MVP11-DELIVERY.md)和[效率回归](evaluations/FLOW-PERFORMANCE.md)。

开发环境：Python 3.12，`pip install -r requirements-dev.txt`；执行`python scripts/check_skill.py`、`python -m unittest discover -s tests -p test_release.py -v`。CI仅运行结构与发布包检查，不启动MCP供应商。原生MCP离线契约测试另需已安装的MCP开发环境，不是Skill运行依赖。

- [技能入口](skills/ecommerce-image-replicator/SKILL.md)、[PRD](PRD.md)、[技术契约](TechSpec.md)
- [实施状态](docs/MVP-STATUS.md)、[DSH验收](docs/DSH-MVP-REPORT.md)
- [工程指南](docs/engineering/ENGINEERING-GUIDE.md)、[手册规范](docs/delivering/MANUAL-WRITING-GUIDE.md)

Git交付：dev → PR → CI和评审 → main复验 → tag触发Release。尚未发布时，Release链接可能没有附件；实际发布结果在MANUAL末尾记录。许可证：[MIT](LICENSE)。
