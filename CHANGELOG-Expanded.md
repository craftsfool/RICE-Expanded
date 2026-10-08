# RICE Expanded — expanded.3.7: opt-in Tondrakian testimony

2026-10-09 · CK3 1.20.* · 社区预发布 / Community prerelease

- 重做通德拉基派地区广播：第一次证词让玩家选择继续听证，或斥责异端、获得100虔诚并退出中间广播。
- 选择听证后，土地争议和教会禁令由玩家决定自己的宫廷立场，并产生学识经验、虔诚和人物态度效果。所有符合地域条件的基督教统治者仍会收到最终裁决；改信选项保留在后期阶段。
- 广播过滤、阶段选项、退订和最终消息加入脚本检查。英、简中、法文同步完成，其他语言提供英文回退。本次未启动游戏。

Turns the regional Tondrakian reports into an opt-in response chain. Rulers may hear the testimony and make decisions in the two intermediate stages, or rebuke the heretics for 100 Piety and receive only the final verdict. English, Simplified Chinese and French are complete; validation remains script-level.

# RICE Expanded — expanded.3.6: Tondrakian rite loop and Caucasus names

2026-10-08 · CK3 1.20.* · 社区预发布 / Community prerelease

- 删除创建信仰后和读取存档时自动重设通德拉基礼仪母信仰的脚本，避免1.20因差异度达到100而反复拆分出相同的独立信仰。
- 第三核心信条改为与原版亚美尼亚宗徒礼仪一致的米亚菲西特主义；无对应DLC时同步采用原版的禁欲主义回退。保留反圣像、公有财产、男女平等和男女私通获准；神职改为神权制、终身教会指认，并允许修道生活。
- 移除整文件覆盖原版97个信条的旧文件，减少与其他模组的冲突。补齐南高加索和高加索两个地区名的英、简中、法文及其他语言英文回退。
- 脚本检查通过582条事件路径、8组广播地域对照和9项礼仪流程检查。未启动游戏；实际引擎差异度与旧档已生成的空信仰仍需实机确认。旧档中的空信仰属于存档数据，本次不强行删除。

Removes the reparenting hook that repeatedly created duplicate Tondrakian faiths in CK3 1.20. The rite now shares the Armenian Miaphysite tenet, spiritual head, theocratic clergy and accepted monasticism, while retaining the requested equality and adultery doctrines. The native tenet override is removed, and Caucasus region names are localized. Script checks pass; engine behavior and old-save cleanup are not claimed as verified.

# RICE Expanded — expanded.3.5: Tondrakian rite and Caucasian broadcasts

2026-10-08 · CK3 1.20.* · 社区预发布 / Community prerelease

- 修复通德拉基礼仪的原版流程缺口：为历史AI创始人准备正确作用域，调用原版 `faith_creation.1021` 新礼仪通知；加入使用原版领主、宫廷和领地改信效果。
- 针对1.20高差异度礼仪转成独立信仰的规则，使用原版重设母信仰效果保留亚美尼亚宗徒教会分支，只处理通德拉基礼仪，不移动其衍生礼仪或其他信仰。
- 868年发源地阿帕胡尼克及信仰与领主均符合条件的邻县改奉礼仪；不强制玩家改信。旧档补回漏掉的改信，已镇压及之后自行改信的地区不会被反复改回。
- 证词、土地争议、教会禁令与处置结果传给南、北高加索所有基督教统治者，不再要求亲自持有阿帕胡尼克或属于同一教派。发源地领主无法主持调查时仍有地区消息链；实际调查接管后停止背景广播。
- 亚美尼亚国王旗下封臣的加入权重由5提高到40；保持拒绝选项。其他基督教派可以自愿加入亚美尼亚母信仰和通德拉基礼仪。移除加入的额外500虔诚门槛。
- 新增消息完成英文、简体中文和法文；其他语言补足明确的英文回退。修复重新生成内容时恢复0.25堡垒等级的制作脚本回归。
- 检验：582条宗教故事路径、8组地域对照、9项礼仪流程检查、6种实际模组文件组合均通过。结构、编码、三语及其他语言回退检查为0错误；保留原有可选整合引用警告。本次未启动游戏，未验证引擎执行或界面呈现。

Connects the historical founder to the native rite-creation notification and conversion helpers, seeds Apahunik and eligible neighbors, retains the Armenian parent faith, broadens follow-up broadcasts to Christian rulers across both sides of the Caucasus, and increases adoption weights for vassals of Armenian kings. English, Simplified Chinese and French are complete. Static and bounded-model checks pass; engine behavior and rendering remain unverified. The update applies to Unified expanded.3.4.

# RICE Expanded — expanded.3.4: nonzero fort bonuses and runtime repairs

2026-10-08 · CK3 1.20.* · 社区预发布 / Community prerelease

- 修复用户截图中塔楼修缮显示“堡垒等级 +0”的问题：塔楼修缮、熟练石匠、杰尔宾特守卫补给的 `fort_level` 从 0.25 改为整数 1；同步制作脚本，并增加整数显示与非零数值检查。其余百分比修正保留原数值。
- 根据实际启动日志，移除 55 处原版 `friendliness_opinion` 不接受的额外持续时间；好感仍按原版月度衰减。
- 补齐迁入 CE 文化概念的 20 个支柱图标，恢复西西里费用计算的四个文件内常量。原版已有文化采用自身的原版外观字段；行政政体条件改用 1.20 的 `government_has_mechanic`。
- 单独启用 Expanded 已实际进入主菜单与1066新战役；爱尔兰角色没有看到不相干的高加索地区决议，存档中1066通德拉基礼制和创立者已生成。本条记录的是修复前首轮实机测试；修复后数值显示尚未再次实机验证。
- 本次提供面向 Unified 3.3 的小型更新包，避免重复保存完整构建目录。完全退出并重启游戏以读取新的修正定义。保留预发布状态，不声称所有模组组合及长期战役已验证。

Corrects three fortification bonuses from fractional 0.25 to whole +1, matching native fort-level presentation. Fixes invalid friendliness-opinion durations, missing culture-pillar icons, local Sicily cost constants, native culture appearance fallback and the administrative-government condition. Standalone main-menu and 1066 campaign loading were observed before these repairs; post-fix UI rendering has not yet been retested. The small update applies to Unified 3.3 and requires a complete game restart.

# RICE Expanded — expanded.3.3: one self-contained package and character-led stories

2026-10-08 · CK3 1.20.* · 社区预发布 / Community prerelease

- 合并为一个无外部模组依赖的 Unified 完整包；CE／EPE 为可选项。补齐共同文化支柱与传递依赖，实际检测 CE 是否启用，恢复独立开局的高加索文化分布和外高加索帝国决议。修复与北太平洋地图的鄂温克文化／姓名表重复定义。
- 为全部 25 个高加索修正配置有效的原版正／负图标，恢复绿／红名称。重写四条宗教争端，强化通德拉基五阶段调查，并让 22 个地方场景出现持续保存的实际人物与书册结果。
- 罗斯招募出现斯拉夫真理教、东斯拉夫传承、军事 26／勇武 32 的队长；按原版机制可达极佳护卫称职度。选择聘为护卫或只雇战团，两者均获得 500 名事件兵，不替换满额职位。
- 洛里可延请教师与制作论辩书册；阿尼代表可入廷并安置迁出会众；阿兰可招募 200 名骑兵，个人洗礼为明确选项。通德拉基的女代表、讲道者和囚禁／庇护均为实际人物效果。
- 867 开局约一年后公布通德拉基兴起，年度全局补偿防止领主死亡漏触发；1066／1178 立即创建分支礼制。保持原创立者在死亡后的姓名、地点与年份链接。
- 878 个高加索制作内容键提供英／简中／法语；额外 CE 依赖标签保留可取得的源译文，缺失翻译明确使用英文回退。修复重复构建误清空标签的问题。
- 六种模组组合的脚本文件检查，以及 582 条宗教分支、时间安排、人物恢复、原版称职度和资源检查通过；只进行后台检验，未启动游戏。没有将静态通过表述为完整组合的崩溃已获实机解决。

A single self-contained Unified package replaces the three installation presets. Optional CE/EPE detection, starting culture assignments, the imported empire decision and North Pacific Evenk collisions are repaired. Caucasus modifiers now use native green/red icons. Stories introduce persistent actors, Rus event soldiers and an Excellent bodyguard, court teachers, manuscripts, sanctuary representatives, Alan riders and an optional baptism. The Tondrakian rite is scheduled around year one in 867 and initialized immediately for later starts. Validation remains static and scripted; no game or desktop control was used.

# RICE Expanded — expanded.3.2: native gold effects

2026-10-08 · CK3 1.20.* · 社区预发布 / Community prerelease

- 根据用户启动后的新日志，修复 31 个高加索事件付费选项：用原版 `remove_short_term_gold` 扣款，替换引擎不接受的负数 `add_gold`。金额、支付条件与分支结果不变，制作脚本也已同步修正。
- 通基拉德礼制定义补充 UTF-8 BOM。静态检查现在拒绝负数 `add_gold`，事件模型使用实际扣款指令，并逐种验证英法中安装文本；三个兼容预设及本地目录的 408 条分支检查通过。
- 包含 expanded.3.1 的 DDS 修复。仍不将这些已确认错误的修复表述为已证实解决完整模组组合的提示框动画崩溃。

Replaced invalid negative add_gold effects in 31 Caucasus event options with native remove_short_term_gold. Added the rite definition's UTF-8 BOM and tightened validation. Includes the DDS fix from expanded.3.1; the full-playset startup crash remains unconfirmed resolved.

# RICE Expanded — expanded.3.1: DDS resource repair

2026-10-08 · CK3 1.20.* · 社区预发布 / Community prerelease

- 修复索科特拉印度洋家族传承图标错误的 DDS mipmap 数：128×128 图标实际包含八级数据，却声明了九级。只修正文件头，所有像素数据保持不变。
- 增加 DDS 文件头、mipmap 级数及数据长度检查；全套 1,994 个纹理通过检查。更新包工具现在也纳入制作目录之外的既有 RICE 文件修复。
- 此修复针对日志中确认的资源错误。Expanded 的提示框动画崩溃与原版 RICE 的决议控件崩溃是不同调用栈；不声称仅凭静态检查已解决启动崩溃。

Corrected an invalid mip count in the existing Socotra dynasty-legacy icon without changing its pixels. DDS integrity checks cover all 1,994 textures. This fixes a logged resource error; the reported startup crash is not yet confirmed resolved.

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
