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
  primary: "#2563EB"
  secondary: "#F97316"
  accent: "#10B981"
  background: "#FFFFFF"
  surface: "#F8FAFC"
  text:
    primary: "#0F172A"
    secondary: "#475569"
    disabled: "#94A3B8"
  border: "#E2E8F0"
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
  professional:
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

  tech:
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

  minimalist:
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

  academic:
    colors:
      primary: "#1A365D"
      accent: "#C53030"
      background: "#FFFFFF"
    typography:
      display_family: "'Georgia', 'Noto Serif SC', serif"
      body_family: "'Source Sans 3', 'Noto Sans SC', sans-serif"
    spacing:
      density: "comfortable"

  creative:
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

### 规则2：风格切换影响范围
切换 L1 风格时：自动更新所有 color/typography/spacing.density token，不改变内容结构和 layout 模板。

### 规则3：内容→视觉表达映射
Strategist 对每个内容块推荐视觉表达形式：
- 数据趋势 → 折线图/面积图，使用 typography.data + colors.semantic
- 对比数据 → 柱状图/表格，使用 spacing.card_gap + colors.border
- 关键指标 → 大数字高亮，使用 typography.data + colors.accent
- 引用 → 引用卡片，使用 border_radius.lg + colors.surface

### 规则4：多风格预览
用户不确定风格时，出 2-3 个封面 SVG 预览，用户选完再完整输出。
