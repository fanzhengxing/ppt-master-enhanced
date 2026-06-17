# ppt-master Speed Bottleneck Analysis

> 分析日期: 2026-06-17
> 触发: 用户报告生成太慢，要求分析优化空间

---

## 瓶颈分布

| 步骤 | 耗时占比 | 性质 |
|------|---------|------|
| Step 4 (Strategist) | ~10-15% | LLM思考 |
| Step 5 (Image Acquisition) | ~10-30% | 外部API（可选） |
| **Step 6 (Executor SVG)** | **~60-75%** | **LLM手写SVG（主瓶颈）** |
| Step 7 (Post-process) | ~5-10% | Python脚本 |

**核心瓶颈：Step 6 Executor 逐页手写 SVG，占总耗时 60-75%。**

---

## 竞品加速思路对比

| 竞品 | 方法 | 加速原理 | 劣势 |
|------|------|---------|------|
| **Gorden** (4-layer compose) | Image → GPT Vision → compose_pptx.py | 跳过SVG中间层，LLM只分析不负责绘制 | 输出是图片嵌入，非原生DrawingML |
| **PPTAgent** (DeepPresenter) | Fine-tuned 9B模型端到端生成 | 专用模型推理快5-10x，直接输出PPTX XML | 需Docker/GPU，不支持Windows |
| **html-ppt-skill** | HTML slides 浏览器渲染 | 毫秒级渲染，无需Python库 | 输出HTML非.pptx |
| **huashu-slides** | 模板→SVG→export，轻量 | 更少确认步骤，模板驱动减少LLM决策 | 不追求极致质量 |

---

## 推荐优化方案（按实施优先级）

### P0: spec_lock精简（预期 2-3x）
创建 `spec_lock_minimal.md`，每页只携带当前页需要的信息（颜色/字体/布局），去掉历史决策记录。

### P0: Mirror模式优先（预期 2-3x）
默认推荐mirror模式模板，LLM只做in-place text edit而非重新设计布局，每页SVG减少40-60%手写量。

### P1: 图片获取并行优化（预期 1.5-2x）
image_gen.py中混合调度ai+web请求，避免串行等待。

### P2: SVG骨架生成（预期 3-5x，风险高）
对重复布局（KPI卡片、4列布局、时间线）用脚本预生成SVG骨架，LLM只填充内容。

---

## 基准测试命令

```bash
# 创建测试项目
python scripts/project_manager.py init test_speed --format ppt169
python scripts/project_manager.py import-sources test_speed test_source.md

# 手动计时各步骤（Step 4/5/6/7分别记录时间）
```

## 关键发现

1. 每页SVG token消耗主要来自 spec_lock.md（~200-500行）+ 模板SVG重复读取
2. 管线的约束（逐页/主agent/hand-written）是质量保障，不能放弃
3. 最优解：不牺牲质量的前提下减少每页token消耗（方案A.1 + A.3）
