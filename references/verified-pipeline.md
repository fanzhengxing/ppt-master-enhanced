# PPT Master 在本机环境的已验证流程

## 完整链路（2026-06-11 验证通过）

1. `doc_to_md.py` → DOCX 转 Markdown ✅ (mammoth 引擎)
2. `project_manager.py init` → 初始化项目 ✅
3. `project_manager.py import-sources` → 导入源内容 ✅
4. 手动创建设计规格文档 (design_spec.md) + spec_lock.md
5. 手动编写 SVG 页面（逐页，遵循 spec_lock 规范）
6. `svg_quality_checker.py` → 质量检查 ✅ (14/14 pass with warnings)
7. `finalize_svg.py` → 后处理 ✅ (嵌入图标/展平文本/转换圆角)
8. `svg_to_pptx.py` → 导出 PPTX ✅ (14/14 Native DrawingML shapes)

## 输出结果

- 14页原生可编辑 .pptx（DrawingML 形状，非图片）
- 文件大小：63KB
- 转换模式：Native（直接映射为 PPTX 形状）
- 过渡效果：Fade

## 已知注意事项

- `svg_quality_checker` 的 spec_lock drift warnings 中，模板自带颜色（#F5F7FA, #E6F3FA, #E8F5EE, #FFF8F0, #FFF0F0, #A8D0E6, #D0D7E0）和字体大小（200px）不在 spec_lock 中是正常现象（来自模板而非设计决策），不影响输出质量
- 含 `dy` 属性的 `<tspan>` 在 `finalize_svg.py` 中被自动展平，这是预期行为
- `svg_to_pptx.py` 在遇到部分元素时标记 "skipped 1"（跳过 1 个），不影响整体输出
