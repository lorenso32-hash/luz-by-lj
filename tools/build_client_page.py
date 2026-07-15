"""
Generate a new client gallery page from Raul.html's template (hero + portrait grids +
neon CTA + Web Share API downloads). Run from the Luz By LJ root directory.
"""

import re
from pathlib import Path

CLOUD = "diitxd6ou"
BASE = f"https://res.cloudinary.com/{CLOUD}/image/upload"

def cld(public_id, transform):
    return f"{BASE}/{transform}/{public_id}"

def build(title, page_title, hero_id, grid_ids, download_all_url, out_path, subdir=True,
          closer_id=None, second_hero_id=None, scroll_card_bg_id=None):
    template = Path("Raul.html").read_text()
    prefix = "../" if subdir else ""

    all_ids = [hero_id] + ([second_hero_id] if second_hero_id else []) + grid_ids + ([closer_id] if closer_id else [])
    total = len(all_ids)
    base_offset = 1 + (1 if second_hero_id else 0)

    # fix hardcoded scroll-card background (carried over verbatim from Raul.html's own photo)
    bg_id = scroll_card_bg_id or hero_id
    template = re.sub(
        r"background: url\('[^']*'\) center/cover no-repeat;",
        f"background: url('{cld(bg_id, 'w_600,f_auto,q_auto')}') center/cover no-repeat;",
        template
    )

    # center the scroll-card on desktop when it lands alone in its own row
    template = template.replace(
        ".carousel-swipe-hint { display: none; }",
        ".carousel-swipe-hint { display: none; }\n\n"
        "    .portrait-grid .scroll-card:only-child { grid-column: 2; }\n"
        "    @media (max-width: 600px) {\n"
        "      .portrait-grid .scroll-card:only-child { grid-column: auto; }\n"
        "    }"
    )

    # mobile scroll-perf fixes: backdrop-filter blur and box-shadow star animations
    # are both expensive repaint work during scroll on mid-range/older mobile GPUs
    template = template.replace(
        "    .carousel-swipe-hint { display: none; }",
        "    .carousel-swipe-hint { display: none; }\n\n"
        "    @media (max-width: 600px) {\n"
        "      nav { backdrop-filter: none; background: rgba(5,1,33,0.95); }\n"
        "      .star { animation-name: twinkle !important; }\n"
        "    }"
    )

    # --- head ---
    template = template.replace(
        "<title>Raul Pacheco — Session | Luz by LJ</title>",
        f"<title>{title}</title>"
    )
    template = template.replace('href="Luz By LJ Logo 2.png"', f'href="{prefix}Luz By LJ Logo 2.png"')
    template = template.replace('href="index.html"', f'href="{prefix}index.html"')
    template = template.replace('src="Luz By LJ Logo 2.png"', f'src="{prefix}Luz By LJ Logo 2.png"')
    template = template.replace(
        '<h1 class="page-title">Raul Pacheco</h1>',
        f'<h1 class="page-title">{page_title}</h1>'
    )

    # --- hero + grids ---
    dl_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'

    def dl_btn(pid):
        return f'<a class="dl-btn-sm" href="{cld(pid, "fl_attachment")}" target="_blank" onclick="event.stopPropagation()">{dl_icon} Download</a>'

    hero_html = f'''<div class="hero-photo-wrap" data-index="0" onclick="openLightbox(0)">
        <img src="{cld(hero_id, "w_1200,f_auto,q_auto")}" alt="{page_title} — 1">
        <div class="photo-overlay">
          <div class="photo-num">Photo 1 of {total}</div>
          {dl_btn(hero_id)}
        </div>
      </div>'''

    second_hero_html = ''
    if second_hero_id:
        second_hero_html = f'''

      <div class="hero-photo-wrap" data-index="1" onclick="openLightbox(1)">
        <img data-src="{cld(second_hero_id, "w_1200,f_auto,q_auto")}" alt="{page_title} — 2">
        <div class="photo-overlay">
          <div class="photo-num">Photo 2 of {total}</div>
          {dl_btn(second_hero_id)}
        </div>
      </div>'''

    grids_html = []
    idx = 1
    n = len(grid_ids)
    while idx <= n:
        chunk = grid_ids[idx - 1: idx - 1 + 3]
        is_last = (idx - 1 + 3) >= n
        items = []
        for j, pid in enumerate(chunk):
            photo_num = idx + j + (base_offset - 1)
            items.append(f'''<div class="portrait-item" data-index="{photo_num}" onclick="openLightbox({photo_num})">
          <img data-src="{cld(pid, "w_600,f_auto,q_auto")}" alt="{page_title} — {photo_num + 1}">
          <div class="photo-overlay">
            <div class="photo-num">Photo {photo_num + 1} of {total}</div>
            {dl_btn(pid)}
          </div>
        </div>''')
        if is_last:
            items.append('''<div class="scroll-card" onclick="document.getElementById('download-all').scrollIntoView({behavior:'smooth'})">
          <span class="scroll-card-label">Scroll Down to Download All</span>
          <span class="scroll-card-arrow">↓</span>
        </div>''')
        grids_html.append('<div class="portrait-grid">\n        ' + '\n        '.join(items) + '\n      </div>')
        idx += 3

    closer_html = ''
    if closer_id:
        closer_idx = total - 1
        closer_html = f'''

      <div class="hero-photo-wrap" data-index="{closer_idx}" onclick="openLightbox({closer_idx})">
        <img data-src="{cld(closer_id, "w_1200,f_auto,q_auto")}" alt="{page_title} — {total}">
        <div class="photo-overlay">
          <div class="photo-num">Photo {total} of {total}</div>
          {dl_btn(closer_id)}
        </div>
      </div>'''

    body_block = hero_html + second_hero_html + '\n\n      ' + '\n\n      '.join(grids_html) + closer_html

    template = re.sub(
        r'<!-- Hero -->.*?<!-- /\.portrait-carousel-wrap -->',
        body_block + '\n\n        <div id="carousel-swipe-hint" class="carousel-swipe-hint">Swipe &nbsp;&#8594;</div>\n      </div><!-- /.portrait-carousel-wrap -->',
        template,
        flags=re.DOTALL
    )

    # --- download-all button ---
    template = re.sub(
        r'<div class="download-wrap" id="download-all">.*?</div>\n\n  <footer>',
        f'''<div class="download-wrap" id="download-all">
    <a href="{download_all_url}" target="_blank" rel="noopener" class="btn-download">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 16l-5-5h3V4h4v7h3l-5 5zm-7 2h14v2H5v-2z"/></svg>
      Download All Photos
    </a>
  </div>

  <footer>''',
        template,
        flags=re.DOTALL
    )

    # --- preconnect to Cloudinary (reduces first-request latency for lazy images) ---
    template = template.replace(
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://res.cloudinary.com" crossorigin>\n'
        '  <link rel="preconnect" href="https://fonts.googleapis.com">'
    )

    # --- manual lazy-load with a large rootMargin: starts fetching well before the image ---
    # --- is visible (unlike native loading="lazy"), so it's already loaded by the time you scroll to it ---
    lazy_js = '''
    // Lazy-load images ahead of viewport so they're ready before you scroll to them
    const lazyImgs = document.querySelectorAll('img[data-src]');
    const lazyObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          lazyObserver.unobserve(img);
        }
      });
    }, { rootMargin: '800px 0px' });
    lazyImgs.forEach(img => lazyObserver.observe(img));
'''
    template = template.replace('</script>', lazy_js + '  </script>')

    # --- lightbox photos JS array ---
    photos_js = ',\n      '.join(
        f"{{ id: '{pid}', alt: '{page_title} — {i+1}' }}" for i, pid in enumerate(all_ids)
    )
    template = re.sub(
        r"const photos = \[.*?\];",
        f"const photos = [\n      {photos_js}\n    ];",
        template,
        count=1,
        flags=re.DOTALL
    )

    Path(out_path).write_text(template)
    print(f"Wrote {out_path} ({total} photos)")
