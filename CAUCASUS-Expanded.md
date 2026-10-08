# RICE Expanded：高加索 Alpha（英／简中／法语，内置）

高加索内容直接内置在 `RICE/`，包括八个 CE 文化定义、相关文化依赖、既有历史人物文化修正、十一个决议、40 个事件、通基拉德分支礼制及原创美术。原创内容为十个决议、39 个事件，另有迁入的 CE 决议与事件。高加索全部 838 条本地化键已提供英文、简中和法语；其他五种语言保留英文回退和原版已有术语。简中 Derbent 固定为 **杰尔宾特**。此翻译范围是高加索内容，并不表示整个 RICE 的各语言翻译均已完整。

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
- 地方玩法：杰尔宾特通道修缮与政策复核、洛里教学与抄写、斯瓦内蒂塔楼社区、1106 年后库塔伊西周边学术赞助。年事件涉及修缮、商旅、书籍与社区分担。
- 新增五条宗教故事，共五个决议、17 个事件：杰尔宾特罗斯近卫争端（1200 年前，穆斯林统治者）、洛里教会争论（1100 年后，基督徒）、阿尼圣所归属（1064 年后，基督徒或穆斯林）、阿兰传教反弹（1200 年前）、通基拉德派调查与处置（1100 年前，基督徒）。决议均需成年、未入狱、和平且直接持有目标县。
- 每条故事有不同处置、后续费用与地方反应，最终政策持续五年，决议冷却十年。延迟事件重新检查目标县归属；流程锁一年后自动到期。阿尼按原版 `c_hayk`／`b_ani` 定位，圣所用途单独保存，不把一座建筑改作教堂或清真寺等同于全县改宗。
- 通基拉德派使用 1.20 原生礼制机制，母体为原版亚美尼亚使徒教会。三条核心教义为反圣像、公有财产、造反有理，支持男女平等、男女俗人神职和男女私通获准。调查开始时按原版历史异端模板生成斯姆巴特·扎雷哈万齐，由他本人创建并改奉礼制。文化为亚美尼亚；Zarehavantsi 是籍贯称号，宗族未获明确证实，故不虚构贵族谱系。亚美尼亚使徒教会统治者可花费 500 虔诚加入，使自身与直接持有的阿帕胡尼克县改奉礼制。创立者去世后，复兴调查由在世追随者出面；描述保留首次创立者的可点击姓名、地点与年份。礼制创建后可通过原版宗教机制继续传播。图标为透明红色碎裂亚美尼亚十字架。
- “造反有理”是原版 `tenet_unrelenting_faith` 的特殊名称。主包覆盖原版 `00_tenet_types.txt`，仅增加新礼制的名称与描述选择条件，所有 71 条原版教义的机械效果保持一致。将来原版更新该文件时需重新同步；其他模组若覆盖同一文件，则需要合并。生成器和原版文件指纹已保存。
- CE 外高加索建国决议与确认事件已迁入；使用 CE 时保留其原始决议并隐藏迁入副本。独立模式在建国时才调整法理归属。
- 杰尔宾特决议使用原创工具生成横幅（1100×440、DXT1、完整 mip 层）；其余使用原版美术。新礼制图标为 100×100、DXT5，保留透明通道。人物外观由原版或所选 EPE 组合提供。

CE 来源为 Workshop 2829397295（本地版本 1.19.0.6），EPE 为 2507209632（本地版本 1.20.0.3）。感谢 Culture Expanded、EPE、cybrxkhan 与 RICE 贡献者。逐项来源和文件指纹见 `reports/caucasus-ce-import-manifest.json`，内容说明、美术来源和可复现工具保留在 `authoring/caucasus_flavor_pack/`。新增译文与故事属于 Expanded 制作，不归为原版、CE 或原汉化作者的作品。未复制无关的虚构巴尔干人物。

## 验证范围

只进行后台脚本和纹理文件检查，不启动游戏，不操作桌面、鼠标或键盘。检查三种预设的实际文件组合、文化与礼制重复注册、依赖引用、三语文本与变量标记、费用、政策互斥、失地后的事件中止、礼制创建与重复加入，以及 DDS 完整性。脚本模拟不等于引擎执行；界面裁切、引擎作用域、人物外观和长期平衡尚未实机验证，本次仍为 Alpha 预发布。

历史题材参考：[杰尔宾特](https://whc.unesco.org/en/list/1070)、[哈格帕特与萨纳欣](https://whc.unesco.org/en/list/777/)、[上斯瓦涅季](https://whc.unesco.org/en/list/709)、[格拉蒂](https://whc.unesco.org/en/list/710)。具体事件对话、纠纷和数值效果属于游戏创作。

宗教故事的具体史料与年代争议见 `plans/Caucasus-Religious-Content-Plan.md`：杰尔宾特取材于 989—990 年近卫争端，洛里取材于 1170 年代合一谈判，阿尼参考 1064／1124 年建筑用途变化，阿兰参考马苏第记载的 932 年教士驱逐。除通基拉德派首次出现时生成历史人物模板外，其他史实人物只在背景说明中出现。斯姆巴特模板随事件触发年生成人生时间，遵循原版历史异端的处理方式，不声称他实际活到了1066等开局。通基拉德派材料多来自其反对者，指定三教义和男女平等属于本次游戏建模；阿兰地方旧俗没有套用近现代奥塞梯神谱。

# Caucasus: Passes and Sanctuaries — built into RICE Expanded

The alpha is embedded in RICE, with eight CE culture definitions, relevant source dependencies and character corrections, eleven decisions, forty events, a Tondrakian branch rite, an original Derbent banner and a fractured Armenian-cross icon. All 838 Caucasus localization keys are available in English, Simplified Chinese and French. Select one installation preset: Base, EPE, or CE–EPE. Compatibility is baked into its single RICE directory. The online Built-In-Update ZIPs update an existing expanded.1 or expanded.2 installation in place. Load RICE Expanded after its required base mods and disable old separate compatibility mods.

The Base preset retains CE gameplay with vanilla appearance fallbacks. EPE presets preserve the exact copied CE appearance fields. CE–EPE preserves CE's original startup setup and empire decision, suppressing duplicate copies. Five other languages retain English fallbacks and native vanilla terms. Complete translations apply to Caucasus content, not every entry in RICE.

Five new optional chains concern Derbent’s Rus guards, Lori’s church debate, Ani’s cathedral, missionary resistance in Alania, and a five-stage Tondrakian inquiry. The Tondrakian rite belongs to the vanilla Armenian Apostolic faith and has Aniconism, Communal Possessions, Righteous Rebellion, gender equality, clergy of either gender and accepted adultery for both sexes. It uses the native Unrelenting Faith tenet mechanics with a rite-specific vanilla label. The native tenet file is overlaid only to extend this label selection; other mods replacing that file need a merged version. Smbat Zarehavantsi is generated once from an Armenian historical-character template and creates the rite in his own character scope. His geographic designation is retained without fabricating a noble dynasty. An Armenian Apostolic ruler can then join for 500 Piety, converting that ruler and Apahunik. Later inquiries use a living follower if Smbat has died. The description follows the native generic format and keeps the original linked founder, place and year. The template lifespan follows the outbreak year, as in native historical-heresy spawning; it does not assert historical survival into later bookmarks. Ani’s sanctuary use persists independently of county faith. Policies last five years, decisions have ten-year cooldowns, and delayed stages recheck direct ownership.

Static validation only; no game or desktop control was used. This does not confirm engine execution, rendered interfaces or campaign balance. Source records, historical references, exact artwork prompt and validation reports are included in the repository.
