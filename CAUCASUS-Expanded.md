# RICE Expanded：高加索英文 Alpha（内置）

高加索内容直接内置在 `RICE/`，包括八个 CE 文化定义、相关文化依赖、既有历史人物文化修正、六个决议、23 个事件和杰尔宾特决议横幅。原创内容为五个决议、22 个事件。英文文本已完成；其他语言暂用明确标识的英文回退，原版已有地名和文化名称保留各语言原文。简中 Derbent 固定为 **杰尔宾特**。

## 安装包与兼容

| 安装包 | 需要的其他模组 | 内置内容 |
| --- | --- | --- |
| Base | 无 | RICE Expanded + 高加索；外观采用原版回退 |
| EPE | EPE | 主包 + RICE/EPE 兼容 + CE 原始高加索外观字段 |
| CE–EPE | CE、EPE | 主包 + RICE/EPE、RICE/CE 兼容 + 高加索 CE 去重与初始化处理 |

完整包只安装一个 `RICE/` 和 `RICE.mod`。在线的 `Built-In-Update` ZIP 是原位更新包，需要先安装 expanded.1 基础包，再解压覆盖同一个 RICE 目录。根据使用的模组选一个包；加载其他基础模组后，再加载 **RICE Expanded (Community 1.20 Beta)**。不用启用独立高加索包或独立兼容补丁。CE–EPE 包与当前本地 CE/EPE 组合对应，CE 本体和 EPE 本体仍需启用。

兼容预设在构建时合入主目录，避免不同加载组合的整文件覆盖互相干扰。旧独立补丁目录保留作兼容构建来源与旧版维护，不作为本次整合包的额外加载项。`authoring/` 是制作素材与可复现工具，不是可启用的独立模组。

## 内容与来源

- CE 文化：Circassian、Udi、Dagestani、Abkhaz、Laz、Svan、Tat、Alan。玩法字段取自已安装 CE；EPE 预设保留完整源外观字段。Base 只替换外观为原版回退，不改变文化玩法。
- 867、1066、1178 的相关 CE 初始化：23 位既有角色，跨开局共 65 条角色操作；59 条县级操作。可以用游戏规则关闭独立 CE 初始化；CE–EPE 包由 CE 自己初始化。
- 地方玩法：杰尔宾特通道修缮与政策复核、洛里教学与抄写、斯瓦涅季塔楼社区、1106 年后库塔伊西周边学术赞助。年事件涉及修缮、商旅、书籍与社区分担。
- CE 外高加索建国决议与确认事件已迁入；使用 CE 时保留其原始决议并隐藏迁入副本。独立模式在建国时才调整法理归属。
- 杰尔宾特两个决议使用原创工具生成横幅（1100×440、DXT1、完整 mip 层）；其余暂用原版美术。人物外观由原版或所选 EPE 组合提供。

CE 来源为 Workshop 2829397295（本地版本 1.19.0.6），EPE 为 2507209632（本地版本 1.20.0.3）。感谢 Culture Expanded、EPE、cybrxkhan 与 RICE 贡献者。逐项来源和文件指纹见 `reports/caucasus-ce-import-manifest.json`，完整英文内容说明和美术提示词保留在 `authoring/caucasus_flavor_pack/`。未复制无关的虚构巴尔干人物。

## 验证范围

只进行后台脚本和纹理文件检查，不启动游戏，不操作桌面、鼠标或键盘。检查整合后的实际文件组合、文化重复注册、依赖引用、英文文本、费用与政策互斥，以及 DDS 完整性。界面裁切、引擎作用域、人物外观和长期平衡尚未实机验证；本次仍为 Alpha 预发布。

历史题材参考：[杰尔宾特](https://whc.unesco.org/en/list/1070)、[哈格帕特与萨纳欣](https://whc.unesco.org/en/list/777/)、[上斯瓦涅季](https://whc.unesco.org/en/list/709)、[格拉蒂](https://whc.unesco.org/en/list/710)。具体事件对话、纠纷和数值效果属于游戏创作。

# Caucasus: Passes and Sanctuaries — built into RICE Expanded

The English alpha is embedded in RICE, with eight CE culture definitions, relevant source dependencies and character corrections, six decisions, twenty-three events and an original generated Derbent banner. Select one complete installation preset: Base, EPE, or CE–EPE. Each full preset installs only `RICE/` and `RICE.mod`; compatibility files are baked into that directory. The online `Built-In-Update` ZIPs require the existing expanded.1 base installation and update that same RICE folder in place. Load RICE Expanded after the required base mods and disable the old separate compatibility mods.

The Base preset retains CE gameplay with vanilla appearance fallbacks. EPE presets preserve the exact copied CE appearance fields. CE–EPE preserves CE's original startup setup and empire decision, suppressing the duplicate copies. Other languages have English fallbacks and native vanilla terms, not completed translations. All new gameplay prose is completed in English.

Static validation only; no game or desktop control was used. This does not confirm engine execution, rendered interfaces or campaign balance. Source records, historical references, exact artwork prompt and validation reports are included in the repository.
