# Visual Archetypes

用于把高完成度模板的视觉能力抽象为可复用方向。只吸收公开设计模式，不复制第三方代码、素材、文案、prompt 或模板结构。

## 使用规则

- 有参考先做 Reference Decomposition：信息架构、布局节奏、字体气质、色彩系统、组件语法、动效模型、资产策略和验收证据。
- 先判定交付形态：产品界面、营销页、个人主页、作品集、仪表盘、移动端、单文件 HTML 或 HTML 演示稿。
- 原型只定义视觉方向，不替代需求、内容、品牌资产、接口契约或实现架构。
- 每个原型输出：适用场景、layout grammar、typography、palette、hero、motion、assets、risk。
- 方向明确时选择一个主原型；方向不清时最多给三个真实可实现的关键视图方向。

## 原型库

### Cinematic Signal

- 适用：高端个人品牌、AI 工程师、创始人、顾问、发布型首页。
- Layout grammar：暗场大留白、强首屏锚点、少量高权重入口、连续滚动叙事。
- Typography：几何无衬线大标题，mono 用于导航、编号和元信息。
- Palette：近黑底、白色主文字、低透明辅助文字，单一克制强调色。
- Hero：固定媒体或抽象背景，身份信息与主 CTA 分区明确。
- Motion：滚动揭示、轻量视频/背景漂移、少量玻璃态交互。
- Assets：优先真实视频、项目截图或人物影像；缺失时用高质量 CSS 背景。
- Risk：内容弱时容易空；必须用清晰定位、证据入口和行动路径补足。

### Neural Media Hero

- 适用：AI 研究者、Agent 项目、前沿技术个人页。
- Layout grammar：全屏媒体主导，身份、指标、技术栈、架构、联系按连续章节推进。
- Typography：冷静技术字体，中文正文保持可读字号和 CJK 字体栈。
- Palette：黑底、白字、青色信号色，少量紫色辅助。
- Hero：人物、网络、数据流或产品循环成为首屏视觉核心。
- Motion：鼠标或滚动驱动的媒体反馈、文本解码、视口播放。
- Assets：视频和头像必须存在或可授权；不能编造远程媒体地址。
- Risk：媒体包和动效成本高；移动端必须降级。

### Soft Product Video

- 适用：个人工具、轻产品入口、创作者产品化首页。
- Layout grammar：居中首屏、柔和背景媒体、短导航、强 CTA、少量下探内容。
- Typography：有性格的 display 字体配合高可读正文。
- Palette：暖中性色或浅色背景，深灰蓝文本，一个明确 CTA 色。
- Hero：一句产品化定位、一句解释、一个媒体或设备框。
- Motion：轻淡 fade、pill 状态、媒体遮罩揭示。
- Assets：需要产品截图或录屏；缺失时用设备框或刻意 placeholder。
- Risk：容易滑向通用 SaaS；必须保持 person-led 与真实产品证据。

### Clean Developer

- 适用：前端开发者、开源作者、技术博客、真实个人网站。
- Layout grammar：浅色连续页面、紧凑导航、身份介绍、头像/符号、项目网格自然衔接。
- Typography：清晰 sans，层级依靠字号、字重和留白，不靠过度装饰。
- Palette：浅蓝白或柔和中性色，炭黑文本，一个蓝/青 CTA 色。
- Hero：问候语、职业关键词、位置/状态、头像或身份符号、两个 CTA。
- Motion：轻量 fade-up、波浪或柔和区段过渡、项目 hover overlay。
- Assets：使用用户头像、授权插画或抽象身份符号。
- Risk：排版弱会显得普通；必须有项目证据和一个视觉记忆点。

### Spatial Tech

- 适用：AI、前端、Coding Agent、系统型项目作品集。
- Layout grammar：代码面板、节点图、3D 项目墙或空间卡片与证据区组合。
- Typography：技术 sans 加 mono 指标。
- Palette：深色中性底，青绿、橙或蓝作为信号色。
- Hero：身份与系统图、项目对象或数据流并置。
- Motion：低速网格、卡片 tilt、节点脉冲。
- Assets：项目截图、架构图、日志、benchmark 优先。
- Risk：不能牺牲可读性；3D 只做空间层次，不承载唯一信息。

### Editorial Magazine

- 适用：设计师、艺术家、视觉创作者、内容型作品集。
- Layout grammar：封面式首屏、不对称排版、图片主导、项目以版面展开。
- Typography：serif display 或强个性标题配合克制正文。
- Palette：纸感底或暗色画廊底，低饱和主色，一个尖锐强调色。
- Hero：姓名、身份、主题标签、大图或海报式视觉。
- Motion：文字 stagger、图片 mask reveal、局部横向画廊。
- Assets：作品图必须清晰且授权。
- Risk：不能只做装饰；项目、角色、过程和结果必须可读。

### Terminal System

- 适用：程序员、安全研究、开源作者、基础设施产品作者。
- Layout grammar：终端身份区、状态卡、日志时间线、仓库式项目列表。
- Typography：mono 承担界面语气，正文可用 readable sans。
- Palette：近黑底、绿色/青色信号、灰边框、少量琥珀提示。
- Hero：`whoami`、当前项目、技术方向和主 CTA 可立即读到。
- Motion：短命令输入、光标、日志流。
- Assets：代码、README、issue、benchmark、CLI 输出可作为证据。
- Risk：不要让全站都变成终端；可读性优先于戏剧感。

### Premium Resume

- 适用：求职、学生、顾问、职业主页。
- Layout grammar：姓名、角色、价值主张、案例、经验和联系按证据链组织。
- Typography：专业 sans 或克制 serif，标题稳重，正文易扫读。
- Palette：白/象牙底、炭黑文本、细边框、一个可信强调色。
- Hero：角色、能力、简历/联系入口和核心证明。
- Motion：轻量 reveal，避免重 3D。
- Assets：简历、项目截图、论文、证书、作品链接。
- Risk：不能退化成简历表；需要一个精致但不喧宾夺主的视觉锚点。

### AI System Dashboard

- 适用：AI 工程师、LLM 研究、Agent 系统、模型工作流展示。
- Layout grammar：把人或项目放在控制平面中心，输入、工具、验证、输出形成系统图。
- Typography：技术 sans 加 mono 指标和节点标签。
- Palette：深蓝/黑底，青色、绿色信号，紫色只作少量辅助。
- Hero：系统流程、能力节点、项目输出和验证闭环。
- Motion：节点脉冲、边流、低密度网格。
- Assets：架构图、评测、日志、demo 链接。
- Risk：别做成普通 SaaS dashboard；中心必须是人的能力或项目系统。

### Creator Bento

- 适用：自媒体、作者、播客、视频创作者、社群入口。
- Layout grammar：身份首屏、平台入口、内容主题、精选内容和合作 CTA 组成可扫 bento。
- Typography：友好粗标题，正文简短有节奏。
- Palette：一个个人品牌主色加中性底。
- Hero：个人定位、内容主题和核心平台入口。
- Motion：卡片入场、hover 展开、精选内容轮播。
- Assets：封面、头像、平台图标、内容截图。
- Risk：bento 不等于同质卡片堆；每块必须承担不同信息。

### Dark Gallery

- 适用：高端作品集、创意技术、摄影、艺术申请。
- Layout grammar：暗色画廊、超大图片、项目展开、引文和少量导航。
- Typography：优雅 serif 标题、窄体 sans 标签。
- Palette：黑、暖灰、奶油或金色少量强调。
- Hero：全幅作品或人物视觉，姓名和身份低噪声出现。
- Motion：mask、慢 fade、局部 parallax。
- Assets：作品图质量决定上限。
- Risk：暗色会伤可读性；对比、间距和正文宽度必须检查。

### Business Proof

- 适用：创始人、顾问、自由职业、服务型个人品牌。
- Layout grammar：问题、方法、案例结果、服务入口和预约 CTA 构成转化链路。
- Typography：可信 executive sans 或精致 serif。
- Palette：象牙、黑、深蓝或石墨，强调色必须服务 CTA。
- Hero：解决什么问题、为什么可信、下一步行动。
- Motion：信任型微交互，不使用分散注意力的炫技效果。
- Assets：案例结果、客户标识、方法论图、真实评价。
- Risk：不能泛化成咨询公司模板；个人故事和证据必须突出。

### Case Study

- 适用：作品集求职、产品设计、工程案例、PM 项目。
- Layout grammar：角色、问题、约束、方案、结果和反思按案例链展示。
- Typography：高可扫读层级，数字和结果突出。
- Palette：中性底，角色或行业对应单一强调色。
- Hero：聚焦能力与证据，而不是空泛愿景。
- Motion：滚动 reveal、进度时间线、hover 细节。
- Assets：截图、流程图、指标、代码片段、before/after。
- Risk：不要写成流水账；每个案例必须说明职责和结果。

### Museum Curation

- 适用：艺术家、摄影师、策展型作品集、教育型创作网站。
- Layout grammar：搜索/发现入口、主题导航、作品墙、故事卡、展览时间线。
- Typography：展览标题用 refined serif，元信息用 precise sans 或 mono。
- Palette：美术馆纸白、墨黑、石灰、少量陶土或画廊红。
- Hero：精选作品、策展陈述、主题 chips。
- Motion：作品慢 reveal、画廊 parallax、细节展开。
- Assets：作品、系列、展览资料必须授权。
- Risk：只能吸收策展模式，不复制博物馆站点资产、文本、集合或结构。

## 渲染级 QA

- 桌面和移动视口必须检查布局、文字换行、横向溢出、资源加载和关键交互。
- 视觉重构必须检查 changed elements 的 computed style：颜色、字体、display、position、z-index、overflow、transform。
- 媒体元素必须有相对路径、alt 文本、稳定 aspect-ratio、合理 object-fit 和缺失资产 fallback。
- 动效必须支持 `prefers-reduced-motion`，移动端降低 3D、粒子、parallax 或视频负载。
- 页面只能有一个主动效系统；局部 hover/focus 只作反馈，不抢内容层级。
- 首屏必须体现真实身份、产品或作品证据；禁止通用居中区块、随机光效、无意义图标墙和同质卡片堆。

## 来源边界

- 高层模式参考 [Personal Homepage Skill](https://github.com/shengjidaguai-china/personal-homepage-skill) 的公开仓库。
- 该项目采用非商业许可；本文件只做抽象学习，不复制第三方代码、素材、文案、prompt 或模板结构。
- 若后续项目需要复用外部代码、素材、模板或 prompt，必须先检查 license、授权范围、署名要求和商业使用限制。
