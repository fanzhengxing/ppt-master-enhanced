# Design Token System — 设计系统抽象层

> 在 brand/layout/deck 模板之上，提供一层 Design Token 抽象。
> 让 Strategist 做**约束求解**而非模板匹配——同一份内容，在不同 Token 约束下自动适配不同视觉风格。

来源：Open Design(设计系统引擎) + ppt-master原brand/layout/deck体系 + huashu-slides(多风格切换)

## Token 体系结构

```
Design Token 层（抽象约束）
    ↓ 实例化
Token Set（具体风格配置）
    ↓ 应用
模板层（brand / layout / deck）
    ↓ 执行
Executor（SVG → PPTX）
```

### Token 层级

| 层级 | 类型 | 说明 | 示例 |
|------|------|------|------|
| **L0** | 全局令牌 | 跨所有风格不变的基线 | 品牌色、文档字体 |
| **L1** | 风格令牌 | 同一品牌下不同风格变体 | 极简风/商务风/科技风各自的色板 |
| **L2** | 页面令牌 | 特定页面类型的局部覆盖 | 封面用大字重、数据页用等宽字体 |

---

## Token 定义规范

### 颜色令牌

```yaml
colors:
  primary: "#2563EB"        # 主色
  secondary: "#F97316"      # 辅助色
  accent: "#10B981"         # 强调色
  background: "#FFFFFF"     # 背景色
  surface: "#F8FAFC"        # 卡片/容器底色
  text:
    primary: "#0F172A"      # 正文色
    secondary: "#475569"    # 二级文本
    disabled: "#94A3B8"     # 禁用态
  border: "#E2E8F0"         # 边框色
  semantic:
    success: "#10B981"
    warning: "#F59E0B"
    error: "#EF4444"
    info: "#3B82F6"
```

### 字体令牌

```yaml
typography:
  display:
    family: "'Satoshi', 'Noto Sans SC', sans-serif"
    weight: 700
    size: "clamp(2rem, 4vw, 3.5rem)"
    line_height: 1.15
  heading:
    family: "'Satoshi', 'Noto Sans SC', sans-serif"
    weight: 600
    size: "clamp(1.25rem, 2.5vw, 2rem)"
    line_height: 1.3
  body:
    family: "'Inter', 'Noto Sans SC', sans-serif"
    weight: 400
    size: "clamp(0.875rem, 1.2vw, 1rem)"
    line_height: 1.6
  caption:
    family: "'Inter', 'Noto Sans SC', sans-serif"
    weight: 400
    size: "0.75rem"
    line_height: 1.4
  data:
    family: "'JetBrains Mono', 'Noto Sans SC', monospace"
    weight: 500
    size: "clamp(1rem, 2vw, 1.5rem)"
```

### 间距令牌

```yaml
spacing:
  xs: "0.25rem"
  sm: "0.5rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2rem"
  xxl: "4rem"
sizing:
  container_max: "1200px"
  card_min: "280px"
  card_gap: "1.5rem"
  border_radius:
    sm: "4px"
    md: "8px"
    lg: "16px"
    pill: "9999px"
```

### 风格定义（L1 风格令牌）

```yaml
styles:
  professional:          # 商务专业风
    colors:
      primary: "#1E3A5F"
      accent: "#D4A843"
      background: "#FFFFFF"
      surface: "#F5F7FA"
    typography:
      display_family: "'Times New Roman', 'Noto Serif SC', serif"
      body_family: "'Calibri', 'Noto Sans SC', sans-serif"
    spacing:
      density: "comfortable"

  tech:                  # 科技现代风
    colors:
      primary: "#2563EB"
      accent: "#06B6D4"
      background: "#0A0E17"
      surface: "rgba(255,255,255,0.04)"
    typography:
      display_family: "'Satoshi', 'Noto Sans SC', sans-serif"
      body_family: "'Inter', 'Noto Sans SC', sans-serif"
    spacing:
      density: "compact"

  minimalist:            # 极简风
    colors:
      primary: "#18181B"
      accent: "#18181B"
      background: "#FAFAFA"
      surface: "#FFFFFF"
    typography:
      display_family: "'Cabinet Grotesk', sans-serif"
      body_family: "'DM Sans', sans-serif"
    spacing:
      density: "spacious"

  academic:              # 学术风
    colors:
      primary: "#1A365D"
      accent: "#C53030"
      background: "#FFFFFF"
    typography:
      display_family: "'Georgia', 'Noto Serif SC', serif"
      body_family: "'Source Sans 3', 'Noto Sans SC', sans-serif"
    spacing:
      density: "comfortable"

  creative:              # 创意风
    colors:
      primary: "#7C3AED"
      accent: "#EC4899"
      background: "#0F0A1E"
    typography:
      display_family: "'Clash Display', sans-serif"
      body_family: "'Space Grotesk', sans-serif"
    spacing:
      density: "expressive"
```

---

## 约束求解规则

### 规则1：Token 覆盖优先级

```
L2（页面特定）> L1（风格变体）> L0（品牌基线）
```

如果某个Token在多个层级都有定义，取最高优先级的值。

### 规则2：风格切换影响范围

切换 L1 风格时：
- 自动更新所有 **color** token
- 自动更新所有 **typography** token
- 自动更新 **spacing.density**
- **不改变**内容结构和文本（只改样式）
- **不改变** layout 模板的 grid/column 结构

### 规则3：内容→视觉表达映射

Strategist 在写 `design_spec.md` 时，对每个内容块推荐视觉表达形式：

| 内容类型 | 推荐表达 | Token 影响 |
|---------|---------|-----------|
| 数据趋势 | 折线图/面积图 | 使用 `typography.data` + `colors.semantic` |
| 对比数据 | 柱状图/表格 | 使用 `spacing.card_gap` + `colors.border` |
| 关键指标 | 大数字高亮 | 使用 `typography.data` + `colors.accent` |
| 引用 | 引用卡片 | 使用 `spacing.border_radius.lg` + `colors.surface` |
| 列表 | 图标列表/数字列表 | 使用 `spacing.sm` + `colors.text.secondary` |
| 流程图 | 步骤卡片 | 使用 `spacing.card_min` + `sizing.container_max` |

### 规则4：多风格预览

在 Strategist 阶段，如果用户不确定风格，可以：
1. 给出 2-3 个风格选项（从 `styles` 中选）
2. 每个风格只生成 **封面页** 的 SVG 预览
3. 用户确认后，完整输出

---

## 与现有模板系统的关系

| 层 | 文件 | 来源 | 作用 |
|---|------|------|------|
| Token Set | `references/design-tokens.md` | 本文件 | 定义约束 |
| Brand | `templates/brands/<id>/design_spec.md` | 原系统 | 锁定 L0 token |
| Layout | `templates/layouts/<id>/design_spec.md` | 原系统 | 锁定结构/比例 |
| Deck | `templates/decks/<id>/` | 原系统 | Full replica |

**融合规则**：当用户指定 `brand` 模板时，策略从 `brand` 提取 L0 token，然后根据 `design_spec.md` 中声明的 `style: professional/tech/...` 自动应用对应的 L1 token。未指定的 token 用品牌模板默认值。

---

## 使用示例

### 给现有 brand 换风格

```
用户：之前用品牌A生成了PPT，想换成科技风
动作：保留 brand 的 L0 colors.primary，覆盖 L1 为 tech 风格
结果：色板主体不变，间距变紧凑，字体变Satoshi+Inter
```

### 多风格预览

```
用户：不确定用什么风格好
动作：生成3个封面SVG（professional, tech, minimalist）
用户选tech → 完整输出
```
