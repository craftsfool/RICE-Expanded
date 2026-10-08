# RICE Expanded：高加索与统一兼容包

expanded.3.7 继续使用一个完整的 **RICE Expanded Unified**。它可以单独启用；CE、EPE、CFP、VIET 和其他已核对模组均为可选项。高加索内容、文化依赖和兼容处理直接内置于 `RICE/`，不需要额外的高加索包或 RICE＋CE／RICE＋EPE 补丁。请停用旧的独立 RICE 补丁，并将 Expanded 排在文化、人物外观和地图模组之后。已有 expanded.3.5 的安装在覆盖新文件后，必须移除旧的 `RICE/common/religion/tenet_types/00_tenet_types.txt`；本机已处理。

这是针对 CK3 1.20.* 的社区 Alpha。RICE 原作者为 cybrxkhan，craftsfool 负责此次整合发布，使用 Codex 协助制作。原 README 保持不变。

## 文化、地图与建国

内置 CE 的 Circassian、Udi、Dagestani、Abkhaz、Laz、Svan、Tat、Alan 八个文化及相关姓名、传统、语言、传承依赖。人物外观使用可独立加载的原版资源；EPE 可以同时启用，统一包不依赖 EPE 的独有资产名称。

默认游戏规则在新开局应用 CE 的高加索分布：867、1066、1178 共 59 条县级操作，以及 23 位既有人物的 65 条文化操作。启用 CE 时交给 CE 自己初始化；未启用 CE 时 Expanded 自行完成。可在游戏规则中关闭文化分布调整。此项在开始战役时执行，**不会把旧存档已经建立的文化分布重新改写，也不保证开局选择界面的预览地图变化**。

CE 的外高加索帝国决议与事件已内置。未启用 CE 时可用“建立外高加索帝国”；启用 CE 时保留 CE 原决议。它要求首都位于外高加索区域，独立、非部落、国王或更低级别的统治者完整控制相应地区并满足声望、资金等条件，不会对世界各地的角色开放。建立帝国时才调整法理归属。亚美尼亚本来就是原版 RICE 胭脂虫产区，本次没有缩小其地区条件。
原版草原扩张的高加索区域比外高加索帝国决议所用区域多阿塞拜疆公国，因此帝国决议保留独立的南高加索范围。事件广播范围则引用原版扩张区域，并补入北高加索四公国；这两个自定义区域都已补齐英、简中、法文名称。

兼容文件保留所借用 CE 文件中的其他记录，并补齐依赖，避免整文件覆盖删除对象。鄂温克文化和姓名表与北太平洋地图扩展使用相同的文件名，消除双重注册。所有源文件指纹与外观回退记录保存在 `reports/`。六个原有 ROA／TFE 可选传承引用仍在对应的兼容条件之后；不把可选引用警告伪装成完整引擎验证。

## 人物与故事

- **杰尔宾特罗斯近卫**：当地领主接见信奉斯拉夫真理教、属于东斯拉夫传承的罗斯队长，军事 26、勇武 32。勇敢、侠义与满级剑术经验使原版护卫称职度达到 91；即使有原版宫廷政治的 −10 惩罚，仍达到极佳的 80 门槛。可以聘他为贴身护卫并获得 500 名事件兵，或只雇用 500 名战士。职位已满或原版职位不可用时，不会撤换现任护卫。宗教争端改变队长对领主的态度；部队合同与队长的宗教待遇分开处理。
- **洛里教会争论**：亚美尼亚院长与正教使者当面争论译文和教会自主权。玩家能延请其中的学者、接受语言教导、撤回有争议的措辞，最后保存一本实际的《洛里论辩录》宝物，或留下教师。前面的立场决定最终协议。
- **阿尼圣所归属**：基督徒管理人与穆斯林代表携钥匙、契据和修缮要求登场。裁决保存建筑用途，两位代表可以留在宫廷；安置迁出的会众影响人物态度和地方秩序。不会因改变一座建筑的用途而强制全县改宗。
- **阿兰传教与反弹**：正教传教士和阿兰长老争论土地与誓约。可延请教师、接纳地方长老或获得 100 名轻骑兵。界桩纠纷记住先前的拨地；结尾可选择亲自受洗，或保留自身信仰。不会自动转换整个阿兰地区。
- **通德拉基派（expanded.3.7）**：867 开局约一年后由斯姆巴特创建礼仪，并调用原版 `faith_creation.1021` 新礼仪通知。阿帕胡尼克及信仰、领主均符合条件的邻县改奉礼仪；玩家不会被强制改信。南、北高加索的基督教统治者首先收到证词，可以选择继续听证；只有参与者会收到土地争议和教会禁令，并决定自己宫廷的立场。斥责异端者获得100虔诚并停止接收中间广播，所有人仍会收到最终裁决。加入使用原版领主、领地和宫廷改信效果；亚美尼亚国王旗下封臣的加入权重为普通领主的8倍。发源地无人能主持调查时仍有地区消息链；实际调查开始后，由调查结果接管广播。1066／1178 开局立即生成礼仪。旧档不再执行可能造成无限拆分的母信仰重设。

斯姆巴特·扎雷哈万齐按原版历史异端模板生成，由他本人创建并改奉通德拉基礼制。文化为亚美尼亚；Zarehavantsi 是籍贯称号，宗族未获明确证实，故不虚构贵族谱系。模板人生时间随游戏触发年安排，不声称历史人物实际活到了后期剧本。首次创立者、地点、年份的引用永久保留；其死亡后由追随者继续出场，描述中的姓名仍可打开原人物。

通德拉基礼仪定义在亚美尼亚宗徒教会之下。核心信条为反圣像、公有财产与米亚菲西特主义；第三条与原版亚美尼亚礼仪一致，无相应DLC时回退为禁欲主义。男女平等、男女神职及男女私通获准；神权教会、终身教会指认，并允许修道。expanded.3.6已删除自动重设母信仰的循环触发点，也不再整文件覆盖原版信条；但礼仪实际差异度及旧档现存空信仰仍需游戏引擎验证。

原有 22 个地方场景也有反复出现的监工、学者或工匠，并可留下实际人物或书册。地方修缮、机构与最终协议仍以县级修正记录，但不再让宗教故事每一步只增删临时数值。25 个新增修正全部引用实际存在的原版图标，通过 `positive`／`negative` 后缀显示绿／红图标与名称；混合效果中的负值仍按原版显示。

## 本地化、美术与验证

高加索全部 **889** 条制作内容提供英／简中／法语，Derbent 中文使用“杰尔宾特”，其余五种语言保留明确的英文回退。另借用的 CE 依赖标签使用可取得的 CE 或原版译文，其缺失翻译保留英文并单独记录；这不表示整个 CE 或 RICE 已完成中法翻译。

杰尔宾特决议使用原创横幅；通德拉基图标为透明红色碎裂亚美尼亚十字架。其他场景、修正与书册使用原版资源。

检查包括六种实际文件组合：独立、EPE、CE、CE＋EPE，以及带 CFP、VIET、北太平洋地图、Cultural Armies、Cadet Branch 和 CFP＋EPE 补丁的两组。582 条宗教故事路径、开局时间安排、人物保存与恢复、护卫称职度、500 名事件兵、费用、地区限制、文化依赖、三语变量标记和 1,994 个 DDS 均在后台检查。**未启动游戏，未接管桌面；脚本模型不等于实际引擎执行，界面渲染和长期平衡仍需实机观察。**

CE 来源为本地 Workshop 2829397295（1.19.0.6），EPE 为 2507209632（1.20.0.3）。感谢 Culture Expanded、EPE、RICE 作者和贡献者。具体史料、年代争议及人物来源见 `plans/Caucasus-Religious-Content-Plan.md` 与 `authoring/caucasus_flavor_pack/research/`；事件对话、地方纠纷与数值属于游戏创作。

# English installation note

Use the single **Unified** full package. RICE Expanded is self-contained; CE, EPE and the checked optional mods are not required. Load it after culture, portrait and map mods; disable old separate RICE compatibility patches. Start a new campaign to obtain the migrated Caucasus starting cultures. Existing saves retain their established distribution.

The character-led stories provide a Rus captain and exactly 500 event soldiers, court teachers, actual manuscripts, Ani’s competing religious representatives, Alan riders and an optional personal baptism. The Tondrakian outbreak is scheduled around one year into an 867 campaign with a succession fallback. Later starts initialize the branch immediately; it appears among the Armenian Apostolic rites, rather than as a duplicate independent faith. All 878 authored Caucasus keys have English, Chinese and French text. Additional CE dependency labels may use English fallbacks.

Validation is static and scripted. The game and desktop were not controlled. This community alpha does not claim universal mod compatibility or verified engine rendering.

expanded.3.5修复另有8组广播地域对照与旧档／县级改信／原版通知作用域检查。检查只覆盖脚本与静态资源，没有验证本次改动在引擎中的执行或界面呈现。
