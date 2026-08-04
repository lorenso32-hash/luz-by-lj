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
          closer_id=None, second_hero_id=None, third_hero_id=None, scroll_card_bg_id=None,
          sections=None, landscape_ids=None, square_ids=None, manual_swaps=None,
          flat_order=False):
    """
    sections: optional list of {"label": str, "ids": [public_id, ...]} rendered after the
    main grid, each with its own header. The scroll-card lands in the last group overall
    (last section if any, else the main grid).
    landscape_ids: optional set of public_ids that are naturally landscape orientation —
    these span the full row width instead of being cropped into the portrait grid box.
    square_ids: optional set of public_ids that are naturally square (1:1) — these stay
    in the normal 2-per-row grouping (no full-width span needed) but get centered,
    uncropped display instead of being force-cropped into the taller portrait box.
    manual_swaps: optional list of (pos_a, pos_b) 1-indexed *final* positions (hero = 1)
    to force-swap after the automatic portrait/landscape grouping — an explicit override
    for when the user wants two specific slots swapped regardless of orientation grouping.
    flat_order: if True, grid_ids is rendered exactly as given (no portrait/landscape
    regrouping) in one continuous grid — use when the caller needs landscape and
    portrait photos interleaved in a specific custom sequence.
    """
    template = Path("Raul.html").read_text()
    prefix = "../" if subdir else ""
    sections = sections or []
    landscape_ids = landscape_ids or set()
    square_ids = square_ids or set()
    manual_swaps = manual_swaps or []

    def by_orientation(ids):
        """Portraits first (own order), then landscapes (own order) — keeps portraits
        grouped in clean rows instead of getting split up by a landscape photo landing
        in the middle of them."""
        portraits = [i for i in ids if i not in landscape_ids]
        landscapes = [i for i in ids if i in landscape_ids]
        return portraits + landscapes, len(portraits)

    if not flat_order:
        grid_ids, _grid_split = by_orientation(grid_ids)
    for s in sections:
        s["ids"], s["_split"] = by_orientation(s["ids"])

    base_offset = 1 + (1 if second_hero_id else 0) + (1 if third_hero_id else 0)

    if manual_swaps:
        # map every id-list that contributes to the final rendered order, in order,
        # so a global 1-indexed position can be traced back to the exact list+index
        # holding it (regardless of which section or portrait/landscape sub-run it's in)
        # +1 because photo_num is 0-indexed (hero has photo_num 0) but the user-facing
        # "position"/"Photo N of Total" numbering is 1-indexed (hero = position 1)
        containers = [grid_ids] + [s["ids"] for s in sections]
        flat_offsets = []
        pos = base_offset + 1
        for c in containers:
            flat_offsets.append(pos)
            pos += len(c)

        def locate(global_pos):
            for c, start in zip(containers, flat_offsets):
                if start <= global_pos < start + len(c):
                    return c, global_pos - start
            raise ValueError(f"position {global_pos} is out of range (hero/closer can't be swapped this way)")

        for a, b in manual_swaps:
            c_a, i_a = locate(a)
            c_b, i_b = locate(b)
            c_a[i_a], c_b[i_b] = c_b[i_b], c_a[i_a]

    section_ids = [pid for s in sections for pid in s["ids"]]
    all_ids = [hero_id] + ([second_hero_id] if second_hero_id else []) + ([third_hero_id] if third_hero_id else []) + grid_ids + section_ids + ([closer_id] if closer_id else [])
    total = len(all_ids)

    # portrait photos in rows of 2 instead of 3 — bigger, and avoids a lone portrait
    # getting stranded on one side of a row when a landscape photo breaks up the grouping
    template = template.replace(
        "    .portrait-grid {\n"
        "      display: grid;\n"
        "      grid-template-columns: repeat(3, 1fr);",
        "    .portrait-grid {\n"
        "      display: grid;\n"
        "      grid-template-columns: repeat(2, 1fr);"
    )

    # fix hardcoded scroll-card background (carried over verbatim from Raul.html's own photo)
    bg_id = scroll_card_bg_id or hero_id
    template = re.sub(
        r"background: url\('[^']*'\) center/cover no-repeat;",
        f"background: url('{cld(bg_id, 'w_600,f_auto,q_auto')}') center/cover no-repeat;",
        template
    )

    # square (1:1) photos: stay in the normal 2-per-row grouping, but show centered
    # and uncropped instead of being force-cropped into the taller 2:3 portrait box
    template = template.replace(
        ".carousel-swipe-hint { display: none; }",
        ".carousel-swipe-hint { display: none; }\n\n"
        "    .portrait-item.square-full { aspect-ratio: 1 / 1; background: var(--navy-light); }\n"
        "    .portrait-item.square-full img { object-fit: contain; }"
    )

    # center the scroll-card, or a lone leftover portrait photo, when it lands alone
    # in its own row — otherwise it's stuck on the left with empty space on the right
    template = template.replace(
        ".carousel-swipe-hint { display: none; }",
        ".carousel-swipe-hint { display: none; }\n\n"
        "    .portrait-grid .scroll-card:only-child,\n"
        "    .portrait-grid .portrait-item:only-child:not(.landscape-full) {\n"
        "      grid-column: 1 / -1; max-width: 50%; margin: 0 auto;\n"
        "    }\n"
        "    @media (max-width: 600px) {\n"
        "      .portrait-grid .scroll-card:only-child,\n"
        "      .portrait-grid .portrait-item:only-child:not(.landscape-full) { grid-column: auto; max-width: none; margin: 0; }\n"
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
        "    }\n\n"
        "    /* mobile: landscape photos show in full within their grid cell, no crop */\n"
        "    .landscape-full { aspect-ratio: 3 / 2; background: var(--navy-light); }\n"
        "    .landscape-full img { object-fit: contain; }\n\n"
        "    /* desktop: landscape photos instead span the full row width as their own */\n"
        "    /* hero-sized block, so they don't visually clash with the portrait grid */\n"
        "    @media (min-width: 601px) {\n"
        "      .portrait-item.landscape-full { grid-column: 1 / -1; }\n"
        "      .portrait-item.landscape-full img { object-fit: cover; }\n"
        "    }"
    )

    # mobile always shows the photo-overlay (no hover state on touch) so the download
    # button stays reachable, but the desktop gradient is too dark/tall to leave on
    # permanently — lighten and shorten it just for mobile so photos don't look dim
    template = template.replace(
        "      .photo-overlay { opacity: 1; }",
        "      .photo-overlay {\n"
        "        opacity: 1;\n"
        "        background: linear-gradient(to top, rgba(5,1,33,0.85) 0%, rgba(5,1,33,0.15) 30%, transparent 55%);\n"
        "      }"
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

    third_hero_html = ''
    if third_hero_id:
        third_idx = 1 + (1 if second_hero_id else 0)
        third_hero_html = f'''

      <div class="hero-photo-wrap" data-index="{third_idx}" onclick="openLightbox({third_idx})">
        <img data-src="{cld(third_hero_id, "w_1200,f_auto,q_auto")}" alt="{page_title} — {third_idx + 1}">
        <div class="photo-overlay">
          <div class="photo-num">Photo {third_idx + 1} of {total}</div>
          {dl_btn(third_hero_id)}
        </div>
      </div>'''

    def render_grid(ids, start_num, add_scroll_card, cols):
        rows = []
        idx = 1
        n = len(ids)
        while idx <= n:
            chunk = ids[idx - 1: idx - 1 + cols]
            is_last_row = (idx - 1 + cols) >= n
            items = []
            for j, pid in enumerate(chunk):
                photo_num = start_num + idx + j - 1
                if pid in landscape_ids:
                    extra_class = ' landscape-full'
                elif pid in square_ids:
                    extra_class = ' square-full'
                else:
                    extra_class = ''
                items.append(f'''<div class="portrait-item{extra_class}" data-index="{photo_num}" onclick="openLightbox({photo_num})">
          <img data-src="{cld(pid, "w_600,f_auto,q_auto")}" alt="{page_title} — {photo_num + 1}">
          <div class="photo-overlay">
            <div class="photo-num">Photo {photo_num + 1} of {total}</div>
            {dl_btn(pid)}
          </div>
        </div>''')
            if is_last_row and add_scroll_card:
                items.append('''<div class="scroll-card" onclick="document.getElementById('download-all').scrollIntoView({behavior:'smooth'})">
          <span class="scroll-card-label">Scroll Down to Download All</span>
          <span class="scroll-card-arrow">↓</span>
        </div>''')
            rows.append('<div class="portrait-grid">\n        ' + '\n        '.join(items) + '\n      </div>')
            idx += cols
        return rows

    def render_flat(ids, start_num, add_scroll_card):
        """Renders ids in exactly the given order, one continuous grid — landscape
        items still get the full-width CSS treatment via their own class, and the
        browser's grid auto-flow handles the row breaks, so custom interleaved
        orders (unlike render_group) don't get split into portrait/landscape groups."""
        items = []
        for j, pid in enumerate(ids):
            photo_num = start_num + j
            if pid in landscape_ids:
                extra_class = ' landscape-full'
            elif pid in square_ids:
                extra_class = ' square-full'
            else:
                extra_class = ''
            items.append(f'''<div class="portrait-item{extra_class}" data-index="{photo_num}" onclick="openLightbox({photo_num})">
          <img data-src="{cld(pid, "w_600,f_auto,q_auto")}" alt="{page_title} — {photo_num + 1}">
          <div class="photo-overlay">
            <div class="photo-num">Photo {photo_num + 1} of {total}</div>
            {dl_btn(pid)}
          </div>
        </div>''')
        if add_scroll_card:
            items.append('''<div class="scroll-card" onclick="document.getElementById('download-all').scrollIntoView({behavior:'smooth'})">
          <span class="scroll-card-label">Scroll Down to Download All</span>
          <span class="scroll-card-arrow">↓</span>
        </div>''')
        return ['<div class="portrait-grid">\n        ' + '\n        '.join(items) + '\n      </div>']

    def render_group(ids, start_num, add_scroll_card, split_at):
        """Renders a group's portraits (2/row) followed by its landscapes (1/row,
        full-width) — split_at marks where the landscapes begin in `ids`."""
        portraits, landscapes = ids[:split_at], ids[split_at:]
        rows = render_grid(portraits, start_num, add_scroll_card=(add_scroll_card and not landscapes), cols=2)
        rows += render_grid(landscapes, start_num + len(portraits), add_scroll_card=add_scroll_card, cols=1)
        return rows

    if flat_order:
        grids_html = render_flat(grid_ids, base_offset, add_scroll_card=not sections)
    else:
        grids_html = render_group(grid_ids, base_offset, add_scroll_card=not sections, split_at=_grid_split)

    sections_html = ''
    running_start = base_offset + len(grid_ids)
    for i, section in enumerate(sections):
        is_final_section = (i == len(sections) - 1)
        header = f'''<div style="text-align:center; margin: 56px 0 24px;">
        <p class="eyebrow" style="margin-bottom:0;">{section["label"]}</p>
      </div>'''
        rows = render_group(section["ids"], running_start, add_scroll_card=is_final_section, split_at=section["_split"])
        sections_html += '\n\n      ' + header + '\n\n      ' + '\n\n      '.join(rows)
        running_start += len(section["ids"])

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

    body_block = hero_html + second_hero_html + third_hero_html + '\n\n      ' + '\n\n      '.join(grids_html) + sections_html + closer_html

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

    # --- Download All: fall back to the zip link if the native share actually fails ---
    # --- (not just when the user cancels the share sheet, which should stay silent) ---
    template = template.replace(
        "            await navigator.share({ files });\n"
        "          } catch(e) { /* cancelled */ }",
        "            await navigator.share({ files });\n"
        "          } catch(e) {\n"
        "            if (e.name !== 'AbortError') window.location.href = dlAllBtn.dataset.zipHref;\n"
        "          }"
    )
    template = template.replace(
        "        dlAllBtn.removeAttribute('href');\n"
        "        dlAllBtn.removeAttribute('target');",
        "        dlAllBtn.dataset.zipHref = dlAllBtn.getAttribute('href');\n"
        "        dlAllBtn.removeAttribute('href');\n"
        "        dlAllBtn.removeAttribute('target');"
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
