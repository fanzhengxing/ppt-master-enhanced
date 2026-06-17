# validate_skill.py — ppt-master 自动化验证管线

## 概述

鲁班打磨要求：每次改动后必须能快速验证是否破坏了管线。
这个脚本是验证门的守门人——它不跑完整管线（太慢），
而是做轻量级的静态+运行时检查，覆盖 P0 验证门。

## 用法

```bash
python validate_skill.py              # 全量检查
python validate_skill.py --quick      # 快速模式（只检查关键文件）
python validate_skill.py --test       # 运行测试 prompt dry-run
python validate_skill.py --strict     # 严格模式（所有检查都报错）
```

## 检查项

| # | 检查项 | 说明 |
|---|--------|------|
| 1 | 文件结构对账 | 验证关键文件/目录/脚本是否存在 |
| 2 | SKILL.md 内容质量 | frontmatter、章节、失败模式、字数 |
| 3 | Python 语法检查 | py_compile 检查所有 .py 文件 |
| 4 | requirements.txt | 依赖文件格式验证 |
| 5 | test-prompts.json | JSON 有效性 + 场景完整性 |
| 6 | Git 膨胀检查 | 图标库不被 git 追踪 |
| 7 | README 可读性 | 首屏钩子、安装指引、showcase |
| 8 | 跨 Runtime 同步 | 检测其他 runtime 副本及文件数一致性 |
| 9 | Dry-run | project_manager.py --help 运行 |

## 退出码

- 0 — 全部通过
- 1 — 有警告（非阻塞）
- 2 — 有失败（阻塞）
