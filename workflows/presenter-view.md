---
name: presenter-view
description: >-
  从生成的.pptx中提取演讲备注，生成配套的HTML演讲者视图页面。
  适合"内部分享/技术演示/培训讲解"场景——浏览器内展示演讲者视图，
  .pptx同步生成供存档。
  参考html-ppt-skill的演示场景思路，但输出保持原生.pptx + HTML双通道。
---

# Presenter View — 演讲者视图生成

> 从 ppt-master 生成的 .pptx 中提取演讲备注（Speaker Notes），
> 生成一个自包含的 HTML 演讲者视图页面。
> 输出是 **双通道**：`.pptx`（正式交付）+ `.html`（演讲辅助）。

## 何时运行

| 触发 | 行为 |
|------|------|
| 用户说"给我演讲者视图/备注/提词器" | 运行完整版 |
| 用户说"内部分享/培训/讲解/演示" | 运行精简版（含notes+翻页） |
| 用户没说但用途是"讲解型PPT" | 不做自动触发，等用户要求 |

## 工作流

### 第一步：读取演讲备注

从导出目录读取 `notes/<page_name>.md` 或 `notes/total.md`:

```bash
cat <project_path>/notes/total.md
```

格式预期：
```markdown
## slide_01
- 要点1：...
- 要点2：...
- 提示：提到这个数据时，可以补充...
## slide_02
...
```

### 第二步：提取幻灯片标题

从 SVG 源文件或 spec_lock 中读取每页标题：

```bash
grep -E "slide-title|data-slide-title|<h1>|<h2>" <project_path>/svg_output/*.svg | head -5
```

没有标题的页面用 "第N页" 代替。

### 第三步：生成 HTML 演讲者视图

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{{DECK_TITLE}} · 演讲者视图</title>
<style>
  /* 演讲者视图 - 左右分栏 */
  *{margin:0;padding:0;box-sizing:border-box}
  body{
    font-family:'Inter','Noto Sans SC',sans-serif;
    background:#0f0f0f;color:#e0e0e0;
    display:grid;grid-template-columns:1fr 1fr;
    height:100vh;overflow:hidden;
  }
  /* 左侧：幻灯片缩略/预览区 */
  .preview-panel{
    background:#1a1a1a;
    display:flex;flex-direction:column;
    padding:2rem;border-right:1px solid #333;
  }
  .preview-panel .slide-num{
    font-size:0.8rem;color:#666;margin-bottom:0.5rem;
  }
  .preview-panel .slide-preview{
    flex:1;display:flex;align-items:center;justify-content:center;
    background:#fff;border-radius:8px;
    color:#999;font-size:0.9rem;overflow:hidden;
  }
  /* 右侧：备注区 */
  .notes-panel{
    display:flex;flex-direction:column;
    padding:2.5rem;overflow-y:auto;
  }
  .notes-panel .timer{
    font-size:2.5rem;font-weight:300;color:#555;
    font-variant-numeric:tabular-nums;margin-bottom:1rem;
  }
  .notes-panel .slide-title{
    font-size:1.5rem;font-weight:600;margin-bottom:1rem;
    color:#fff;
  }
  .notes-panel .notes{
    font-size:1.05rem;line-height:1.8;color:#bbb;
  }
  .notes-panel .notes li{list-style-position:inside;margin-bottom:0.5rem}
  .notes-panel .notes .highlight{color:#00d4ff;font-weight:500}
  .notes-panel .notes .tip{color:#f59e0b;font-style:italic}
  /* 底部控制 */
  .controls{
    position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);
    display:flex;align-items:center;gap:1rem;
    background:rgba(255,255,255,0.06);
    backdrop-filter:blur(12px);padding:0.75rem 1.5rem;
    border-radius:2rem;border:1px solid rgba(255,255,255,0.08);
    z-index:100;
  }
  .controls button{
    background:transparent;border:none;color:#e0e0e0;
    font-size:1.25rem;cursor:pointer;padding:0.5rem;
    transition:opacity .2s;
  }
  .controls button:hover{opacity:1}
  .controls .progress{
    width:120px;height:4px;background:#333;border-radius:2px;overflow:hidden;
  }
  .controls .progress-bar{
    height:100%;background:#00d4ff;transition:width .3s;
  }
  .controls .page-info{font-size:0.8rem;color:#666;min-width:4em;text-align:center}
</style>
</head>
<body>
<div class="preview-panel" id="previewPanel">
  <div class="slide-num" id="slideNum">1 / {{TOTAL}}</div>
  <div class="slide-preview" id="slidePreview">
    {{PREVIEW_CONTENT}}
  </div>
</div>
<div class="notes-panel" id="notesPanel">
  <div class="timer" id="timer">00:00</div>
  <div class="slide-title" id="slideTitle">{{TITLE}}</div>
  <div class="notes" id="notes">{{NOTES_HTML}}</div>
</div>
<div class="controls">
  <button id="prevBtn">‹</button>
  <div class="progress"><div class="progress-bar" id="progressBar"></div></div>
  <span class="page-info" id="pageInfo">1 / {{TOTAL}}</span>
  <button id="nextBtn">›</button>
</div>
<script>
(function(){
  const slides = {{SLIDES_JSON}};
  let current = 0;
  const elSlideNum = document.getElementById('slideNum');
  const elPreview = document.getElementById('slidePreview');
  const elTitle = document.getElementById('slideTitle');
  const elNotes = document.getElementById('notes');
  const elProgress = document.getElementById('progressBar');
  const elPageInfo = document.getElementById('pageInfo');
  let timerSeconds = 0;
  let timerInterval;

  function show(n){
    const s = slides[n];
    elSlideNum.textContent = (n+1) + ' / ' + slides.length;
    elPreview.textContent = s.title || '第'+(n+1)+'页';
    elTitle.textContent = s.title || '第'+(n+1)+'页';
    elNotes.innerHTML = s.notes ? '<ul>'+s.notes.map(n=>'<li>'+n+'</li>').join('')+'</ul>' : '<p style="color:#555;font-style:italic">此页暂无备注</p>';
    elProgress.style.width = ((n+1)/slides.length*100)+'%';
    elPageInfo.textContent = (n+1)+' / '+slides.length;
    current = n;
  }

  document.getElementById('prevBtn').addEventListener('click',()=>{if(current>0) show(current-1)});
  document.getElementById('nextBtn').addEventListener('click',()=>{if(current<slides.length-1) show(current+1)});
  document.addEventListener('keydown',(e)=>{
    if(e.key==='ArrowRight'||e.key===' '){e.preventDefault();if(current<slides.length-1) show(current+1)}
    if(e.key==='ArrowLeft'){if(current>0) show(current-1)}
  });
  // Timer
  timerInterval = setInterval(()=>{
    timerSeconds++;
    const m = String(Math.floor(timerSeconds/60)).padStart(2,'0');
    const s = String(timerSeconds % 60).padStart(2,'0');
    document.getElementById('timer').textContent = m+':'+s;
  },1000);

  show(0);
})();
</script>
</body>
</html>
```

### 第四步：保存到项目目录

```bash
cp <演讲者视图HTML> <project_path>/presenter-view.html
```

### 第五步：交付

```
✅ 演讲者视图已生成
  - .pptx: exports/<project_name>_<timestamp>.pptx（正式交付）
  - 演讲者视图: presenter-view.html（浏览器打开 → 左右分栏显示备注+计时）
  
  打开方法：用浏览器直接打开 presenter-view.html
  快捷键：← → 翻页，空格下一页，计时自动开始
```

## 与主流程的关系

```
Step 7 Export → Presenter View（可选） → 双通道交付
```

Presenter View **跑在 Export 之后**——先导出 `.pptx`，再在读notes生成HTML。
它是**纯可选附加物**，不影响主线管线的完整性和效率。
