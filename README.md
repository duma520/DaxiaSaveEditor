# 软件截图 v1.5.1

<img width="1442" height="932" alt="image" src="https://github.com/user-attachments/assets/439cd15d-21ea-4c1c-ae81-a3e87998c07f" />

<img width="1442" height="932" alt="image" src="https://github.com/user-attachments/assets/fbdb046f-587e-4779-a2cd-c608f6da6f75" />

<img width="1442" height="932" alt="image" src="https://github.com/user-attachments/assets/019f53d4-24d9-4e3b-b1c1-a5b832ecf29e" />

<img width="1442" height="932" alt="image" src="https://github.com/user-attachments/assets/1ed66479-52bb-4a19-b0d4-f95dc06ef3b0" />

<img width="1442" height="932" alt="image" src="https://github.com/user-attachments/assets/32728526-b034-4d71-9814-afd926ee118d" />

<img width="1442" height="932" alt="image" src="https://github.com/user-attachments/assets/296fe991-b473-4225-a75e-5e058cd875c1" />

# 大侠狂想曲 存档修改器 —— 从零基础到高级应用完全指南

**作者：杜玛**  
**版权：永久**  
**日期：永久**  
**邮箱：不提供**  
**开源许可证：AGPL-3.0**  
**GitHub：https://github.com/duma520**  
**网站：https://github.com/duma520**  
**项目地址：https://github.com/duma520/DaxiaSaveEditor**  
**问题报告：通过 GitHub Issues 提交**

**版权声明 © 永久 杜玛 保留所有权利**  
本文档内容随本仓库以 AGPL-3.0 发布，可自由转载与商用。  
注意：我们不提供私人邮箱支持，所有技术支持都通过公开渠道进行，以便其他用户也能受益。

**开发时间：2026-09-18**

## 目录

- [第一部分：写给所有人——3 分钟看懂这个工具](#第一部分写给所有人3-分钟看懂这个工具)
- [第二部分：零基础入门——从下载到第一次修改](#第二部分零基础入门从下载到第一次修改)
- [第三部分：界面详解——8 个页签每一个按钮都讲清楚](#第三部分界面详解8-个页签每一个按钮都讲清楚)
- [第四部分：按人群分类的使用指南](#第四部分按人群分类的使用指南)
- [第五部分：按职业/行业分类的应用场景](#第五部分按职业行业分类的应用场景)
- [第六部分：高级应用——数据层、逆向与二次开发](#第六部分高级应用数据层逆向与二次开发)
- [第七部分：专业说明——存档格式白皮书（技术版）](#第七部分专业说明存档格式白皮书技术版)
- [第八部分：安全、法律与伦理](#第八部分安全法律与伦理)
- [第九部分：常见问题（FAQ）——从入门到疑难杂症](#第九部分常见问题faq从入门到疑难杂症)
- [第十部分：版本更新简史——每个版本一句话](#第十部分版本更新简史每个版本一句话)
- [第十一部分：开发者文档——代码地图与维护约定](#第十一部分开发者文档代码地图与维护约定)
- [第十二部分：编译、打包与分发](#第十二部分编译打包与分发)
- [第十三部分：故障排查手册](#第十三部分故障排查手册)
- [第十四部分：术语表](#第十四部分术语表)
- [第十五部分：附录——文件清单与快速索引](#第十五部分附录文件清单与快速索引)

# 第一部分：写给所有人——3 分钟看懂这个工具

## 1.1 这是什么？

**大侠狂想曲 存档修改器**是一个免费、开源的小工具，用来修改单机游戏《大侠狂想曲》的存档文件。

你可以用它：

- 把金钱改成 999,999,999
- 给背包里加任何物品（武器、护甲、丹药、种子、配方……）
- 把武学全部学会、全部满级
- 把 NPC 好感度全部拉满
- 把任务全部标记为已完成
- 让农田里的作物瞬间成熟
- 解锁全部场景
- ……以及更多

**一句话总结：它是一个“游戏存档的记事本 + 计算器 + 批量编辑器”。**

## 1.2 它不是什么？

- **不是外挂**：它不注入游戏进程、不修改游戏内存、不联网、不绕过任何反作弊。
- **不是盗版工具**：它不包含游戏本体，不破解游戏，不提供下载。
- **不是在线服务**：它完全离线运行，不收集你的任何数据，不联网上传任何东西。
- **不是万能修改器**：它只能改存档里**已经存在**的字段；游戏不存的东西（比如“内力上限”）它改不了。

## 1.3 为什么需要它？

《大侠狂想曲》是一个 Unity 引擎做的单机游戏，存档是明文 JSON 文件。理论上你用记事本也能改，但是：

- 存档是**单行紧凑 JSON**，47 个顶层字段，几万到几十万个字符挤在一行里，人眼根本没法看。
- 物品有 **176 种**，NPC 有 **85 个**，场景有 **57 个**，任务有 **83+51 个**，全靠 ID 引用，你记不住。
- 浮点数必须**逐字节保真**，否则游戏可能读不了。
- 删物品时如果它正被手持/装备，还得**同步清理引用**，否则存档会出问题。

这个工具就是把这些麻烦事全部包好，给你一个中文图形界面，点几下就完事。

## 1.4 它的核心原则

| 原则 | 含义 |
|---|---|
| **安全第一** | 每次保存前自动备份；原子写盘；回读校验；浮点保真 |
| **不打扰用户** | 游戏开着也能保存；只在右下角安静显示一行小字；不弹窗拦截 |
| **诚实** | 改不了的东西就说改不了（比如内力上限），不猜、不硬塞 |
| **开源** | AGPL-3.0 许可证，代码全公开，随便看、随便改、随便分发 |
| **离线** | 不联网、不上传、不收集任何信息 |

# 第二部分：零基础入门——从下载到第一次修改

## 2.1 你需要准备什么？

### 2.1.1 如果你拿到的是“打包好的 exe 版本”

你只需要：

- 一台 Windows 电脑（Windows 10 或 Windows 11 都行）
- 《大侠狂想曲》游戏本体（已经玩过，至少有一个存档）
- 本工具解压后的文件夹

**不需要**安装 Python，**不需要**安装任何运行库，**不需要**联网。

### 2.1.2 如果你拿到的是“源代码版本”

你需要：

- Windows 电脑
- Python 3.10.11（推荐这个版本，其他 3.10.x 也行）
- PySide6 6.11.0（Qt6 的 Python 绑定）

安装命令（在命令行里运行）：

```bat
python -m pip install PySide6==6.11.0
```

### 2.1.3 不管哪种版本，你都需要知道存档在哪

默认路径是：

```
<游戏安装目录>\大侠狂想曲_Data\Data\Save\
```

里面会有：

```
save0player.json   ← 槽 1 的主存档
save0.txt          ← 槽 1 的玩家名/进度/时间
save0.png          ← 槽 1 的截图
save1player.json   ← 槽 2
save1.txt
save1.png
save2player.json   ← 槽 3
save2.txt
save2.png
save3player.json   ← 槽 4
save3.txt
save3.png
```

**N = 0~3，对应游戏里的存档槽 1~4。**

## 2.2 第一次启动

### 2.2.1 exe 版本

双击 `DaxiaSaveEditor.exe`。

### 2.2.2 源代码版本

双击 `1.bat`，或者在命令行里：

```bat
python DaxiaSaveEditor.py
```

### 2.2.3 启动后你会看到什么？

一个窗口，标题是「大侠狂想曲存档修改器 v1.5.1」。

- 顶部：一排按钮（打开存档、保存、设置……）
- 左侧：4 个存档槽的列表 + 存档截图 + 槽信息
- 右侧：8 个页签（基础属性、背包/工具栏、武学/配方、NPC/剧情、任务、农场/建造、世界/杂项、高级）
- 底部右下角：可能有一行灰色小字「游戏运行中（PID xxxxx）」，不用管它。

## 2.3 第一次修改（手把手）

**目标：把金钱改成 999,999,999。**

1. **看左侧**：找到你想改的那个存档槽（比如「槽1」），点一下。
   - 如果槽里有存档，会显示玩家名、金钱、等级、场景、物品条数。
   - 如果显示「（空存档）」，说明这个槽没存档，换一个。
2. **看右侧**：点「基础属性」页签 → 点「一键修改」子页签。
3. **点按钮**：点「金钱 999,999,999」。
4. **看标题栏**：标题会多一个 `*`，状态灯变红，表示有未保存的修改。
5. **保存**：按 `Ctrl+S`，或者点工具栏「保存」。
6. **确认**：如果弹确认框，点「是」。
7. **看弹窗**：会显示「保存成功！」+ 文件路径 + 回读校验结果 + 「回游戏里读档即可」。
8. **回游戏**：启动游戏，读档，看金钱。

**恭喜，你完成了第一次修改。**

## 2.4 修改前必读：三条铁律

### 铁律 1：先备份，再修改

工具每次保存前会自动备份到 `backups\` 目录，最多保留 30 份。但如果你想更保险，可以手动点「备份当前」。

### 铁律 2：改的是哪个槽，就在游戏里读哪个槽

如果你改了「槽1」，游戏里就要读「存档1」。改错槽是新手最常见的错误。

### 铁律 3：改完保存，回游戏里读档

不需要关游戏（v1.4.0 起不再拦截），但**如果游戏里没看到变化**，先试试重启游戏再读档。

## 2.5 撤销修改

如果你改错了，有两种撤销方式：

| 方式 | 操作 | 效果 |
|---|---|---|
| **重新载入** | 点工具栏「重新载入」（Ctrl+R） | 放弃内存里所有未保存的修改，重新从磁盘读 |
| **还原备份** | 高级 → 备份管理 → 选中一个备份 → 还原到存档槽 | 把之前自动备份的文件还原回去 |

**注意**：「重新载入」只能撤销**还没保存**的修改。如果你已经保存了，只能用备份还原。

# 第三部分：界面详解——8 个页签每一个按钮都讲清楚

## 3.1 顶部工具栏

| 按钮 | 快捷键 | 作用 | 什么时候用 |
|---|---|---|---|
| **状态灯** | — | 灰=未打开；绿=已保存；红=有未保存修改 | 一眼看状态 |
| **打开存档…** | Ctrl+O | 手动选一个 `saveNplayer.json` | 自动找不到存档时 |
| **重新载入** | Ctrl+R | 放弃未保存修改，重新读盘 | 改乱了想重来 |
| **保存** | Ctrl+S | 写回原文件；写前自动备份 + 确认 | 改完就点 |
| **另存为…** | Ctrl+Shift+S | 存到其它路径 | 想保留原档做对比 |
| **备份当前** | — | 立刻复制一份到 `backups\` | 大改之前手动备份 |
| **刷新列表** | — | 重扫 4 个存档槽 | 游戏里存了新档之后 |
| **设置…** | — | 存档目录 / 备份份数 / 确认开关 | 第一次用先设置 |
| **使用说明** | — | 内置帮助 | 忘了怎么用 |
| **关于** | — | 版本信息 | 报 bug 时看版本 |

**重要**：工具栏右侧会显示当前打开的存档路径。如果路径太长，鼠标悬停可以看完整路径。

## 3.2 左侧面板

### 3.2.1 存档槽列表

显示 4 个槽，每个槽显示：

- 槽号
- 玩家名
- 金钱（¥ 开头）
- 等级（Lv 开头）
- 场景名
- 物品条数 / 种类数
- 保存时间

**点击任意一个槽，就会载入那个存档。**

如果当前有未保存的修改，会先问你「确定放弃并打开？」。

### 3.2.2 存档预览

显示 `saveN.png` 游戏截图。如果游戏没生成截图，显示「（无截图）」。

### 3.2.3 槽信息

显示：

- 槽号
- 文件大小（KB）
- 物品条数 / 种类数
- 进度摘要（`saveN.txt` 第 2 行）
- 保存时间
- 文件名

## 3.3 页签 1：基础属性

这个页签有 3 个子页签。

### 3.3.1 子页「角色与状态」

**角色区：**

| 字段 | 含义 | 建议值 |
|---|---|---|
| 姓名 | 玩家名（PlayerName） | 随便改，别太长 |
| 金钱 | Money | 999,999,999 |
| 经验 | Experience | 999,999,999 |
| 熟练度 | Proficiency | 999,999,999 |
| 等级 | level | 99（别太夸张） |
| 农场等级 | farmLevel | 99 |

**状态区：**

| 字段 | 含义 | 建议值 |
|---|---|---|
| 当前HP | currentHP | 999999 |
| 当前MP | currentMP | 999999 |
| 疲劳 Tired | 疲劳度 | 0 |
| 快捷槽 BaltSlot | 快捷栏位 | 0 |
| 奔跑状态 isRun | 是否奔跑 | 随意 |
| 睡觉中 Sleep | 是否在睡觉 | 随意 |

**HP / MP 的上限说明区（★ v1.5.0 新增）：**

这里有一段灰字说明，讲清楚三件事：

1. 存档里没有「最大 HP / MP」字段。
2. 最大生命 = 游戏基础值 + 身上装备的 `property.maxHP` 之和。
3. 内力上限没有可写字段，改不了。

下面有一个按钮「一键设置装备生命上限 maxHP…」，点开可以批量设置。

### 3.3.2 子页「时间与位置」

**时间区：**

| 字段 | 含义 |
|---|---|
| activeTime | 游戏活跃计时（秒级计数器） |
| sleepTime | 睡觉计时 |
| GameTime[0..2] | 游戏时间 |

**位置区：**

| 字段 | 含义 |
|---|---|
| 当前场景 PlayerScene | 57 个场景下拉，可编辑 |
| PlayerLocation.x/y/z | 坐标（浮点） |

### 3.3.3 子页「一键修改」

一排按钮：

- 金钱 999,999,999
- 经验 + 熟练度拉满
- HP / MP 当前值拉满
- 全部一键最大
- 清零疲劳
- 装备生命上限…

下面有一段说明文字，解释「当前值」和「上限」的区别。

## 3.4 页签 2：背包 / 工具栏

这个页签有 2 个子页签。

### 3.4.1 子页「背包 bagitems」

显示背包全部物品，列：

`# / 物品名 / ID / 数量 / 类型 / 攻击 / 防御 / 暴击 / 闪避 / 移速 / HP / UUID`

**按钮：**

| 按钮 | 作用 |
|---|---|
| ＋ 添加物品… | 打开物品选择对话框 |
| － 删除选中 | 删除选中的行（可多选） |
| 数量改为… | 把选中行的数量改成指定值 |
| 编辑物品… | 编辑单件物品的详细属性 |
| 一键满数量 | 把选中行数量设为 2,100,000,000 |
| 清空该列表 | 清空整个背包 |
| 装备生命上限… | 批量设置所有装备的 maxHP |

**物品选择对话框：**

- 左侧是分类树（武器/护甲/饰品/功法/心法/食物/丹药/种子/……）
- 顶部有搜索框（支持中文名、拼音、ID，多个关键字空格分隔）
- 支持多选
- 可以设置数量
- 已有物品会显示灰色「已有」标签

**同 ID 物品已存在时自动叠加数量，不新建重复条目。**

### 3.4.2 子页「工具栏 toolitems」

和背包完全一样的操作，但对应的是游戏固定的 10 格工具栏。

**注意**：工具栏超过 10 格可能不被游戏识别。

## 3.5 页签 3：武学 / 配方

这个页签有 3 个子页签。

### 3.5.1 子页「已学武学 list_skill」

字段格式：`[{x: 功法物品ID, y: 等级}]`

**按钮：**

- ＋ 添加武学…（只列 16 门 GongFa/XinFa）
- － 删除选中（会同步清掉出招栏里的引用）
- 等级改为…
- 一键全部满级(4)

### 3.5.2 子页「出招栏 list_skillRun」

6 个下拉格，`0` = 空。选择功法物品 ID 即可。

### 3.5.3 子页「配方 list_recipe」

菜谱/配方/图纸的物品 ID 列表。

**按钮：**

- ＋ 添加配方…
- － 删除选中
- 全部学会

## 3.6 页签 4：NPC / 剧情

这个页签有 4 个子页签。

### 3.6.1 子页「NPC 好感」

字段：`list_npcFavorItem`，格式 `[{npcID, favorCount, activeDialogueID, favorEvents}]`

**按钮：**

- ＋ 添加 NPC…（带搜索的 NPC 列表）
- － 删除选中
- 好感改为…
- 全部 999

### 3.6.2 子页「已触发对话」

字段：`activeDialogues`，格式 `[{dialogueID, overTime}]`

**按钮：**

- ＋ 添加对话ID…（手动输入，多个用逗号/空格分隔）
- － 删除选中
- 全部清空（**会让剧情重新触发，有二次确认**）
- 筛选框（按 ID 筛选）

### 3.6.3 子页「送礼 / 交谈记录」

字段：`list_giftSend` · `list_talk`，格式 `[{x: NPC ID, y: 值}]`

**按钮：**

- ＋ 添加…
- － 删除选中
- 下拉切换查看 `list_giftSend` / `list_talk`

### 3.6.4 子页「点击事件」

字段：`clickEvents`，格式 `[{type, clickCount}]`

**按钮：**

- 次数改为…

## 3.7 页签 5：任务（单页）

字段：`taskinfos`，格式 `[{taskID, state, startTime, overTime}]`

- 状态：`0 未开始 / 1 进行中 / 2 已完成`
- 表格显示章节名

**按钮：**

- ＋ 添加任务…（章节列表）
- － 删除选中
- 状态改为…
- 开始/结束时间改为…
- 全部标记「已完成」

## 3.8 页签 6：农场 / 建造

这个页签有 2 个子页签。

### 3.8.1 子页「农田 farmitems」

字段：`farmitems`，格式 `[{uuid, pos, seedTime, waterTime, freeTime, farm}]`

**按钮：**

- － 删除选中地块
- 清空全部农田
- 全部立即成熟（`seedTime = waterTime - growTime - 1`）
- 全部浇水（`waterTime = 当前 activeTime`）
- 批量设置时间（3 个输入 + 应用于选中）

### 3.8.2 子页「建筑 list_buildinfos」

字段：`list_buildinfos`，格式 `[{uuid, name(物品ID), pos}]`

**按钮：**

- － 删除选中建筑

## 3.9 页签 7：世界 / 杂项（单页）

**已激活场景 activeScene：**

- ＋ 添加场景…（场景库 57 个）
- － 删除选中
- 解锁全部场景

**一键清空：**

- 制作队列 makeCraftInfos
- 装备引用 list_equipment
- 已破坏物件 scenesDestroyID
- 已点击对象 list_clickedObj

**统计显示：**

`ListScene` / `Marker` / `ListMemory` / `Bounty` 等列表长度。

**手动改数值：**

`Equipment`(4 项) / `Perk`(6 项) / `BaltSlot` / `Tired`

## 3.10 页签 8：高级

这个页签有 2 个子页签。

### 3.10.1 子页「JSON 文本编辑」

- 从当前数据刷新文本
- 应用文本（JSON 校验后写入内存）
- 格式化（缩进显示）
- 校验存档完整性

**校验项：**

- JSON 合法性
- 关键字段齐全
- 数值字段类型
- 物品 ID 是否在物品库
- 装备引用是否有效

### 3.10.2 子页「备份管理」

- 列出 `backups\`
- 还原到指定存档槽（还原前自动再备份）
- 删除
- 打开备份目录

## 3.11 特殊对话框

### 3.11.1 ItemEditDialog（编辑物品）

编辑单条物品记录：

- 数量 count
- 物品 level
- uuid
- 装备属性 property（11 项：minAttack / maxAttack / attack / minArmor / maxArmor / armor / crit / critHit / moveSpeed / dodge / maxHP）

### 3.11.2 EquipMaxHpDialog（装备生命上限）

批量把「所有装备」的 `property.maxHP` 设成同一个值。

- 显示当前各装备 maxHP 的最小/最大/总数
- 输入新值
- 勾选框「顺便把当前 HP 也设成同一个值」

### 3.11.3 ItemPickDialog（物品选择）

分类树 + 搜索 + 多选 + 数量。

### 3.11.4 SimplePickDialog / NpcPickDialog / TaskPickDialog

通用「带搜索的多选列表」对话框，分别用于场景、NPC、任务。

# 第四部分：按人群分类的使用指南

## 4.1 给完全不懂电脑的小白

**你只需要记住三件事：**

1. **双击 exe，点左边一个槽，点右边一个按钮，按 Ctrl+S，回游戏读档。**
2. **如果改错了，点「重新载入」或者去「高级 → 备份管理」还原。**
3. **不确定的按钮不要点，特别是「清空」「全部删除」这种。**

**推荐你先试这几个最安全的修改：**

- 基础属性 → 一键修改 → 金钱 999,999,999
- 基础属性 → 一键修改 → 经验 + 熟练度拉满
- 基础属性 → 一键修改 → 清零疲劳

**这三个改完，游戏体验会好很多，而且不会出问题。**

## 4.2 给普通玩家

**你已经会玩游戏了，想省点时间。**

推荐流程：

1. 先手动玩到一定程度，知道游戏里缺什么。
2. 用工具补上缺的东西：
   - 缺钱 → 一键金钱
   - 缺材料 → 背包添加
   - 想学全武学 → 武学页一键满级
   - 想刷好感 → NPC 页全部 999
   - 想推剧情 → 任务页全部完成
3. **不要一次改太多**，改完保存，回游戏看看，再继续。

**进阶技巧：**

- 用「另存为…」保存不同阶段的存档，方便回滚。
- 用「备份当前」在大改之前手动备份。
- 用「高级 → JSON 文本编辑」看存档长什么样，了解游戏数据结构。

## 4.3 给硬核玩家 / 速通玩家

**你要的是精确控制。**

推荐做法：

1. **直接用「高级 → JSON 文本编辑」**，因为你知道自己要什么。
2. 用「校验存档完整性」确认改完的存档没问题。
3. 用「另存为…」保存不同阶段的存档，做速通路线对比。
4. 用 `_scaffold\diff_save.py`（开发者脚本）对比两个存档的差异。

**速通常用修改：**

- 金钱拉满（省去赚钱时间）
- 经验/熟练度拉满（省去练级时间）
- 武学全部满级（省去练武时间）
- 全部场景解锁（省去跑图时间）
- 农田全部立即成熟（省去等待时间）
- 任务全部完成（跳过某些任务链）

## 4.4 给游戏 MOD 制作者

**你想基于这个工具做二次开发。**

推荐做法：

1. 先读第七部分「存档格式白皮书」，理解存档结构。
2. 再读第十一部分「开发者文档」，理解代码结构。
3. 用 `_scaffold\` 下的脚本做数据探查。
4. 所有数据操作写成**模块级纯函数**（见第五章），GUI 只负责取值/展示。
5. 改完必须跑冒烟测试：`python -u _scaffold/smoke_test.py`。

**注意：**

- 游戏更新后，`resources.assets` 里的数据表可能变化，需要重新跑 `extract_assets_json.py` + `build_libs.py`。
- 浮点保真必须用 `RawFloat` + `_enc_json()`，不要直接用 `json.dumps`。

## 4.5 给 Python 初学者

**你想学 Python，顺便看看这个项目怎么写的。**

推荐阅读顺序：

1. 先看 `DaxiaSaveEditor.py` 第 1~150 行（常量、路径、图标）。
2. 再看第 543~625 行（`RawFloat` / `_enc_json` / `read_save` / `write_save`）——这是最核心的存档读写。
3. 再看第 731~951 行（纯数据操作层）——这是与 GUI 解耦的数据操作。
4. 再看第 1356 行开始的 `MainWindow.__init__`——这是主窗口。
5. 最后看各个 `create_XXX_tab()`——这是各个页签的构造。

**学到的知识点：**

- PySide6（Qt6）的基本用法
- JSON 序列化与浮点保真
- Win32 API 进程枚举（ctypes）
- GUI 与数据层分离的设计模式
- 原子写盘（tmp + os.replace）
- 冒烟测试的写法

## 4.6 给专业软件工程师

**你想评估这个项目的代码质量。**

**优点：**

- 数据层与 GUI 层分离，纯函数可测试。
- 浮点保真处理得当（`RawFloat`）。
- 原子写盘 + 回读校验 + 自动备份，安全机制完善。
- 进程检测用 Win32 API，不用 `tasklist`（避免卡死）。
- 有 187 项冒烟测试。
- 文档与代码同步更新（`软件升级迭代记录.md`）。

**可改进之处：**

- 主程序单文件 3939 行，可以拆成多个模块。
- 部分方法较长（如 `create_world_tab`），可以进一步拆分。
- 测试是自定义冒烟测试，不是 pytest/unittest，可以迁移。
- 没有类型注解（type hints），可以加。
- 没有 CI/CD，可以加 GitHub Actions。

**架构概览：**

```
┌─────────────────────────────────────────┐
│  GUI 层（MainWindow + 各 Dialog）        │
│  - 只负责取值/展示                       │
│  - 不直接操作 doc，通过纯函数            │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  纯数据操作层（模块级函数）               │
│  - bag_add / bag_delete / set_maxhp_all │
│  - list_add_ids / list_remove_pairs ...  │
│  - 可独立测试                            │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  存档读写层（RawFloat / read_save ...）   │
│  - 浮点保真                              │
│  - 原子写盘                              │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  数据表库（data/*.json）                  │
│  - 物品库 / 装备属性库 / 配方库 ...       │
└─────────────────────────────────────────┘
```

## 4.7 给项目经理 / 技术主管

**你想评估这个项目能不能用于生产。**

**结论：可以，但要注意以下几点。**

| 维度 | 评估 |
|---|---|
| **许可证** | AGPL-3.0，商用友好 |
| **依赖** | Python 3.10.11 + PySide6 6.11.0，依赖少 |
| **平台** | 目前仅 Windows（进程检测用 Win32 API） |
| **测试** | 187 项冒烟测试，覆盖数据层/GUI/进程检测/保存 |
| **文档** | 非常完善（`软件升级迭代记录.md` + 本说明书） |
| **安全** | 自动备份 + 原子写盘 + 回读校验 + 浮点保真 |
| **可维护性** | 单文件 3939 行，需要一定时间理解 |
| **风险** | 游戏更新后数据表可能失效，需要重新生成 |

**建议：**

- 如果要用于商业分发，保留 AGPL-3.0 许可证声明。
- 如果要修改代码，遵守第十一部分的维护约定。
- 如果要打包，用 `0_nuitka_pyside6_clang_auto.bat`。

## 4.8 给游戏主播 / 内容创作者

**你想直播/录视频用这个工具。**

推荐做法：

1. **先备份**，再直播修改，避免翻车。
2. **改前先讲清楚**：这是单机游戏，不联机，不影响他人。
3. **演示安全的修改**：金钱、经验、物品，不要演示删存档。
4. **展示备份还原**：让观众知道改错了也能救回来。
5. **展示回读校验**：让观众知道工具是真的写进去了。

**直播脚本建议：**

```
1. 打开工具，展示界面（30 秒）
2. 选中存档，展示当前状态（30 秒）
3. 改金钱 999,999,999，保存（1 分钟）
4. 回游戏读档，展示效果（1 分钟）
5. 改背包添加物品，保存（2 分钟）
6. 回游戏读档，展示效果（1 分钟）
7. 展示备份管理，说明可以还原（1 分钟）
8. 展示高级 JSON 编辑，说明可以精确控制（2 分钟）
```

## 4.9 给教师 / 学生（编程教学）

**你想用这个项目做教学案例。**

**适合教学的知识点：**

- JSON 序列化与反序列化
- 浮点数精度问题（0.1 + 0.2 != 0.3）
- GUI 编程（PySide6/Qt6）
- 文件 I/O 与原子操作
- 进程枚举（Win32 API）
- 测试驱动开发（冒烟测试）
- 代码重构（单文件 → 模块化）

**教学建议：**

1. 先让学生用工具改存档，理解需求。
2. 再让学生读代码，理解实现。
3. 最后让学生改代码，加一个新功能（比如「一键解锁全部配方」）。

## 4.10 给逆向工程师

**你想了解这个游戏的存档格式。**

直接看第七部分「存档格式白皮书」。关键结论：

- 存档是**单行紧凑 JSON、UTF-8 无 BOM、无换行**，47 个顶层字段。
- 浮点用 **17 位有效数字**（Unity 的 double 序列化）。
- 物品 ID 范围 **1000~1228**，NPC ID 范围 **1~1085**，两套 ID 体系**数值区间重叠**，不要互相套用。
- **最大 HP/MP 不存存档**，只有当前值；最大生命 = 基础值 + 装备 `property.maxHP` 之和；**maxMP 没有可写字段**。
- 数据表来自 `resources.assets` 里的明文 JSON 文本资产，用括号配平扫描可完整抠出。

# 第五部分：按职业/行业分类的应用场景

## 5.1 学生党（时间少，想快速体验）

**痛点**：课余时间少，不想花几十小时练级刷钱。

**方案**：

- 金钱拉满 + 经验拉满 + 熟练度拉满 → 直接体验后期内容
- 武学全部满级 → 体验各种武功
- 场景全部解锁 → 不用跑图
- 任务全部完成 → 直接看结局

**注意**：一次改太多会失去游戏乐趣，建议先手动玩一遍再改。

## 5.2 上班族（下班放松）

**痛点**：每天只有 1~2 小时，不想浪费在重复劳动上。

**方案**：

- 金钱适度改（比如 100 万，不要 999,999,999）→ 够用但不破坏平衡
- 材料适度改 → 不用反复刷
- 农田全部立即成熟 → 不用等
- NPC 好感适度改 → 不用反复送礼

**建议**：把工具当成「时间加速器」，而不是「一键通关」。

## 5.3 退休玩家（喜欢慢慢玩）

**痛点**：喜欢慢慢体验，但某些设计太磨人。

**方案**：

- 只改「疲劳」→ 不用频繁睡觉
- 只改「农田时间」→ 不用等作物
- 只改「背包容量」→ 不用反复整理

**建议**：保留大部分游戏体验，只去掉最烦人的部分。

## 5.4 游戏测试员（QA）

**痛点**：需要测试各种边界情况，但正常玩法很难触发。

**方案**：

- 用「高级 → JSON 文本编辑」精确构造测试数据
- 用「校验存档完整性」验证存档合法性
- 用「备份管理」保存不同测试用例的存档
- 用 `_scaffold\diff_save.py` 对比测试前后的差异

**测试用例示例：**

| 测试项 | 构造方法 | 预期结果 |
|---|---|---|
| 金钱溢出 | Money = 2147483647 | 游戏正常显示或截断 |
| 背包满 | bagitems 添加 1000 条 | 游戏正常或卡顿 |
| 未知物品 ID | bagitems 添加 id=9999 | 游戏忽略或报错 |
| 装备引用失效 | list_equipment 加一个不存在的 uuid | 游戏忽略 |
| 空背包 | bagitems = [] | 游戏正常 |

## 5.5 游戏开发者（同行参考）

**痛点**：想看看别人怎么做存档修改器。

**参考点：**

- 浮点保真方案（`RawFloat`）—— 任何 Unity 游戏存档修改都适用
- 原子写盘方案（tmp + os.replace）—— 任何文件写入都适用
- 进程检测方案（Win32 CreateToolhelp32Snapshot）—— 任何 Windows 进程检测都适用
- GUI 与数据层分离 —— 任何 GUI 项目都适用
- 冒烟测试方案 —— 任何 Python 项目都适用

## 5.6 数据分析师

**痛点**：想分析游戏数据。

**方案：**

- 用 `_scaffold\extract_assets_json.py` 提取游戏内嵌 JSON
- 用 `_scaffold\build_libs.py` 生成数据表
- 用 Python 的 pandas/matplotlib 分析物品价格、属性分布、NPC 关系等

**可分析的问题：**

- 物品价格与属性的关系
- 装备属性的随机分布
- NPC 好感度与对话触发的关系
- 任务链的依赖关系
- 农作物生长时间与收益的关系

## 5.7 翻译/本地化人员

**痛点**：想翻译游戏文本。

**方案：**

- 用 `_scaffold\extract_assets_json.py` 提取所有文本资产
- 从中找出中文文本
- 翻译后替换
- 注意：这需要修改游戏本体，不是本工具的功能范围

## 5.8 安全研究员

**痛点**：想研究 Unity 游戏存档的安全性。

**方案：**

- 分析存档格式（JSON，无加密，无签名）
- 分析游戏如何读取存档（只在启动/载入时读一次）
- 分析游戏如何写回存档（内存数据整份写回）
- 分析存档篡改的检测机制（无检测）

**结论**：这个游戏的存档完全没有防篡改机制，任何 JSON 修改都会被接受。

## 5.9 法律从业者

**痛点**：想了解单机游戏修改的法律边界。

**要点：**

- 单机游戏修改存档，**通常不违法**（不涉及破解、不涉及盗版、不涉及联网作弊）。
- 但**可能违反游戏 EULA**（最终用户许可协议），具体看游戏条款。
- **不要分发修改后的游戏本体**，只分发修改器本身是合法的。
- 本工具采用 AGPL-3.0 许可证，允许自由使用、修改、分发。

## 5.10 其他行业

**任何需要「批量编辑 JSON 文件」的场景，都可以参考本工具的设计。**

比如：

- 配置文件批量修改
- 数据库导出/导入
- 游戏存档迁移
- 自动化测试数据构造

# 第六部分：高级应用——数据层、逆向与二次开发

## 6.1 数据层 API 参考

### 6.1.1 存档读写

```python
from DaxiaSaveEditor import read_save, write_save, dumps_save, RawFloat

# 读存档
doc, text = read_save("save0player.json")

# 修改
doc["Money"] = 999999999

# 写存档（自动原子替换）
write_save("save0player.json", doc)

# 序列化为字符串（保持浮点原文）
text = dumps_save(doc)
```

### 6.1.2 物品操作

```python
from DaxiaSaveEditor import (
    bag_add, bag_delete, field_fix_after_delete,
    make_bag_entry, make_property_for, bag_summary
)

# 添加物品（同 id 自动叠加）
added, stacked, failed = bag_add(doc, "bagitems", [(1207, 100), (1036, 50)])

# 删除物品（按索引）
uuids = bag_delete(doc, "bagitems", [0, 2, 5])

# 清理引用（手持/装备）
fixed = field_fix_after_delete(doc, uuids)

# 统计
kinds, total = bag_summary(doc, "bagitems")
```

### 6.1.3 列表操作

```python
from DaxiaSaveEditor import (
    list_add_ids, list_remove_ids,
    list_add_pairs, list_remove_pairs,
    list_add_dicts, list_remove_dicts
)

# 纯 id 列表
list_add_ids(doc, "list_recipe", [1001, 1002, 1003])
list_remove_ids(doc, "list_recipe", [1002])

# [{x, y}] 列表
list_add_pairs(doc, "list_giftSend", [(1004, 10), (1005, 20)])
list_remove_pairs(doc, "list_giftSend", [1004])

# [{taskID, ...}] 列表
list_add_dicts(doc, "taskinfos", [{"taskID": 1, "state": 2}], "taskID")
list_remove_dicts(doc, "taskinfos", [1], "taskID")
```

### 6.1.4 装备 maxHP

```python
from DaxiaSaveEditor import (
    iter_equip_entries, maxhp_list, set_maxhp_all
)

# 遍历所有装备
for field, idx, entry in iter_equip_entries(doc):
    print(field, idx, entry["item"]["name"])

# 读取现有 maxHP
vals = maxhp_list(doc)

# 批量设置
n = set_maxhp_all(doc, 1000)  # 所有装备 maxHP = 1000
n = set_maxhp_all(doc, 1000, only_nonzero=True)  # 只改原本有加成的
```

### 6.1.5 数据表查询

```python
from DaxiaSaveEditor import (
    item_lib, item_map, item_name,
    npc_lib, npc_map, npc_display_name,
    crop_lib, crop_map, scene_lib,
    chapter_lib, chapter_map, buff_lib,
    prop_lib_map, gongfa_items, recipe_items, weapon_items
)

# 物品
it = item_map()[1207]  # {"id": 1207, "name": "木剑", ...}
name = item_name(1207)  # "木剑"

# NPC
n = npc_map()[1004]
display = npc_display_name(1004)  # "阿婆(apo)"

# 农作物
c = crop_map()[1036]

# 场景
scenes = scene_lib()  # 57 个场景标识
```

## 6.2 逆向工程：如何探查游戏数据

### 6.2.1 探查存档结构

```python
# _scaffold/probe_structure.py
# 扫描存档所有键（含嵌套），输出顶层字段并集、物品/作物库、取值域
python -u _scaffold/probe_structure.py
```

### 6.2.2 提取游戏内嵌 JSON

```python
# _scaffold/extract_assets_json.py
# 从 resources.assets 里抠出所有内嵌 JSON 到 assets_json/
python -u _scaffold/extract_assets_json.py
```

### 6.2.3 生成数据表

```python
# _scaffold/build_libs.py
# 由 assets_json/ 生成 data/*.json（含 NPC 名字还原）
python -u _scaffold/build_libs.py
```

### 6.2.4 探查 HP/MP 上限

```python
# _scaffold/probe_hpmp.py  —— 扫存档所有键
# _scaffold/probe_hpmp2.py —— 扫 777 个数据表键名
python -u _scaffold/probe_hpmp.py
python -u _scaffold/probe_hpmp2.py
```

### 6.2.5 追踪背包变化

```python
# _scaffold/trace_bag.py
# 把所有备份按时间线排列，逐版本列出背包增/删/改
python -u _scaffold/trace_bag.py
```

## 6.3 二次开发：加一个新功能

**目标：加一个「一键解锁全部配方」按钮。**

### 步骤 1：写纯函数

```python
def unlock_all_recipes(doc):
    """解锁全部配方，返回新增个数。"""
    from DaxiaSaveEditor import recipe_items, list_add_ids
    return list_add_ids(doc, "list_recipe", [it["id"] for it in recipe_items()])
```

### 步骤 2：加 GUI 按钮

在 `_recipe_page()` 里加：

```python
b = QPushButton("全部学会")
b.clicked.connect(self.on_recipe_all)
row.addWidget(b)
```

`on_recipe_all` 已经有了，不用改。

### 步骤 3：写测试

在 `_scaffold/smoke_test.py` 里加：

```python
def test_unlock_all_recipes():
    doc = {"list_recipe": []}
    n = unlock_all_recipes(doc)
    assert n == len(recipe_items())
    assert len(doc["list_recipe"]) == len(recipe_items())
```

### 步骤 4：更新文档

- 更新 `软件升级迭代记录.md` 的「一、迭代记录」
- 更新「二、功能清单」
- 更新「三、代码地图」
- 更新 `DaxiaSaveEditor.py` 第 2 行的 `__version__`
- 备份到 `version\`

### 步骤 5：跑测试

```bat
python -u _scaffold/smoke_test.py
```

## 6.4 二次开发：加一个新数据表

**目标：加一个「怪物库」。**

### 步骤 1：提取数据

```python
# 在 _scaffold/build_libs.py 里加
monsters = extract_monsters()
save_lib("怪物库.json", "monsters", monsters)
```

### 步骤 2：加加载函数

```python
def monster_lib():
    return _load_lib("怪物库.json", "monsters")

def monster_map():
    ck = ("monster_map",)
    if ck not in _LIB_CACHE:
        _LIB_CACHE[ck] = {m["id"]: m for m in monster_lib()}
    return _LIB_CACHE[ck]
```

### 步骤 3：加 GUI

在合适的页签里加表格和按钮。

### 步骤 4：加打包参数

在 `0_nuitka_pyside6_clang_auto.bat` 里加：

```bat
--include-data-files=data/怪物库.json=data/怪物库.json ^
```

### 步骤 5：更新文档 + 测试

同 6.3。

## 6.5 脚本化使用（不启动 GUI）

```python
# 直接用数据层 API，不启动 GUI
from DaxiaSaveEditor import read_save, write_save, bag_add, set_maxhp_all

doc, _ = read_save("save0player.json")
doc["Money"] = 999999999
bag_add(doc, "bagitems", [(1207, 100)])
set_maxhp_all(doc, 1000)
write_save("save0player.json", doc)
```

**注意**：脚本化使用不会自动备份，请手动备份。

# 第七部分：专业说明——存档格式白皮书（技术版）

## 7.1 文件组成

游戏存档目录：`<游戏>\大侠狂想曲_Data\Data\Save\`

| 文件 | 内容 |
|---|---|
| `saveNplayer.json` | **主存档**：单行紧凑 JSON，UTF-8 **无 BOM**，**无换行符**，47 个顶层键 |
| `saveN.txt` | 3 行 UTF-8 + CRLF：`玩家名` / `进度摘要(如 "168,6")` / `保存时间` |
| `saveN.png` | 存档截图（约 100 KB） |

N = 0..3，共 4 个存档槽。

## 7.2 顶层字段表

| 字段 | 类型 | 含义 / 备注 |
|---|---|---|
| `PlayerName` | str | 玩家名（同步写入 `saveN.txt` 第 1 行） |
| `Sleep` | bool | 是否在睡觉 |
| `Money` | int | 金钱 |
| `Experience` | int | 经验 |
| `Proficiency` | int | 熟练度 |
| `level` | int | 等级 |
| `farmLevel` | int | 农场等级 |
| `currentHP` / `currentMP` | int | 当前 HP / MP |
| `Marker` | list | 地图标记（本档为空） |
| `GameTime` | list[3] | 游戏时间 `[0,0,0]` |
| `activeTime` | int | 游戏活跃计时（秒级计数器，用于作物/事件时间比较） |
| `sleepTime` | int | 睡觉计时 |
| `PlayerScene` | str | 当前场景标识（如 `FengMinYuan2`） |
| `PlayerLocation` | dict | `{x, y, z}` **float（注意浮点保真）** |
| `isRun` | bool | 是否奔跑 |
| `bagitems` | list | **背包**，见 7.3 |
| `toolitems` | list | **工具栏**（游戏固定 10 格），结构同 bagitems |
| `handerItemuuid` | str | 手持物品的 uuid（引用 bagitems 里的 uuid），无则空串 |
| `handerType` | str | 手持类型（如 `Seed`） |
| `scenesDestroyID` | list[str] | 已破坏/已采集物件，格式 `"<x><y><类型><场景名>"` |
| `list_clickedObj` | list[str] | 已点击对象，格式同上 |
| `farmitems` | list | **农田**，见 7.4 |
| `list_buildinfos` | list | 建筑 `[{uuid, name(物品ID字符串), pos{x,y,z}}]` |
| `fishItemuuid` | str | 鱼竿上挂的物品 uuid |
| `makeCraftInfos` | list | 制作队列 |
| `activeDialogues` | list | 已触发对话 `[{dialogueID, overTime}]` |
| `taskinfos` | list | 任务 `[{taskID, state, startTime, overTime}]`，state 0/1/2 |
| `clickEvents` | list | 点击事件 `[{type, clickCount}]` |
| `activeScene` | list[str] | 已激活（可去）的场景标识 |
| `list_npcFavorItem` | list | NPC 好感 |
| `list_giftSend` | list | 送礼记录 `[{x: NPC ID, y: 值}]` |
| `list_talk` | list | 交谈记录 `[{x: NPC ID, y: 值}]` |
| `list_relation` | list | 关系（本档为空） |
| `list_destroyNPC` | list | 已消灭 NPC（本档为空） |
| `list_recipe` | list[int] | **已学配方**（物品 ID 列表） |
| `list_skill` | list | **已学武学** `[{x: 功法物品ID, y: 等级}]` |
| `list_skillRun` | list[int] | **出招栏** 6 格（功法物品 ID，`0` = 空） |
| `list_equipment` | list[str] | 已装备饰品的 uuid（引用 bagitems） |
| `list_destroyMonstor` | list | 已消灭怪物（空） |
| `list_plant` / `list_buff` | list | 种植 / 状态（空） |
| `Equipment` | list[int] | 4 项装备相关数值 |
| `BaltSlot` | int | 快捷槽位（0） |
| `Tired` | int | 疲劳度（0） |
| `ListMemory` | list | 记忆（空） |
| `ListScene` | list[str] | 类别场景（3 项） |
| `Perk` | list[int] | 天赋栏 6 项 |
| `Bounty` | list | 悬赏（空） |

## 7.3 物品条目结构

```json
{
  "uuid": "<uuid4 字符串>",
  "count": 100000000,
  "item": {
    "id": 1207,
    "name": "木剑",
    "nameKey": "mujian",
    "MakeTime": 0,
    "spriteName": "mujian",
    "descriptionID": "Local206",
    "type": "Equipment",
    "itemTypeShow": "Weapon",
    "itemType": "Weapon",
    "level": 0,
    "giftValue": 0,
    "sellValue": 5,
    "buyValue": 10
  },
  "entered": true,
  "property": {
    "id": 1207,
    "name": "木剑",
    "keyName": "mujian",
    "minAttack": 0,
    "maxAttack": 0,
    "attack": 2,
    "minArmor": 0,
    "maxArmor": 0,
    "armor": 0,
    "crit": 0,
    "critHit": 0,
    "moveSpeed": 0,
    "dodge": 0,
    "maxHP": 0
  }
}
```

- `item` 与 `data\物品库.json` 里的条目**字段完全一致**。
- `property` 是**该实例已随机出的**数值。
- ★ **`property` 共 14 个键，里面只有 `maxHP`、没有 `maxMP`**。
- `uuid` 必须唯一；`handerItemuuid` / `fishItemuuid` / `list_equipment` 通过它引用。

## 7.4 农田条目

```json
{
  "uuid": "...",
  "pos": {"x": -8.0, "y": 1.0, "z": 0.0},
  "seedTime": 47728,
  "waterTime": 121012,
  "freeTime": 0,
  "farm": {
    "id": 1036,
    "name": "甘蔗",
    "nameKey": "GanZhe",
    "animName": "ganzhe",
    "Level": 1,
    "experience": 4,
    "growTime": 18,
    "dropID": 1035,
    "dropCount": 4
  }
}
```

## 7.5 序列化规则（最容易踩的坑）

1. 分隔符：`,` 与 `:` **前后都没有空格**。
2. 键顺序 = 文件顺序，**不要 `sort_keys`**。
3. 中文**不转义**（`ensure_ascii=False`）。
4. **浮点必须保留原文**（`RawFloat`）。
5. 文件末尾**没有换行符**。
6. 写盘编码 UTF-8 **无 BOM**，且用 `newline=""` 避免 Windows 自动加 `\r\n`。

## 7.6 两套 ID 体系（极易混淆）

| 体系 | 取值范围 | 来源 | 用于 |
|---|---|---|---|
| **物品 ID** | 1000~1228 | `data\物品库.json`（176 条） | `bagitems.item.id`、`list_recipe`、`list_skill.x`、`list_skillRun`、`farmitems.farm.dropID`、`list_buildinfos.name` |
| **NPC ID** | 1~1085 | `data\NPC库.json`（85 条） | `list_npcFavorItem.npcID`、`list_giftSend.x`、`list_talk.x` |

两套 ID **数值区间重叠**——**不要互相套用**。

## 7.7 HP / MP 上限的逆向结论（勿重复查）

| 问题 | 结论 |
|---|---|
| 存档里有「最大 HP / MP」字段吗？ | **没有**。只有当前值 `currentHP` / `currentMP` |
| 那上限从哪来？ | 游戏运行时算：**基础值（在代码里） + 身上装备的 `property.maxHP` 之和** |
| 存档里跟上限有关的只有一处 | `bagitems[*].property.maxHP`；**没有 maxMP** |
| 游戏数据表里的 maxHP/maxMP 在哪？ | 只在**装备属性表**；605~625 系列**只有 maxHP**；没有任何「人物基础生命表」 |
| 能改什么 | **生命上限**：改装备的 `maxHP`；**内力上限**：没有可写字段，**改不了** |

## 7.8 游戏如何读写存档（重要）

- Unity 游戏只在**启动/载入存档时读一次盘**，此后一直用内存里的数据。
- 在游戏里点「读档」**不会重新读文件**。
- 游戏一存档就把内存里的旧数据写回文件，**直接覆盖**我们的修改。
- 所以：**改了存档后，要在游戏里重新读档（必要时重启游戏）才能看到变化。**

# 第八部分：安全、法律与伦理

## 8.1 安全须知

### 8.1.1 对游戏的安全

- 本工具**不注入游戏进程**，不修改游戏内存，不联网。
- 本工具只修改**存档文件**，游戏读取后才会生效。
- 修改存档**不会导致游戏崩溃**（除非你写入了非法数据）。
- 建议**不要写极端值**（如 `Money = 2147483647`），可能引起游戏异常。

### 8.1.2 对存档的安全

- 每次保存前**自动备份**到 `backups\`。
- 写盘用**原子替换**（tmp + os.replace），不会写一半坏掉。
- 写盘后**回读校验**，确认真的写进去了。
- 浮点**逐字节保真**，不会因为序列化差异导致游戏读不了。

### 8.1.3 对电脑的安全

- 本工具**不联网**，不上传任何数据。
- 本工具**不修改注册表**，不写系统目录。
- 本工具**不包含病毒**，源码全公开，可自行审计。

## 8.2 法律须知

- 单机游戏修改存档，**通常不违法**。
- 但**可能违反游戏 EULA**，具体看游戏条款。
- **不要分发修改后的游戏本体**。
- **不要用本工具从事任何违法活动**。
- 本工具采用 **AGPL-3.0 许可证**，允许自由使用、修改、分发。

## 8.3 伦理须知

- **单机游戏修改不影响他人**，但**联机游戏修改可能影响他人**，请勿在联机游戏中使用。
- **不要用修改后的存档冒充正常存档**（比如速通排行榜）。
- **尊重游戏开发者的劳动成果**，修改存档可以，但不要传播盗版。
- **分享修改心得时，注明使用了本工具**。

# 第九部分：常见问题（FAQ）——从入门到疑难杂症

## 9.1 入门级问题

**Q1：这个工具收费吗？**

A：免费，开源，AGPL-3.0 许可证。

**Q2：这个工具会盗号吗？**

A：不会。它不联网，不读你的账号密码，只读写游戏存档文件。

**Q3：这个工具会封号吗？**

A：单机游戏不会封号。联机游戏请勿使用。

**Q4：我该下载哪个版本？**

A：如果你不懂编程，下载打包好的 exe 版本。如果你懂 Python，可以下载源代码版本。

**Q5：存档在哪？**

A：`<游戏安装目录>\大侠狂想曲_Data\Data\Save\saveNplayer.json`。

**Q6：为什么程序找不到存档？**

A：点「设置…」→「浏览…」手动指定 `Save` 目录。

**Q7：改完保存了，游戏里没看到变化？**

A：①确认点了「保存」（标题栏的 `*` 消失）；②确认改的是当前在玩的那个槽；③回游戏里重新读一次档（必要时重启游戏再读档）。

**Q8：程序右下角显示「游戏运行中」，需要关掉游戏吗？**

A：不需要，那只是一行提示。改完保存，回游戏里读档就行。

## 9.2 进阶级问题

**Q9：为什么加了道具游戏里看不到？**

A：先确认保存成功（回读校验显示 ✔）；再确认改的是当前在玩的槽；最后重启游戏再读档。

**Q10：为什么删了道具又回来了？**

A：因为游戏在内存里持有旧数据，存档时把旧数据写回，覆盖了你的修改。**重启游戏再读档**。

**Q11：浮点保真是什么？**

A：Unity 写 double 用 17 位有效数字（如 `222.22796630859376`），Python 的 `repr` 只给最短可还原文本（`222.22796630859375`）。二进制值相同，但字节不同。本工具用 `RawFloat` 记住原文本，保证逐字节一致。

**Q12：为什么不能改内力上限？**

A：存档里没有 `maxMP` 字段，游戏自己的 `property` 结构里也没有这个键。硬塞一个会被游戏忽略。

**Q13：为什么改装备 maxHP 能提高最大生命？**

A：因为游戏的最大生命 = 基础值 + 身上装备的 `property.maxHP` 之和。改装备的 maxHP，穿上就生效。

**Q14：怎么一次改多个物品？**

A：在物品选择对话框里按住 Ctrl 或 Shift 多选。

**Q15：怎么把存档还原到之前的状态？**

A：高级 → 备份管理 → 选中一个备份 → 还原到存档槽。

## 9.3 疑难杂症

**Q16：程序启动报错「数据表缺失」？**

A：确认 `data\` 目录与程序在同一目录下。编译后需要一起分发。

**Q17：程序启动后物品列表是空的？**

A：同上，`data\` 目录缺失或损坏。

**Q18：保存后游戏读档报错？**

A：用「高级 → 备份管理」还原一份备份。然后检查你改了什么非法数据。

**Q19：存档文件变得很大？**

A：正常。JSON 是明文，物品多了文件就大。

**Q20：能改存档槽数量吗？**

A：不能。游戏固定 4 个槽。

**Q21：能改游戏本体吗？**

A：不能。本工具只改存档。

**Q22：能联机用吗？**

A：不能。请勿在联机游戏中使用。

**Q23：能改手机版吗？**

A：如果手机版存档格式相同，理论上可以，但本工具目前只支持 Windows。

**Q24：游戏更新后工具还能用吗？**

A：可能能用，但数据表可能失效。需要重新跑 `extract_assets_json.py` + `build_libs.py`。

**Q25：怎么报 bug？**

A：通过 GitHub Issues 提交：https://github.com/duma520/DaxiaSaveEditor/issues

# 第十部分：版本更新简史——每个版本一句话

| 版本 | 日期 | 一句话简介 |
|---|---|---|
| **v1.0.0** | 2026-09-20 | 首个版本：逆向存档格式、提取数据表、8 页签界面、安全机制 |
| **v1.1.0** | 2026-09-20 | 界面改为「外层页签 + 内嵌分页」，解决内容拥挤问题 |
| **v1.2.0** | 2026-09-20 | 修复「加的道具游戏里看不到」——防游戏覆盖，加进程检测 |
| **v1.3.0** | 2026-09-20 | 定位「改了没变化」根因：游戏没退出；加运行时禁止保存 |
| **v1.4.0** | 2026-09-20 | 去掉「关游戏」式提示与保存拦截，回归简单流程 |
| **v1.5.0** | 2026-09-20 | HP/MP 最大值逆向清楚 + 装备 maxHP 一键设置 |
| **v1.5.1** | 2026-09-20 | 接入程序图标 icon.ico（exe 图标 + 窗口/任务栏图标） |

**当前版本：v1.5.1**

# 第十一部分：开发者文档——代码地图与维护约定

## 11.1 代码地图（v1.5.1 实测行号，共 3939 行）

| 行号 | 内容 |
|---|---|
| L2 | `__version__`（**改版本号只需改这里**） |
| L13 | `from datetime import datetime, timedelta` |
| L20~L93 | 常量：`MAX_INT` / `MAX_COUNT` / `SLOT_COUNT` / `DEFAULT_SAVE_DIR` / `GAME_EXE_NAMES` / `SAVE_WATCH_MS` / `ZERO_PROPERTY` / `EQUIP_KINDS` / `ITEM_TYPE_ORDER` / `TASK_STATE_LABELS` |
| L96~L149 | 路径与图标：`app_dir` / `_app_icon_cache` / `app_icon` / `data_dir` / `settings_path` / `backup_dir` / `history_path` |
| L152~L195 | 设置持久化：`DEFAULT_SETTINGS` / `load_settings` / `save_settings` |
| L198~L367 | 进程检测：`_enum_processes` / `list_process_names` / `_is_game_name` / `_process_start_time` / `_find_game_process` / `game_process_running` / `human_duration` / `game_process_info` / `file_signature` |
| L370~L422 | `detect_save_dir` / `load_history` / `push_history` |
| L430~L534 | 数据表库：`_load_lib` / `item_lib` / `item_map` / `prop_lib_map` / `npc_lib` / `npc_map` / `npc_display_name` / `chapter_lib` / `crop_lib` / `scene_lib` / `buff_lib` / `item_name` / `is_gongfa` / `gongfa_items` / `recipe_items` / `weapon_items` |
| L543~L625 | 存档读写：`RawFloat` / `_enc_json` / `dumps_save` / `read_save` / `write_save` |
| L638~L728 | 存档槽与备份：`slot_*_path` / `read_slot_txt` / `write_slot_txt` / `scan_slots` / `backup_save` |
| L731~L951 | 纯数据操作层：`make_property_for` / `make_bag_entry` / `bag_add` / `bag_delete` / `field_fix_after_delete` / `list_add_ids` / `list_remove_ids` / `list_add_pairs` / `list_remove_pairs` / `list_add_dicts` / `list_remove_dicts` / `bag_summary` / `iter_equip_entries` / `maxhp_list` / `set_maxhp_all` |
| L954~L1005 | 小组件与工具：`NumEdit` / `make_table` / `set_row` / `info` / `warn` / `ask` |
| L1013~L1184 | `ItemPickDialog` |
| L1188~L1269 | `SettingsDialog` |
| L1272~L1352 | `HELP_TEXT` / `HelpDialog` |
| L1356~L1457 | `MainWindow.__init__` / `_check_game_process` / `_ack_save_warn` / `_start_save_watch` / `_on_watch_tick` |
| L1461~L1572 | `_act` / `_build_toolbar` / `_build_central` / `_set_dot` / `_restore_geometry` / `_show_slot_info` |
| L1576~L1681 | 存档槽：`refresh_slots` / `_sync_slot_selection` / `_select_start_slot` / `on_slot_changed` / `open_slot` |
| L1685~L1782 | 打开/保存：`load_file` / `_update_title` / `mark_dirty` / `_txt_path_for` / `on_save` / `on_save_as` / `on_reload` / `on_backup_now` |
| L1869~L1877 | `closeEvent` |
| L1887~L1974 | 通用工具：`_doc_get` / `_doc_set` / `_guard` / `_bind_int` / `_bind_float` / `_bind_bool` / `_bind_text` / `_scroll_page` |
| L1977~L2137 | 页签 1 基础属性：`_basic_role_page` / `_basic_time_page` / `_basic_quick_page` / `create_basic_tab` / `refresh_basic` |
| L2225~L2441 | 页签 2 背包/工具栏：`_make_item_section` / `create_bag_tab` / `refresh_bag` / `on_bag_*` / `open_maxhp_batch` |
| L2446~L2653 | 页签 3 武学/配方：`_skill_page` / `_skillrun_page` / `_recipe_page` / `create_skill_tab` |
| L2658~L2939 | 页签 4 NPC/剧情：`_favor_page` / `_dialogue_page` / `_gifttalk_page` / `_click_page` / `create_npc_tab` |
| L2944~L3053 | 页签 5 任务：`create_task_tab` |
| L3059~L3238 | 页签 6 农场/建造：`_farm_page` / `_build_page` / `create_farm_tab` |
| L3243~L3440 | 页签 7 世界/杂项：`create_world_tab` |
| L3445~L3643 | 页签 8 高级：`_json_page` / `_backup_page` / `create_adv_tab` / `on_validate` |
| L3648 | `refresh_all()` |
| L3668~L3910 | `ItemEditDialog` / `EquipMaxHpDialog` / `SimplePickDialog` / `NpcPickDialog` / `TaskPickDialog` |
| L3916~L3938 | `main()` + `__main__` |

## 11.2 维护约定（必须遵守）

1. **文档 + 版本号同步**：每次改主程序后，必须更新 `软件升级迭代记录.md` 和 `__version__`。
2. **版本号更新必须备份**：把主程序复制到 `version\` 子目录。
3. **唯一编译源**：`DaxiaSaveEditor.py` 是最终版本。
4. **新增设置项必须三处成对**：`DEFAULT_SETTINGS` + `SettingsDialog` + `_on_setting_changed`。
5. **新增数据表**：放到 `data\`，用 `_load_lib` 读取，同时加进 Nuitka bat。
6. **脚手架入子目录**：所有探查/生成/测试脚本必须放 `_scaffold\`。
7. **GUI 层与数据层分离**：所有数据操作写成模块级纯函数。
8. **改完必须跑冒烟测试**：当前基线 187 项全部通过。
9. **不要在 GUI 方法里直接 `json.dumps/loads` 存档**，必须走 `dumps_save` / `read_save`。
10. **任何写盘动作都要先 `backup_save()`**。
11. **界面布局：内容多的页签要拆内嵌分页**。
12. **不要把一堆控件塞在一行**。
13. **新增/调整界面后必须跑 `_scaffold\shot_ui.py` 截图人工看一眼**。
14. **任何“刷新/重画”类方法都不得隐式重读存档**。
15. **检测外部进程 → 用 Win32 API，不要用 `tasklist`**。
16. **游戏没退出＝白改，但不要再拿这件事烦用户**。
17. **`except Exception: return None` 会吞掉真 Bug**。
18. **要做「最大值 / 上限」类功能，先扫存档 + 扫数据表，别猜**。

# 第十二部分：编译、打包与分发

## 12.1 编译命令

```bat
0_nuitka_pyside6_clang_auto.bat
```

## 12.2 编译脚本说明

```bat
@echo off
REM  ... ASCII-only comments (see the real file) ...
chcp 65001 >nul

nuitka --standalone ^
    --enable-plugin=pyside6 ^
    --windows-console-mode=disable ^
    --follow-imports ^    --jobs=4 ^
    --clang ^
    --remove-output ^
    --output-dir=build_output ^
    --windows-icon-from-ico=icon.ico ^
    --include-data-files=icon.ico=icon.ico ^
    --include-data-files=data/物品库.json=data/物品库.json ^
    --include-data-files=data/装备属性库.json=data/装备属性库.json ^
    --include-data-files=data/配方库.json=data/配方库.json ^
    --include-data-files=data/农作库.json=data/农作库.json ^
    --include-data-files=data/NPC库.json=data/NPC库.json ^
    --include-data-files=data/章节任务库.json=data/章节任务库.json ^
    --include-data-files=data/状态库.json=data/状态库.json ^
    --include-data-files=data/场景库.json=data/场景库.json ^
    DaxiaSaveEditor.py
```

## 12.3 编译产物

`build_output\DaxiaSaveEditor.dist\` 目录，包含：

- `DaxiaSaveEditor.exe` — 主程序
- `icon.ico` — 程序图标
- `data\` — 数据表
- 依赖 DLL

**整个 `DaxiaSaveEditor.dist\` 目录一起拷给用户。**

## 12.4 什么情况下必须同步改 bat

| 触发条件 | 要改什么 |
|---|---|
| 新增/改名/删除 `data\*.json` | 同步加/改/删对应的 `--include-data-files` |
| 新增第三方库 | 一般 `--follow-imports` 会自动跟；带数据文件的库要加 `--include-package-data` |
| 换入口文件名 | 末尾的 `DaxiaSaveEditor.py` |
| 换图标/新增图标 | 两行都要：`--windows-icon-from-ico` + `--include-data-files` |
| 改产物目录/控制台行为 | `--output-dir` / `--windows-console-mode` |

## 12.5 bat 格式铁律

- UTF-8 **无 BOM**
- 全 **CRLF**
- 首行 `@echo off`、第二行 `chcp 65001 >nul`

# 第十三部分：故障排查手册

## 13.1 启动问题

| 现象 | 原因 | 解决 |
|---|---|---|
| 双击 exe 没反应 | 杀毒软件拦截 | 加白名单 |
| 报错「缺少 DLL」 | 没有整个 dist 目录一起拷 | 整个目录一起拷 |
| 报错「数据表缺失」 | `data\` 目录缺失 | 把 `data\` 放到 exe 旁 |
| 启动后界面空白 | 显卡驱动问题 | 更新显卡驱动 |
| 启动后中文乱码 | 系统区域设置问题 | 控制面板 → 区域 → 非 Unicode 程序语言 → 中文 |

## 13.2 存档问题

| 现象 | 原因 | 解决 |
|---|---|---|
| 找不到存档 | 存档目录不对 | 设置 → 浏览 → 手动指定 |
| 读存档失败 | 存档损坏 | 用备份还原 |
| 保存失败 | 文件被占用 | 关掉游戏再保存 |
| 保存后游戏读不了 | 写入了非法数据 | 用备份还原 |

## 13.3 修改问题

| 现象 | 原因 | 解决 |
|---|---|---|
| 改了没变化 | 游戏没重新读盘 | 重启游戏再读档 |
| 加了道具看不到 | 同上 | 同上 |
| 删了道具又回来 | 同上 | 同上 |
| 改错了想撤销 | — | 重新载入 / 备份还原 |

## 13.4 性能问题

| 现象 | 原因 | 解决 |
|---|---|---|
| 启动慢 | 数据表加载 | 正常，几秒 |
| 切换页签卡 | 表格数据多 | 正常，等一下 |
| 保存慢 | 文件大 | 正常，几秒 |

# 第十四部分：术语表

| 术语 | 含义 |
|---|---|
| **存档** | 游戏保存进度的文件，`saveNplayer.json` |
| **槽** | 游戏的存档位，共 4 个 |
| **JSON** | 一种数据格式，用键值对表示 |
| **字段** | JSON 里的一个键值对 |
| **顶层字段** | JSON 根对象下的字段 |
| **嵌套字段** | 字段里的字段 |
| **UUID** | 唯一标识符，用于引用物品 |
| **引用** | 一个字段的值是另一个对象的标识符 |
| **浮点保真** | 保证浮点数序列化后字节不变 |
| **原子写盘** | 写临时文件再替换，避免写一半坏掉 |
| **回读校验** | 写完后重新读一遍，确认写对了 |
| **备份** | 保存前复制一份原文件 |
| **冒烟测试** | 快速验证核心功能的测试 |
| **纯函数** | 不依赖外部状态、不修改外部状态的函数 |
| **GUI** | 图形用户界面 |
| **数据层** | 与界面无关的数据操作代码 |
| **逆向** | 分析游戏文件，理解其结构 |
| **数据表** | 从游戏里提取的物品/NPC/场景等数据 |
| **进程** | 正在运行的程序 |
| **Win32 API** | Windows 系统接口 |
| **ctypes** | Python 调用 C 函数的库 |
| **Nuitka** | 把 Python 编译成 exe 的工具 |
| **PySide6** | Qt6 的 Python 绑定 |
| **Qt6** | 一个跨平台 GUI 框架 |
| **AGPL-3.0 许可证** | GNU Affero 通用公共许可证第 3 版，允许自由使用/修改/分发，以网络服务形式提供时亦须开源 |

# 第十五部分：附录——文件清单与快速索引

## 15.1 项目目录结构

```
你的项目目录\DaxiaSaveEditor\
├─ DaxiaSaveEditor.py                     主程序（唯一编译源）
├─ icon.ico                               程序图标
├─ 软件升级迭代记录.md                     项目说明书 + 迭代日志
├─ 使用说明.txt                            给玩家的快速上手说明
├─ 0_nuitka_pyside6_clang_auto.bat        编译脚本
├─ 1.bat                                  开发运行
├─ data\                                  数据表（随程序分发）
│   ├─ 物品库.json / 装备属性库.json / 配方库.json / 农作库.json
│   ├─ NPC库.json / 章节任务库.json / 状态库.json / 场景库.json
│   └─ 数据来源.json
├─ _scaffold\                             开发脚本与测试（不分发）
│   ├─ README.md
│   ├─ smoke_test.py / launch_check.py / shot_ui.py
│   ├─ probe_structure.py / probe_assets.py / peek_assets.py
│   ├─ extract_assets_json.py / build_libs.py
│   ├─ assets_json\                       从 resources.assets 抠出的原始 JSON
│   └─ shots\                             界面截图
├─ version\                               版本备份
│   ├─ DaxiaSaveEditor - 1.0.0 首个版本.py
│   ├─ DaxiaSaveEditor - 1.1.0 界面改为内嵌分页.py
│   ├─ DaxiaSaveEditor - 1.2.0 防游戏覆盖存档.py
│   ├─ DaxiaSaveEditor - 1.3.0 游戏运行时禁止保存.py
│   ├─ DaxiaSaveEditor - 1.4.0 去掉关游戏提示.py
│   ├─ DaxiaSaveEditor - 1.5.0 装备生命上限maxHP.py
│   └─ DaxiaSaveEditor - 1.5.1 接入图标icon.py
├─ backups\                               存档备份（运行时自建）
├─ 设置.json                              程序设置（运行时自建）
└─ 历史记录.json                          最近打开的存档目录（运行时自建）
```

## 15.2 快速索引

| 我想…… | 去看…… |
|---|---|
| 快速上手 | 第二部分 |
| 了解每个按钮 | 第三部分 |
| 按人群找方案 | 第四部分 |
| 按职业找方案 | 第五部分 |
| 二次开发 | 第六部分 |
| 理解存档格式 | 第七部分 |
| 了解法律问题 | 第八部分 |
| 解决常见问题 | 第九部分 |
| 看版本历史 | 第十部分 |
| 读代码 | 第十一部分 |
| 编译打包 | 第十二部分 |
| 排查故障 | 第十三部分 |
| 查术语 | 第十四部分 |

## 15.3 外部链接

- **GitHub**：https://github.com/duma520
- **项目地址**：https://github.com/duma520/DaxiaSaveEditor
- **问题报告**：https://github.com/duma520/DaxiaSaveEditor/issues

**版权声明 © 永久 杜玛 保留所有权利**  
本文档内容随本仓库以 AGPL-3.0 发布，可自由转载与商用。  
注意：我们不提供私人邮箱支持，所有技术支持都通过公开渠道进行，以便其他用户也能受益。

**开源许可证：AGPL-3.0**  
**开发时间：2026-09-18**  
**当前版本：v1.5.1**

## 许可

本项目采用 **GNU Affero General Public License v3.0（AGPL-3.0）** 发布。

- 完整许可证条文见仓库根目录 [LICENSE](LICENSE)。
- 你可以自由使用、修改、分发，包括用于商业用途，无需另行获得授权。
- 若你修改后分发，或以网络服务方式提供本软件，必须按 AGPL-3.0 公开相应源代码。
- 本仓库自 2026-11-23 起改用 AGPL-3.0；此前已按 MIT / BSD-3-Clause 发布的版本，其接收者依原许可证获得的授权继续有效。
