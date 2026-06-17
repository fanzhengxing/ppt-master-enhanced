# HTML Export 资源内联修复记录

> Date: 2026-06-16
> Status: VERIFIED & DEPLOYED

## Problem
`html_export.py` 生成的 `deck.html` 引用 `../assets/` 下的 CSS/JS 文件，但这些文件：
1. 位于 skill 安装目录 (`~/.hermes/skills/productivity/ppt-master/assets/`)
2. 不会被复制到输出目录 (`exports/`)
3. 用户双击 `deck.html` 时 CSS/JS 全部 404，页面空白

## Root Cause
- `html_export.py` 的 `build_full_html()` 使用 `<link href="../assets/...">` 和 `<script src="../assets/...">`
- `build_html_deck()` 虽然有 `include_assets` 参数会复制 assets，但：
  - 用户手动创建的示例 HTML（如 `html-ppt-deck.html`）没有走这个逻辑
  - 复制 assets 的逻辑在 `exports/` 目录下创建 `assets/` 子目录，但 HTML 引用的是 `../assets/`（相对路径错误）

## Solution: Resource Inlining

### Step 1: 修改 `html_export.py`
新增 `_read_asset()` 函数读取 CSS/JS 文件内容，`build_full_html()` 改为内联模式：

```python
def _read_asset(asset_path: Path) -> str:
    """Read an asset file, return empty string if missing."""
    try:
        return asset_path.read_text(encoding='utf-8')
    except Exception:
        return ''

def build_full_html(slides: list, theme: str, theme_css: str, total: int) -> str:
    """Build a self-contained HTML deck with ALL CSS/JS inlined."""
    
    skill_dir = Path(__file__).resolve().parent.parent
    assets = skill_dir / "assets"
    
    # Read all CSS sources
    fonts_css = _read_asset(assets / "fonts.css")
    base_css = _read_asset(assets / "base.css")
    animations_css = _read_asset(assets / "animations.css")
    runtime_js = _read_asset(assets / "runtime.js")
    
    # Build HTML with inline CSS/JS
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="{theme}" ...>
<head>
<meta charset="utf-8">
<style>
{fonts_css}
{base_css}
{animations_css}
.notes {{ display: none !important; }}
</style>
</head>
<body>
<!-- slides -->
</body>
<script>
{runtime_js}
</script>
</html>"""
```

### Step 2: 移除 assets 复制逻辑
`build_html_deck()` 中的 `shutil.copytree(src_assets, dst_assets)` 不再需要，改为注释说明。

### Step 3: 更新 SKILL.md
Step 7.4 描述更新为：
```bash
# Output: exports/deck.html (self-contained, all CSS/JS inlined)
#         No external assets directory needed
```

### Step 4: 修复手动示例
`html-ppt-deck.html` 手动示例同样改为内联模式——用 Python 脚本读取所有 CSS/JS 文件内容，替换 `<link>` 和 `<script src>` 为内联块。

## Verification
| Test | Result |
|------|--------|
| `html_export.py` 语法检查 | ✅ |
| 生成 deck.html 无 assets/ 目录 | ✅ |
| 浏览器打开两页幻灯片 | ✅ 样式正常 |
| 全屏模式 (F) | ✅ |
| 主题切换 (T) | ✅ |
| `html-ppt-deck.html` 手动示例 | ✅ 渐变文字、数据卡片正常 |

## Pitfalls for Future Sessions
1. **永远不要依赖 `../assets/` 相对路径** — skill 目录和用户输出目录不在同一层级，相对路径必然 404
2. **内联是最佳实践** — 单文件 HTML 交付，双击即用，无外部依赖
3. **验证时检查 `grep -c "assets/" deck.html`** — 应该返回 0
4. **文件大小会增加** — 内联后 HTML 从 ~10KB 增至 ~55KB，但这对演示场景是可接受的

## Related Files
- `scripts/html_export.py` — 核心修改
- `SKILL.md` Step 7.4 — 文档更新
- `references/html-export-verification.md` — 端到端验证记录
- `D:/hermes/html-ppt-deck.html` — 手动示例（已内联修复）
