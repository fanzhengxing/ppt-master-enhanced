#!/usr/bin/env python3
"""
PPT Master - HTML Deck Export Tool

Generates an interactive HTML presentation from ppt-master project assets.
Reads SVG pages + speaker notes, produces a single self-contained HTML file
with presenter mode (S key), theme support, and animations.

Usage:
    python3 scripts/html_export.py <project_path> [--theme THEME] [--output DIR]

Examples:
    python3 scripts/html_export.py projects/my_deck_ppt169_20260616
    python3 scripts/html_export.py projects/my_deck_ppt169_20260616 --theme minimal-white
    python3 scripts/html_export.py projects/my_deck_ppt169_20260616 --output exports/
"""

import sys
import argparse
import json
import re
from pathlib import Path


def read_svg_file(svg_path: Path) -> str:
    """Read SVG file and return cleaned content."""
    content = svg_path.read_text(encoding='utf-8')
    return content


def read_notes_file(notes_path: Path) -> str:
    """Read speaker notes and strip leading # heading if present."""
    content = notes_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    # Strip leading level-1 heading (slide title)
    if lines and re.match(r'^#\s+', lines[0]):
        lines = lines[1:]
    return '\n'.join(lines).strip()


def read_spec_lock(project_path: Path) -> dict:
    """Parse spec_lock.md into a dict for theme/color/font selection."""
    spec_lock_path = project_path / 'spec_lock.md'
    if not spec_lock_path.exists():
        return {}
    
    content = spec_lock_path.read_text(encoding='utf-8')
    result = {}
    current_section = None
    
    for line in content.splitlines():
        m = re.match(r'^##\s+(\w+)', line)
        if m:
            current_section = m.group(1)
            result[current_section] = {}
            continue
        
        if current_section and line.startswith('- '):
            parts = line[2:].split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().strip('"').strip("'")
                result[current_section][key] = val
    
    return result


def find_theme_for_project(spec_lock: dict) -> str:
    """Pick an html-ppt theme that matches the project's design."""
    colors = spec_lock.get('colors', {})
    bg = colors.get('bg', '#FFFFFF').upper()
    
    # Simple heuristic: dark backgrounds → dark theme
    if bg in ['#1A1A2E', '#16213E', '#0F0F0F', '#2D2D2D', '#000000', '#1A1A1A']:
        return 'minimal-dark'
    
    # Corporate blues
    if any(k in bg.upper() for k in ['#3B', '#4B', '#5B']):
        return 'corporate-clean'
    
    # Default: clean white
    return 'minimal-white'


def sanitize_html(text: str) -> str:
    """Escape HTML special characters for safe embedding."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def build_html_deck(project_path: Path, theme: str, output_dir: Path, 
                    include_assets: bool = True) -> Path:
    """Build the complete HTML deck file."""
    
    svg_dir = project_path / 'svg_output'
    notes_dir = project_path / 'notes'
    spec_lock = read_spec_lock(project_path)
    
    if not svg_dir.exists():
        print(f"Error: svg_output directory not found at {svg_dir}", file=sys.stderr)
        sys.exit(1)
    
    svg_files = sorted(svg_dir.glob('*.svg'))
    if not svg_files:
        print(f"Error: No SVG files found in {svg_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Build slides array
    slides = []
    for svg_path in svg_files:
        stem = svg_path.stem
        
        # Find matching notes
        notes_content = ""
        notes_file = notes_dir / f"{stem}.md"
        if notes_file.exists():
            notes_content = read_notes_file(notes_file)
        
        # Extract title from SVG if possible
        svg_content = read_svg_file(svg_path)
        title = stem
        
        # Try to find text content in SVG for the title
        title_match = re.search(r'<text[^>]*>([^<]{2,50})</text>', svg_content)
        if title_match:
            title = title_match.group(1).strip()
        
        slides.append({
            'title': title,
            'svg': svg_content,
            'notes': notes_content,
            'file': stem
        })
    
    # Theme CSS from spec_lock colors
    theme_css = generate_theme_css(spec_lock, theme)
    
    # Build the HTML
    html = build_full_html(slides, theme, theme_css, len(svg_files))
    
    # Write output
    output_file = output_dir / 'deck.html'
    output_file.write_text(html, encoding='utf-8')
    
    # Note: assets are now inlined into the HTML, so no external files needed.
    # The include_assets parameter is kept for backward compatibility but is ignored.
    if include_assets:
        print(f"  (Note: assets are now inlined — no external files required)")
    
    print(f"[OK] HTML deck: {output_file}")
    print(f"[OK] {len(slides)} slides exported")
    print(f"[OK] Theme: {theme}")
    
    return output_file


def generate_theme_css(spec_lock: dict, base_theme: str) -> str:
    """Generate a custom theme CSS from spec_lock colors."""
    colors = spec_lock.get('colors', {})
    typography = spec_lock.get('typography', {})
    
    css_parts = [f'/* Custom theme from spec_lock — overrides {base_theme} */']
    css_parts.append(':root {')
    
    # Map spec_lock colors to html-ppt tokens
    color_map = {
        '--bg': colors.get('bg', '#FFFFFF'),
        '--text-1': colors.get('text', '#111216'),
        '--text-2': colors.get('text_secondary', '#55596a'),
        '--text-3': colors.get('text_secondary', '#8a8f9e'),
        '--accent': colors.get('primary', '#3b6cff'),
        '--accent-2': colors.get('secondary_accent', '#7a5cff'),
    }
    
    for token, value in color_map.items():
        if value and value != '#......' and value != '':
            css_parts.append(f'  {token}: {value};')
    
    # Typography
    if typography:
        default_font = '"Microsoft YaHei", Arial, sans-serif'
        font_sans = typography.get('font_family', default_font)
        font_display = typography.get('title_family', typography.get('font_family', default_font))
        css_parts.append('  --font-sans: ' + font_sans + ';')
        css_parts.append('  --font-display: ' + font_display + ';')
        body_size = typography.get('body', '16')
        if body_size:
            css_parts.append('  --font-body: ' + body_size + 'px;')
    
    css_parts.append('}')
    
    return '\n'.join(css_parts)


def _read_asset(asset_path: Path) -> str:
    """Read an asset file, return empty string if missing."""
    try:
        return asset_path.read_text(encoding='utf-8')
    except Exception:
        return ""


def build_full_html(slides: list, theme: str, theme_css: str, total: int,
                    asset_dir: Path = None) -> str:
    """Build the complete standalone HTML deck — fully self-contained.
    
    All CSS (fonts, base, animations, theme) and JS (runtime) are inlined
    into <style>/<script> tags so the output is a single file that works
    offline with no external dependencies.
    """
    skill_dir = Path(__file__).resolve().parent.parent
    
    # Resolve asset directory: caller-supplied > skill dir > None
    assets = asset_dir or (skill_dir / 'assets')
    
    # Read all CSS sources
    fonts_css = _read_asset(assets / 'fonts.css')
    base_css = _read_asset(assets / 'base.css')
    animations_css = _read_asset(assets / 'animations.css')
    theme_css_file = _read_asset(assets / 'themes' / f'{theme}.css') if theme != 'minimal-white' else ""
    
    # Build inline CSS: fonts + base + theme override + animations + custom
    inline_css = "\n".join([
        "/* ── html-ppt :: INLINE ASSETS (self-contained) ── */",
        fonts_css,
        base_css,
        theme_css_file,
        theme_css,
        animations_css,
        """
/* Inline slide SVG styling */
.slide img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  position: absolute;
  top: 0;
  left: 0;
}
.notes { display: none !important; }
""",
    ])
    
    # Read JS runtime
    runtime_js = _read_asset(assets / 'runtime.js')
    
    # Encode slides as JSON for runtime.js
    slides_json = json.dumps([{
        'title': s['title'],
        'notes': s['notes'],
        'svg': s['svg']
    } for s in slides], ensure_ascii=False)
    
    # Detect theme list from available theme files
    theme_names = "minimal-white,corporate-clean"
    if theme != 'minimal-white' and theme_css_file:
        theme_names = f"{theme},{theme_names}"
    # Add any extra themes found in assets/themes
    if assets.exists():
        extra_themes = [f.stem for f in (assets / 'themes').glob('*.css')
                       if f.stem != theme]
        if extra_themes:
            theme_names = f"{theme_names},{','.join(extra_themes)}"
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN" data-theme="{theme}" data-themes="{theme_names}">
<head>
<meta charset="utf-8">
<title>Presentation</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
{inline_css}
</style>
</head>
<body>

<div class="deck">
'''
    
    for i, slide in enumerate(slides):
        svg_b64 = _svg_to_base64(slide['svg'])
        notes_b64 = _escape_notes(slide['notes'])
        title_esc = sanitize_html(slide['title'])
        html += '\n  <section class="slide" data-title="' + title_esc + '" data-anim="fade-up" data-index="' + str(i) + '">'
        html += '\n    <img src="data:image/svg+xml;base64,' + svg_b64 + '" alt="' + title_esc + '">'
        html += '\n    <div class="notes">' + notes_b64 + '</div>'
        html += '\n  </section>\n'
    
    html += '''
</div>

'''
    if runtime_js:
        html += f'<script>\n{runtime_js}\n</script>\n'
    else:
        html += '<!-- WARNING: runtime.js not found — presenter mode and animations disabled -->\n'
    
    html += '''
<script>
// Inject slides metadata for runtime.js presenter mode
window.__SLIDES_DATA__ = ''' + slides_json + ''';
</script>

</body>
</html>'''
    
    return html

def _svg_to_base64(svg_content: str) -> str:
    """Convert SVG content to base64 for data URI embedding."""
    import base64
    svg_bytes = svg_content.encode('utf-8')
    return base64.b64encode(svg_bytes).decode('ascii')


def _escape_notes(notes: str) -> str:
    """Escape notes for safe embedding in HTML."""
    import base64
    return base64.b64encode(notes.encode('utf-8')).decode('ascii')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='PPT Master - HTML Deck Export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s projects/my_deck_ppt169_20260616
  %(prog)s projects/my_deck_ppt169_20260616 --theme corporate-clean
  %(prog)s projects/my_deck_ppt169_20260616 --output exports/
        """
    )
    
    parser.add_argument('project_path', type=str, help='Project directory path')
    parser.add_argument('--theme', type=str, default=None,
                        help='Theme name (default: auto-detect from spec_lock)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output directory (default: <project>/exports/)')
    parser.add_argument('--no-assets', action='store_true',
                        help='Do not copy assets (use if assets are already present)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"Error: Path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)
    
    # Determine theme
    spec_lock = read_spec_lock(project_path)
    if args.theme:
        theme = args.theme
    else:
        theme = find_theme_for_project(spec_lock)
    
    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = project_path / 'exports'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not args.quiet:
        print("PPT Master - HTML Deck Export")
        print("=" * 50)
        print(f"  Project: {project_path}")
        print(f"  Theme: {theme}")
        print(f"  Output: {output_dir}")
        print()
    
    build_html_deck(project_path, theme, output_dir, include_assets=not args.no_assets)


if __name__ == '__main__':
    main()
