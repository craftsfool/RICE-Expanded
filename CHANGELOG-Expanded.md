# RICE Expanded — expanded.3: Caucasus translations and religious stories

2026-10-08 · CK3 1.20.* · 社区预发布 / Community prerelease

- 完成高加索既有内容的简中和法语译文，并补齐两条 CE 文化条件、CE 原始建国决议的本地化别名。高加索共 838 个键提供英／简中／法语；旧中法英文回退文件被清空，以支持原位更新。
- 新增杰尔宾特近卫争端、洛里教会争论、阿尼圣所归属、阿兰传教反弹和通基拉德派五条故事：五个决议、17 个事件、15 个五年地方修正。包含付费选项、后续反应、互斥政策、十年冷却和失地后的事件中止。
- 通基拉德礼制为原版亚美尼亚使徒教会分支，使用反圣像、公有财产、造反有理三条原版教义，支持男女平等、男女俗人神职及男女私通获准。红色碎裂亚美尼亚十字架图标为工具生成，透明 DXT5。
- 按原版历史异端首次创立逻辑生成斯姆巴特·扎雷哈万齐，由他创建礼制并出场于事件。描述使用原版通用格式与教义句子，永久保存首次创立者姓名链接、地点与年份；死亡后由追随者接续讲道。
- “造反有理”采用原版不屈信仰教义的特殊名称；仅修改原版名称／描述选择，71 条教义的机械效果不变。阿尼记录建筑用途而不改变全县信仰；通基拉德加入仅影响统治者与阿帕胡尼克。
- 内容和兼容层继续内置在 RICE Expanded，提供 Base、EPE、CE–EPE 三种原位更新包；仅进行后台静态与脚本检查，未启动游戏。

Completed Simplified Chinese and French translations for all Caucasus content, with English retained and five other languages using explicit fallbacks. Added five religious story chains with seventeen events and fifteen policies. The Tondrakian branch of the vanilla Armenian Apostolic faith uses native Aniconism, Communal Possessions and Righteous Rebellion mechanics, equal gender doctrines, accepted male and female adultery, and a generated fractured-cross icon. Compatibility remains built into RICE. Validation is static and scripted; the game was not launched.

# RICE Expanded — expanded.2: Caucasus English Alpha

2026-10-07 · CK3 1.20.* · 社区预发布 / Community prerelease

## 身份与来源 / Roles and sources

RICE 的原作者为 **cybrxkhan**。本版由 **craftsfool** 作为协助发布者／整合维护者发布，使用 Codex 协助审查、整合、补译与验证；不是上游官方发布，也不代表原作者或汉化作者。原 README 保持逐字一致。

RICE is authored by **cybrxkhan**. **craftsfool** publishes this community integration as an assisting publisher and integration maintainer, with Codex assistance for review, integration, translation and validation. This is not an official upstream release. The original README is unchanged byte for byte.

- 基础 / Base: fork master `f2aa2c7ae50294407f0aca7f154dfdbd2dc28d46`，已包含上游 [1.20.0-beta-1](https://github.com/cybrxkhan/RICE-for-CK3/releases/tag/1.20.0-beta-1)。
- [PR #345](https://github.com/cybrxkhan/RICE-for-CK3/pull/345), **pharaox**: `7097fbf0b41f3aada8dbb11e516dd819ad01c7ec`，完整合入 / merged with original history.
- [PR #344](https://github.com/cybrxkhan/RICE-for-CK3/pull/344), **Vakiadia**: `54924c115ed827da5042afdba47e76c850fec12b`，完整合入并适配山岳崇拜标识 / merged; sacred-mountain history identifiers updated for 1.20.0.4.
- [PR #343](https://github.com/cybrxkhan/RICE-for-CK3/pull/343), **Vakiadia**: `261a750796d77398c3460ccc595d7e831fed3284`，审查后补入尚未覆盖的礼制教义判断 / reviewed; remaining rite-level doctrine fallback fixes applied.
- 法语 / French: **Bacchurion**, **NicolasGrosjean**, upstream PR #327–#342，仅迁入本地化变更；重叠键采用较新有效译文。确切来源见 [french-sources.json](reports/french-sources.json)。Localization changes only, with newer effective translations retained for overlapping keys.
- 简中 / Simplified Chinese: [牛奶汉化之 RICE](https://steamcommunity.com/sharedfiles/filedetails/?id=2823178539)。保留原文件和开局致谢中的汉化署名，包括 Juijote、奶皇、xizhigaofeng、YoungのFish 及其他贡献者。本次补译不能归为这些作者的原作。Original translator credits are retained; new Expanded translations are separate integration work.

## 适配 / Compatibility

- 保留新版宗教、宗派、礼制、圣地与教义结构；合入无地头衔、宗教访问器、历史信仰核心教义及事件适配。
- 核对本地清单全部 236 项 RICE 修正：232 项目的已由新版实现覆盖，4 项旧占位或结构已过时。90 份旧 `local120` 新增文件由上游正式定义替代，避免重复注册。逐项结果及核对边界见 [local-repair-audit.json](reports/local-repair-audit.json)。
- 北大西洋与斯里兰卡决议的重复 widget 防崩溃修正已通过 #345 整合进本体，每项决议最多保留一个 widget。
- 为 25 份决议文件中的 50 个选项列表启用 1.20 支持的 `show_from_start`，恢复选择方式后再确认的流程；实机复核斯里兰卡与格陵兰决议。
- 将双元论净化与佛教经典的默认教义判断放在各礼制内，保留已有自定义教义；诺斯替资格仍按宗派判断。
- 本地工坊安装、播放集、存档保持原样；开始工作前已保存 RICE、牛奶汉化、决议补丁及本地修正备份。

Retains the 1.20 religion/faith/rite structure and incorporates landless titles, religion accessors, starting tenets and event adaptation. All 236 local repair records were reconciled against the new structure: 232 purposes covered by the updated implementation and four obsolete records. Canonical upstream definitions replace the 90 old `local120` files. North Atlantic and Sri Lanka decisions have at most one widget. The 50 option lists in 25 decision files now explicitly show choices before confirmation through the 1.20 `show_from_start` setting. Default canon/purification doctrines are checked per rite, preserving existing custom choices. Workshop installations, playsets and saves were left untouched.

## 本地化 / Localization

- 按键迁移牛奶汉化 113 份文件，包含普通、宗教、引用和 `replace` 内容；新增 187 个真实简中译文，并审查适配 47 个英文变化条目。修正斯里兰卡、努比亚等处的过时表达式、括号、引用、乱码与版本说明。
- 补齐 `held_county` 与 `squared_distance` 条件提示的中英文文本，消除相关决议条件中的缺失标签；其他六种语言暂用英文回退。
- 法语 PR 共应用 4,856 次变更键记录（重叠键可能多次计数），只引入翻译内容。
- 八种语言统一 UTF-8 BOM、语言头与文件命名；修复内嵌引号、重复键、错误文本引用和旧宗教访问器。保留变量、格式标记及合法 `replace` 覆盖。
- 其他语言没有译文的缺键用单独文件英文回退：法语 176、德语 803、西语 455、俄语 223、波兰语 222、日语 222。**这些不是已完成翻译**。逐语言键清单和已有英文候选见 [localization-gaps.json](reports/localization-gaps.json)；候选中可能含正常人名、地名和共享引用。

Migrates 113 Milk localization files, adds 187 translated Simplified Chinese keys, and reviews 47 changed English entries. French contributions account for 4,856 key applications, including overlapping edits. All eight languages retain valid BOMs, headers, filenames, expressions, formatting and intentional overrides. Missing translations use explicit English fallbacks, listed above and in the language gap report; fallback coverage does not imply completed translation.

## 安装 / Installation

下载 Release 的安装 ZIP，将其中 `RICE/` 和 `RICE.mod` 放入 CK3 用户目录的 `mod/` 文件夹，在启动器中启用 **RICE Expanded (Community 1.20 Beta)**。此安装包使用 `path="mod/RICE"`，没有绑定官方工坊发布 ID。建议用新播放集和新存档测试，避免同时启用官方 RICE、旧决议补丁或独立牛奶 RICE 汉化，以免重复覆盖。支持版本标记为 `1.20.*`，实机验证版本为 `1.20.0.4`。

Download the installation ZIP from the Release. Place `RICE/` and `RICE.mod` in your CK3 user directory’s `mod/` folder and enable **RICE Expanded (Community 1.20 Beta)** in the launcher. The descriptor uses the portable `mod/RICE` path and has no official Workshop publishing ID. Test with a new playset and save; avoid enabling the original RICE, old decision compatibility patch or separate Milk RICE translation alongside this integrated package. Marked compatible with `1.20.*`; runtime validation uses `1.20.0.4`.

## 验证与 beta 限制 / Validation and beta limitations

- 静态检查：0 项错误、13 项可选模组／调试宗派引用警告。103 个宗派、106 个礼制、44 个宗教类型没有重复注册；相关决议最多一个 widget。八种语言均无英文基准缺键、格式错误或未解析的静态 `$...$` 引用；README 与起始提交逐字一致。检查器仅验证结构，不能证明所有动态表达式及引擎作用域正确。
- 自动操作实机测试：CK3 **1.20.0.4**，独立用户目录、冻结模组副本、简中界面。1066 开局与宗教界面正常；“支持室利楞伽僧伽”的香火钱、“净化室利楞伽的僧伽”的掠夺财富、格陵兰基本用品支援均经过选择、确认、事件和资源变化复核。观察者从 1066-09-15 运行至 1073-01-01，未再次崩溃。最终选项界面修复又完成上述决议复测。
- 手动测试：维护者在收到 867、1178、无地冒险者、宗教、决议及存读档等清单后确认“测试完毕，发布”。这是维护者的整体确认，未提供逐项记录，因此不将每项写成独立自动验证通过。自动测试环境未生成可玩的无地营地，该项目的独立实机验证仍有限。
- 测试期间曾发生两次崩溃：第一次栈指向调试本地化热重载，发生于运行时修改翻译文件；第二次发生于误用历史角色标识作为控制台 `play` 参数后，栈位于角色／继承界面更新。改用冻结副本、有效数字角色 ID 后未复现。这些测试操作相关异常不等于已证明所有正常玩法无崩溃。
- 保留的 beta 问题：日志仍有 DLC 锁定核心教义、可选其他模组宗派、缺失历史角色 `RICE_bodah_001`／`RICE_lohanah_001`、部分事件作用域及南埃塞俄比亚活动选项类别错误。后两项所抽查脚本片段与起始 beta 相同；未做同条件双版本运行，不能把全部日志差异归为上游或声明运行日志零错误。决议条件的精确视角提示仍可能使用有效回退。详见 [runtime-validation.json](reports/runtime-validation.json)。
- 其他语言完成结构检查，未逐语言实机检查所有界面。长期战役、旧存档升级及其他模组组合未作全面验证。本版维持 **预发布** 状态。

Static validation reports zero errors and 13 optional-mod/debug faith-reference warnings, with no duplicate religion registries or multiple decision widgets. All eight languages cover the English key baseline and have no malformed entries or unresolved static text references. README matches the starting commit byte for byte. Structural validation cannot prove every dynamic expression or engine scope valid.

Runtime checks used CK3 **1.20.0.4**, an isolated user directory, a frozen mod copy and Simplified Chinese. The 1066 start, religion interface, non-default Sri Lankan support/purification choices, and Greenland basic-supply support completed their confirmation and event flows. An observer run reached 1073-01-01 from 1066-09-15 without a further crash. The final option-list repairs were retested in these decision flows. The maintainer subsequently confirmed manual testing was complete and authorized publication; individual manual test results were not supplied. Landless validation in the automated environment was limited by DLC availability.

Two earlier test crashes occurred during localization hot reload and after an invalid debug role-switch argument. Neither recurred after freezing the test files and using verified numeric character IDs. This is not a guarantee of crash-free gameplay. Beta log issues remain, including DLC-locked tenets, optional faith references, missing historical characters, event scopes and an Ethiopian activity option category. Sampled affected scripts match the starting beta; a controlled two-build runtime comparison was not performed. Other languages were checked structurally, with full UI coverage, long campaigns, old-save upgrades and mod combinations still unverified. This remains a **prerelease**.


## 2026-10-07 — Compatibility patches

核对维护者修改过的本地 RICE、CE 和 EPE，同步 EPE 补丁的六处文化内容；修复 CE 组合的重复文化和语言／传承定义，恢复美洲及大洋洲独立分类与创新初始化。两个补丁改用便携安装描述文件。未启动游戏；四种加载组合通过脚本检查。CE 本体仍标注 1.19，本次不是 CE 全量 1.20 移植。详见 [兼容补丁说明](COMPATCHES-Expanded.md) 及 [检查报告](reports/compatch-validation.json)。

Audit against modified local RICE, CE and EPE; preserve local gameplay in six EPE cultures, resolve CE shared registries, restore distinct American/Oceanian pillars and startup innovation grants, and make both patch descriptors portable. Four static load profiles pass; no game launched. CE itself still targets 1.19. See the compatibility documentation and report linked above.

## 2026-10-07 — expanded.2: Caucasus English Alpha, built-in compatibility

高加索内容直接合入 RICE 主包：八个 CE 文化及依赖、23 位既有历史人物文化修正、六个决议、23 个事件、686 条英文键和杰尔宾特横幅。Base、EPE、CE–EPE 三个完整安装预设把所需兼容文件合入同一个 RICE 目录，无需独立高加索或兼容模组。其他语言保留原版术语和明确的英文回退，尚未完成新内容翻译。本次只进行后台静态检查，未启动游戏或操作桌面；旧版实机测试不能代表本次新内容已实机验证。

Embeds the Caucasus English alpha and produces complete Base, EPE and CE–EPE installation presets, with compatibility baked into each RICE directory. Includes eight CE culture definitions, source dependencies and existing-character corrections, six decisions, twenty-three events and a generated Derbent banner. Native vanilla terms and explicit English fallbacks are retained for other languages. Validation of this update is static only; earlier runtime results do not validate the new content. See [Caucasus details](CAUCASUS-Expanded.md).
