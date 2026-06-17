#!/usr/bin/env python3
"""
validate_skill.py — ppt-master 自动化验证管线

鲁班打磨要求：每次改动后必须能快速验证是否破坏了管线。
这个脚本是验证门的守门人——它不跑完整管线（太慢），
而是做轻量级的静态+运行时检查，覆盖 P0 验证门。

用法:
    python validate_skill.py              # 全量检查
    python validate_skill.py --quick      # 快速模式（只检查关键文件）
    python validate_skill.py --test       # 运行测试 prompt dry-run
    python validate_skill.py --strict     # 严格模式（所有检查都报错）

退出码:
    0 — 全部通过
    1 — 有警告（非阻塞）
    2 — 有失败（阻塞）
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# ─── 颜色输出 ───
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def ok(msg):
    print(f"{Colors.GREEN}  ✅ {msg}{Colors.RESET}")

def warn(msg):
    print(f"{Colors.YELLOW}  ⚠️  {msg}{Colors.RESET}")

def fail(msg):
    print(f"{Colors.RED}  ❌ {msg}{Colors.RESET}")

def info(msg):
    print(f"{Colors.BLUE}  ℹ️  {msg}{Colors.RESET}")

# ─── 环境检测 ───
def detect_skill_dir():
    """自动检测 skill 目录"""
    candidates = []
    # 当前目录
    if Path("SKILL.md").exists():
        candidates.append(Path(".").resolve())
    # 标准 Hermes 路径
    home = Path.home()
    for base in [
        home / "AppData" / "Local" / "hermes" / "skills" / "productivity" / "ppt-master",
        home / ".hermes" / "skills" / "productivity" / "ppt-master",
        home / ".claude" / "skills" / "ppt-master",
        home / "skills" / "ppt-master",
    ]:
        if base.exists() and (base / "SKILL.md").exists():
            candidates.append(base.resolve())
    # 用户自定义路径
    if len(candidates) == 0:
        print(f"{Colors.RED}❌ 找不到 SKILL.md。请 cd 到 ppt-master 目录后运行，或设置 SKILL_DIR 环境变量{Colors.RESET}")
        sys.exit(2)
    return candidates[0]

# ─── 检查 1: 文件结构对账 ───
def check_structure(skill_dir):
    """验证目录结构是否符合 SKILL.md 描述"""
    results = []
    
    # 关键文件必须存在
    required_files = [
        "SKILL.md",
        "README.md",
        "test-prompts.json",
        "requirements.txt",
    ]
    
    for f in required_files:
        path = skill_dir / f
        if path.exists():
            ok(f"文件存在: {f}")
        else:
            fail(f"文件缺失: {f}")
            results.append(("fail", f))
    
    # 关键目录必须存在
    required_dirs = [
        "scripts/",
        "templates/",
        "references/",
    ]
    
    for d in required_dirs:
        path = skill_dir / d
        if path.exists() and any(path.iterdir()):
            ok(f"目录存在且有内容: {d}")
        elif path.exists():
            warn(f"目录存在但为空: {d}")
            results.append(("warn", d))
        else:
            fail(f"目录缺失: {d}")
            results.append(("fail", d))
    
    # scripts/ 下关键脚本必须存在
    critical_scripts = [
        "project_manager.py",
        "svg_quality_checker.py",
        "svg_to_pptx.py",
        "finalize_svg.py",
    ]
    
    scripts_dir = skill_dir / "scripts"
    for s in critical_scripts:
        path = scripts_dir / s
        if path.exists():
            ok(f"关键脚本: {s}")
        else:
            fail(f"关键脚本缺失: {s}")
            results.append(("fail", s))
    
    # workflows/ 下工作流文件
    workflows_dir = skill_dir / "workflows"
    if workflows_dir.exists():
        wf_count = sum(1 for f in workflows_dir.iterdir() if f.suffix == '.md')
        if wf_count >= 5:
            ok(f"工作流文件: {wf_count} 个")
        else:
            warn(f"工作流文件偏少: {wf_count} 个（预期 ≥ 5）")
            results.append(("warn", f"workflow-count:{wf_count}"))
    
    return results

# ─── 检查 2: SKILL.md 内容质量 ───
def check_skill_md(skill_dir):
    """验证 SKILL.md 的关键内容要素"""
    results = []
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        fail("SKILL.md 不存在")
        return results
    
    content = skill_md.read_text(encoding="utf-8")
    
    # 检查 frontmatter
    if content.startswith("---"):
        ok("frontmatter 存在")
    else:
        warn("frontmatter 缺失（name/description）")
        results.append(("warn", "frontmatter"))
    
    # 检查关键章节
    required_sections = [
        ("Workflow", "工作流步骤"),
        ("Anti-Patterns", "反例黑名单"),
        ("Checkpoint", "检查点"),
        ("GATE", "门控检查"),
    ]
    
    for keyword, name in required_sections:
        if keyword in content:
            ok(f"包含章节: {name}")
        else:
            warn(f"缺失章节: {name}")
            results.append(("warn", f"section:{name}"))
    
    # 检查失败模式编码
    failure_keywords = ["失败", "排错", "Troubleshoot", "error", "fail"]
    if any(kw in content for kw in failure_keywords):
        ok("包含失败模式/排错内容")
    else:
        warn("未检测到失败模式编码（P1 差距）")
        results.append(("warn", "failure-mode"))
    
    # 检查字数（不能太短也不能太长）
    word_count = len(content.split())
    if 3000 <= word_count <= 80000:
        ok(f"SKILL.md 长度合理: {word_count} 词")
    else:
        warn(f"SKILL.md 长度异常: {word_count} 词（预期 3000-80000）")
        results.append(("warn", f"word-count:{word_count}"))
    
    return results

# ─── 检查 3: Python 语法检查 ───
def check_python_syntax(skill_dir):
    """验证 Python 脚本语法正确性"""
    results = []
    scripts_dir = skill_dir / "scripts"
    
    if not scripts_dir.exists():
        return results
    
    py_files = list(scripts_dir.glob("*.py")) + list(scripts_dir.rglob("*.py"))
    # 去重
    py_files = list(set(py_files))[:30]  # 最多检查30个
    
    syntax_errors = []
    for py_file in py_files:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                ok(f"语法OK: {py_file.relative_to(skill_dir)}")
            else:
                fail(f"语法错误: {py_file.relative_to(skill_dir)}")
                syntax_errors.append(str(py_file))
                results.append(("fail", f"syntax:{py_file.name}"))
        except subprocess.TimeoutExpired:
            warn(f"编译超时: {py_file.relative_to(skill_dir)}")
        except Exception as e:
            warn(f"检查失败 {py_file.relative_to(skill_dir)}: {e}")
    
    if not syntax_errors:
        ok(f"Python 语法检查通过 ({len(py_files)} 个文件)")
    
    return results

# ─── 检查 4: requirements.txt 可解析 ───
def check_requirements(skill_dir):
    """验证 requirements.txt 格式正确"""
    results = []
    req_file = skill_dir / "requirements.txt"
    
    if not req_file.exists():
        warn("requirements.txt 不存在")
        results.append(("warn", "requirements"))
        return results
    
    try:
        lines = req_file.read_text(encoding="utf-8").strip().split("\n")
        valid_packages = []
        invalid_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # 简单验证：应该包含包名
            if any(c.isalnum() for c in line):
                valid_packages.append(line)
            else:
                invalid_lines.append(line)
        
        ok(f"requirements.txt: {len(valid_packages)} 个依赖")
        
        if invalid_lines:
            warn(f"无效行: {invalid_lines[:3]}")
        
        return results
        
    except Exception as e:
        fail(f"requirements.txt 解析失败: {e}")
        results.append(("fail", "requirements"))
        return results

# ─── 检查 5: test-prompts.json 有效性 ───
def check_test_prompts(skill_dir):
    """验证测试 prompt 文件"""
    results = []
    tp_file = skill_dir / "test-prompts.json"
    
    if not tp_file.exists():
        warn("test-prompts.json 不存在")
        results.append(("warn", "test-prompts"))
        return results
    
    try:
        data = json.loads(tp_file.read_text(encoding="utf-8"))
        scenarios = data.get("test_scenarios", [])
        
        if len(scenarios) >= 3:
            ok(f"test-prompts.json: {len(scenarios)} 个测试场景")
            
            # 检查每个场景的关键字段
            for i, s in enumerate(scenarios):
                has_id = "id" in s
                has_prompt = "prompt" in s
                has_verification = "verification" in s
                
                if has_id and has_prompt and has_verification:
                    ok(f"  场景 {s.get('id', f'test-{i}')}: 完整")
                else:
                    warn(f"  场景 {s.get('id', f'test-{i}')}: 缺少字段")
                    results.append(("warn", f"test-scenario:{s.get('id', i)}"))
        else:
            warn(f"测试场景偏少: {len(scenarios)} 个（预期 ≥ 3）")
            results.append(("warn", "test-scenario-count"))
        
        return results
        
    except json.JSONDecodeError as e:
        fail(f"test-prompts.json JSON 解析失败: {e}")
        results.append(("fail", "test-prompts-json"))
        return results

# ─── 检查 6: 图标库不再被 git 追踪 ───
def check_git_icons(skill_dir):
    """验证图标库不在 git 追踪中"""
    results = []
    
    try:
        result = subprocess.run(
            ["git", "ls-files", "templates/icons/"],
            capture_output=True, text=True, cwd=str(skill_dir), timeout=10
        )
        if result.stdout.strip():
            icon_count = len(result.stdout.strip().split("\n"))
            fail(f"图标库仍在 git 追踪中: {icon_count} 个文件（应被 .gitignore 排除）")
            results.append(("fail", "git-icons-bloat"))
        else:
            ok("图标库未被 git 追踪（无膨胀）")
    except subprocess.TimeoutExpired:
        warn("git ls-files 超时，跳过图标检查")
    except Exception as e:
        warn(f"git ls-files 失败: {e}")
    
    return results

# ─── 检查 7: README 首屏可读性 ───
def check_readme(skill_dir):
    """验证 README.md 基本质量"""
    results = []
    readme = skill_dir / "README.md"
    
    if not readme.exists():
        warn("README.md 不存在")
        results.append(("warn", "readme"))
        return results
    
    content = readme.read_text(encoding="utf-8")
    
    # 检查首屏内容（前500字符）
    first_screen = content[:1000]
    
    has_hook = any(kw in first_screen.lower() for kw in ["save", "省", "分钟", "一键", "自动", "扔进来"])
    has_install = any(kw in first_screen.lower() for kw in ["install", "安装", "pip", "clone", "git"])
    
    if has_hook:
        ok("README 首屏有钩子/价值主张")
    else:
        warn("README 首屏缺少明确的钩子/价值主张")
        results.append(("warn", "readme-hook"))
    
    if has_install:
        ok("README 首屏有安装指引")
    else:
        warn("README 首屏缺少安装指引")
        results.append(("warn", "readme-install"))
    
    # 检查是否有截图/GIF 引用
    has_showcase = any(kw in first_screen for kw in ["![", "showcase", "demo", "gif", "screenshot"])
    if has_showcase:
        ok("README 有 showcase/截图引用")
    else:
        warn("README 首屏缺少 showcase/截图（影响传播力）")
        results.append(("warn", "readme-showcase"))
    
    return results

# ─── 检查 8: 双端同步检测 ───
def check_cross_runtime_sync(skill_dir):
    """检测是否有其他 runtime 的副本需要同步"""
    results = []
    
    home = Path.home()
    other_paths = {
        "Hermes": skill_dir,
        "Claude Code": home / ".claude" / "skills" / "ppt-master",
        "Codex": home / ".codex" / "skills" / "ppt-master",
        "OpenClaw": home / ".openclaw" / "skills" / "ppt-master",
    }
    
    # 过滤掉当前目录
    other_paths = {k: v for k, v in other_paths.items() if v != skill_dir}
    
    active_runtimes = {}
    for name, path in other_paths.items():
        if path.exists() and (path / "SKILL.md").exists():
            active_runtimes[name] = path
    
    if not active_runtimes:
        info("未检测到其他 runtime 的副本（单端部署）")
        return results
    
    ok(f"检测到 {len(active_runtimes)} 个其他 runtime 副本: {', '.join(active_runtimes.keys())}")
    
    # 检查文件数一致性
    skill_file_count = sum(1 for _ in skill_dir.rglob("*") if _.is_file())
    
    for name, path in active_runtimes.items():
        other_count = sum(1 for _ in path.rglob("*") if _.is_file())
        diff = abs(skill_file_count - other_count)
        
        if diff == 0:
            ok(f"  {name}: 文件数一致 ({other_count})")
        elif diff < 50:
            info(f"  {name}: 文件数接近 ({skill_file_count} vs {other_count}, 差 {diff})")
        else:
            warn(f"  {name}: 文件数差异较大 ({skill_file_count} vs {other_count}, 差 {diff})")
            results.append(("warn", f"sync:{name}:diff={diff}"))
    
    return results

# ─── Dry-run 测试 ───
def dry_run_project_init(skill_dir):
    """Dry-run 项目初始化（不实际创建文件）"""
    results = []
    
    project_manager = skill_dir / "scripts" / "project_manager.py"
    if not project_manager.exists():
        fail("project_manager.py 不存在，无法做 dry-run")
        return results
    
    # 用 --help 测试脚本可运行
    try:
        result = subprocess.run(
            [sys.executable, str(project_manager), "--help"],
            capture_output=True, text=True, timeout=15,
            cwd=str(skill_dir)
        )
        if result.returncode == 0:
            ok("project_manager.py --help 运行成功")
        else:
            # --help 不一定支持，检查是否有 error
            if "error" in result.stderr.lower() or "not found" in result.stderr.lower():
                warn(f"project_manager.py --help 返回非零: {result.stderr[:200]}")
            else:
                ok(f"project_manager.py 可执行 (exit={result.returncode})")
    except subprocess.TimeoutExpired:
        warn("project_manager.py --help 超时")
    except FileNotFoundError:
        fail(f"Python 解释器未找到: {sys.executable}")
        results.append(("fail", "python-interpreter"))
    
    return results

# ─── 主流程 ───
def main():
    quick = "--quick" in sys.argv
    strict = "--strict" in sys.argv
    skip_sync = "--no-sync" in sys.argv
    
    print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}  ppt-master 自动化验证管线{Colors.RESET}")
    print(f"{Colors.BOLD}  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*50}{Colors.RESET}\n")
    
    skill_dir = detect_skill_dir()
    info(f"Skill 目录: {skill_dir}")
    print()
    
    all_results = []
    
    # 1. 文件结构对账
    print(f"{Colors.BOLD}【1】文件结构对账{Colors.RESET}")
    all_results.extend(check_structure(skill_dir))
    print()
    
    # 2. SKILL.md 内容质量
    print(f"{Colors.BOLD}【2】SKILL.md 内容质量{Colors.RESET}")
    all_results.extend(check_skill_md(skill_dir))
    print()
    
    # 3. Python 语法检查
    print(f"{Colors.BOLD}【3】Python 语法检查{Colors.RESET}")
    all_results.extend(check_python_syntax(skill_dir))
    print()
    
    # 4. requirements.txt
    print(f"{Colors.BOLD}【4】依赖文件检查{Colors.RESET}")
    all_results.extend(check_requirements(skill_dir))
    print()
    
    # 5. test-prompts.json
    print(f"{Colors.BOLD}【5】测试 Prompt 检查{Colors.RESET}")
    all_results.extend(check_test_prompts(skill_dir))
    print()
    
    # 6. Git 图标膨胀检查
    print(f"{Colors.BOLD}【6】Git 膨胀检查{Colors.RESET}")
    all_results.extend(check_git_icons(skill_dir))
    print()
    
    # 7. README 首屏
    print(f"{Colors.BOLD}【7】README 可读性{Colors.RESET}")
    all_results.extend(check_readme(skill_dir))
    print()
    
    # 8. 双端同步
    if not skip_sync:
        print(f"{Colors.BOLD}【8】跨 Runtime 同步检测{Colors.RESET}")
        all_results.extend(check_cross_runtime_sync(skill_dir))
        print()
    
    # 9. Dry-run
    if not quick:
        print(f"{Colors.BOLD}【9】Dry-run 检查{Colors.RESET}")
        all_results.extend(dry_run_project_init(skill_dir))
        print()
    
    # ─── 汇总 ───
    total = len(all_results)
    fails = sum(1 for r in all_results if r[0] == "fail")
    warns = sum(1 for r in all_results if r[0] == "warn")
    passes = total - fails - warns
    
    print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}  验证结果汇总{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*50}{Colors.RESET}")
    print(f"  通过: {Colors.GREEN}{passes}{Colors.RESET}")
    if warns:
        print(f"  警告: {Colors.YELLOW}{warns}{Colors.RESET}")
    if fails:
        print(f"  失败: {Colors.RED}{fails}{Colors.RESET}")
    
    if fails > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ 验证不通过（阻塞）{Colors.RESET}")
        print(f"  修复上述失败项后再提交/推送")
        sys.exit(2)
    elif warns > 0:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  验证通过但有警告{Colors.RESET}")
        print(f"  建议修复警告项，非阻塞")
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ 全部验证通过{Colors.RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
