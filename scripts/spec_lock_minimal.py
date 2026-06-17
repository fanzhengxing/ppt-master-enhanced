#!/usr/bin/env python3
"""
spec_lock_minimal.py — 从 spec_lock.md 自动生成 spec_lock_minimal.md

精简策略：
1. 删除所有 blockquote (>) 引导行
2. 删除非运行时字段（设计叙事、推荐说明）
3. 只保留 Executor SVG 生成直接需要的字段
4. 空行清理，保持紧凑

用法:
    python3 scripts/spec_lock_minimal.py <project_path>
    
示例:
    python3 scripts/spec_lock_minimal.py projects/mydeck_20260617
"""

import sys
import os
import re
from pathlib import Path


def is_blockquote_line(line: str) -> bool:
    """检查是否是 blockquote 引导行"""
    stripped = line.strip()
    return stripped.startswith('>')


def is_placeholder_line(line: str) -> bool:
    """检查是否是占位符行（未填写的值）"""
    stripped = line.strip()
    return stripped.endswith('#......') or stripped.endswith('____')


def parse_spec_lock(content: str) -> dict:
    """
    解析 spec_lock.md，返回节名 -> 数据行列表的映射。
    跳过所有 blockquote 行和占位符行。
    """
    sections = {}
    current_section = None
    current_lines = []
    
    for line in content.split('\n'):
        # 节标题
        section_match = re.match(r'^##\s+(.+)', line)
        if section_match:
            # 保存上一个节
            if current_section is not None:
                sections[current_section] = current_lines
            
            current_section = section_match.group(1).strip()
            current_lines = []
            continue
        
        # 跳过 blockquote 行
        if is_blockquote_line(line):
            continue
        
        # 跳过纯空行（但保留节之间的单个空行）
        if line.strip() == '':
            if len(current_lines) > 0 and current_lines[-1].strip() != '':
                current_lines.append('')
            continue
        
        # 跳过占位符行
        if is_placeholder_line(line):
            continue
        
        # 保留数据行
        current_lines.append(line)
    
    # 保存最后一个节
    if current_section is not None:
        sections[current_section] = current_lines
    
    return sections


def clean_section_lines(lines: list[str]) -> list[str]:
    """清理节内的数据行：去除多余空白、注释行"""
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # 跳过行内详细解释（包含 "—" 或 "—" 的长注释行）
        if '—' in stripped or '–' in stripped:
            # 保留短注释，跳过长解释
            if len(stripped) > 80:
                continue
        cleaned.append(line)
    return cleaned


def generate_minimal(sections: dict) -> str:
    """
    从解析后的 sections 生成 spec_lock_minimal.md 内容。
    只保留 Executor 真正需要的节。
    """
    # Executor SVG 生成需要的节
    required_sections = [
        'canvas',
        'colors',
        'typography',
        'icons',
        'images',
        'page_rhythm',
        'page_layouts',
        'page_charts',
        'forbidden',
    ]
    
    # 可选节（仅在特定条件下需要）
    optional_sections = [
        'image_rendering',  # 当有 ai 图片时
        'image_palette',    # 当有 ai 图片时
    ]
    
    output_parts = ['# Execution Lock (Minimal)', '']
    
    for section_name in required_sections:
        if section_name in sections:
            output_parts.append(f'## {section_name}')
            lines = clean_section_lines(sections[section_name])
            # 过滤空行
            lines = [l for l in lines if l.strip()]
            output_parts.extend(lines)
            output_parts.append('')  # 节间空行
    
    # 检查是否需要可选节
    if 'images' in sections:
        images_lines = clean_section_lines(sections['images'])
        has_ai = any('ai' in l.lower() for l in images_lines)
        if has_ai:
            for opt in optional_sections:
                if opt in sections:
                    output_parts.append(f'## {opt}')
                    lines = clean_section_lines(sections[opt])
                    lines = [l for l in lines if l.strip()]
                    output_parts.extend(lines)
                    output_parts.append('')
    
    return '\n'.join(output_parts)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 spec_lock_minimal.py <project_path>")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    spec_lock_path = project_path / 'spec_lock.md'
    minimal_path = project_path / 'spec_lock_minimal.md'
    
    if not spec_lock_path.exists():
        print(f"Error: {spec_lock_path} not found")
        sys.exit(1)
    
    content = spec_lock_path.read_text(encoding='utf-8')
    sections = parse_spec_lock(content)
    minimal_content = generate_minimal(sections)
    
    minimal_path.write_text(minimal_content, encoding='utf-8')
    print(f"Generated: {minimal_path}")
    
    # 统计精简比例
    original_lines = len(content.split('\n'))
    minimal_lines = len(minimal_content.split('\n'))
    reduction = (1 - minimal_lines / original_lines) * 100
    print(f"Original: {original_lines} lines → Minimal: {minimal_lines} lines ({reduction:.0f}% reduction)")


if __name__ == '__main__':
    main()
