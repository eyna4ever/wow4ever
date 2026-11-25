/**
 * Wowkipedia shared header behaviour (lots L1/L1b): mega-menu disclosures, mobile accordion drawer and search overlay.
 * Progressive enhancement: without JavaScript the menu stays a plain list and the magnifier links to the
 * home search. No inline script/style, no network request other than the same-origin search-index.json and, once the reader
 * types, search-detail-fr.json / search-detail-en.json (v42b: NPCs, items, quests, materials, recipes… with their exact anchor).
 */
import {prepareSearch, searchPrepared, entryTitle, localized, normalizeQuery, detailSnippet, prepareDetails, searchDetails} from './ui-core.mjs?v=42c';  // v42c: versioned URL (no stale module after an update)

const header = document.querySelector('[data-wk-header]');
if (header && !header.dataset.wkReady) {
  header.dataset.wkReady = '1';
  const lang = header.dataset.lang === 'en' ? 'en' : 'fr';
  const t = (fr, en) => lang === 'en' ? en : fr;
  const nav = header.querySelector('#wk-nav');
  const burger = header.querySelector('#wk-menu-toggle');
  const tops = [...header.querySelectorAll('.wk-has-panel > .wk-top')];
  const mobile = window.matchMedia('(max-width: 1220px)')  /* same breakpoint as site.css (drawer) */;
  header.classList.add('is-enhanced');
  burger.hidden = false;

  const panelOf = button => document.getElementById(button.getAttribute('aria-controls'));
  const setPanel = (button, open) => {
    button.setAttribute('aria-expanded', String(open));
    panelOf(button).hidden = !open;
    button.parentElement.classList.toggle('is-open', open);
  };
  const closePanels = except => tops.forEach(button => { if (button !== except) setPanel(button, false); });
  const setDrawer = open => {
    if (open) header.style.setProperty('--wk-bar', `${Math.round(header.getBoundingClientRect().bottom)}px`);
    burger.setAttribute('aria-expanded', String(open));
    burger.querySelector('.visually-hidden').textContent = open ? t('Fermer le menu', 'Close menu') : t('Menu', 'Menu');
    nav.classList.toggle('is-open', open);
    document.documentElement.classList.toggle('wk-drawer-open', open);
    if (!open) closePanels();
  };
  burger.querySelector('.visually-hidden').textContent = t('Menu', 'Menu');

  tops.forEach(button => {
    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') !== 'true';
      // Desktop mega-menu and mobile accordion alike: one panel open at a time.
      closePanels(button);
      setPanel(button, open);
    });
  });
  burger.addEventListener('click', () => setDrawer(burger.getAttribute('aria-expanded') !== 'true'));
  mobile.addEventListener?.('change', () => { setDrawer(false); closePanels(); });

  // Escape closes the innermost open layer and returns focus to its trigger.
  header.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    const open = tops.find(button => button.getAttribute('aria-expanded') === 'true');
    if (open) { setPanel(open, false); open.focus(); event.preventDefault(); return; }
    if (nav.classList.contains('is-open')) { setDrawer(false); burger.focus(); event.preventDefault(); }
  });
  // Desktop: leaving the menu (focus or click elsewhere) closes the open panel.
  header.addEventListener('focusout', event => {
    if (mobile.matches) return;
    tops.forEach(button => { if (!event.relatedTarget || !button.parentElement.contains(event.relatedTarget)) setPanel(button, false); });
  });
  document.addEventListener('click', event => {
    if (!header.contains(event.target)) { closePanels(); if (nav.classList.contains('is-open')) setDrawer(false); }
  });
  // Mobile drawer: keep Tab inside the header while the drawer is open.
  header.addEventListener('keydown', event => {
    if (event.key !== 'Tab' || !mobile.matches || !nav.classList.contains('is-open')) return;
    const items = [burger, ...nav.querySelectorAll('a[href], button')].filter(node => node.offsetParent !== null);
    const first = items[0], last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) { last.focus(); event.preventDefault(); }
    else if (!event.shiftKey && document.activeElement === last) { first.focus(); event.preventDefault(); }
  });

  // ---- v42b: arriving on an anchor (search result) opens the folded block that holds it and marks it ----------
  const reveal = () => {
    let id = '';
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = id && document.getElementById(id);
    if (!target) return;
    for (let node = target; node; node = node.parentElement) if (node.tagName === 'DETAILS') node.open = true;
    document.querySelectorAll('.wk-hit').forEach(node => node.classList.remove('wk-hit'));
    target.classList.add('wk-hit');
    const place = () => target.scrollIntoView({behavior: 'instant', block: target.tagName === 'DETAILS' || target.offsetHeight > innerHeight / 2 ? 'start' : 'center'});
    place();
    // images and fonts loading above the target move it: keep it in place for 2.5 s, unless the reader scrolls first
    if (typeof ResizeObserver !== 'function') return;
    const watch = new ResizeObserver(place), stop = () => { watch.disconnect(); ['wheel', 'touchstart', 'keydown'].forEach(e => removeEventListener(e, stop)); };
    watch.observe(document.body); ['wheel', 'touchstart', 'keydown'].forEach(e => addEventListener(e, stop, {passive: true}));
    setTimeout(stop, 2500);
  };
  reveal();
  window.addEventListener('hashchange', reveal);
  if (document.readyState !== 'complete') window.addEventListener('load', reveal, {once: true});  // re-centre once images have their size

  // ---- Search overlay -------------------------------------------------------------------------
  const overlay = document.getElementById('wk-search');
  const opener = header.querySelector('[data-wk-search-open]');
  const input = document.getElementById('wk-search-input');
  const results = document.getElementById('wk-search-results');
  const status = document.getElementById('wk-search-status');
  const allLink = document.getElementById('wk-search-all');
  const registry = overlay?.dataset.registry ?? '';
  const preview = overlay?.querySelector('form')?.hasAttribute('data-preview');
  const indexURL = new URL('search-index.json', import.meta.url);
  const detailURL = new URL(`search-detail-${lang}.json`, import.meta.url);  // v42b: detailed entries, loaded when the reader types
  let index = null, prepared = null, loading = null, lastFocus = null, timer = 0;
  let details = null, detailLoading = null, dtype = -1, dlimit = 20, dquery = '';

  const getJSON = url => fetch(url, {credentials: 'same-origin'})
    .then(response => response.ok ? response.json() : Promise.reject(new Error(String(response.status))));
  const load = () => loading ??= getJSON(indexURL)
    .then(data => { index = data; prepared = prepareSearch(data.entries); return data; }) // v17: normalized once
    .catch(() => { index = {categories: [], entries: [], failed: true}; return index; });

  // v17: matched terms in result titles wrapped in <mark> (DOM nodes and textContent only, no HTML parsing).
  const fold = text => text.normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('en');
  const highlight = (node, text, terms) => {
    const folded = [...text].map(fold).join(''); // same length as text for Latin letters with accents
    const marks = [];
    if (folded.length === text.length) for (const term of terms) { let at = folded.indexOf(term); while (at !== -1 && term) { marks.push([at, at + term.length]); at = folded.indexOf(term, at + term.length); } }
    marks.sort((a, b) => a[0] - b[0]);
    let last = 0;
    for (const [start, end] of marks) {
      if (start < last) continue;
      node.append(text.slice(last, start));
      const mark = document.createElement('mark'); mark.textContent = text.slice(start, end); node.append(mark);
      last = end;
    }
    node.append(text.slice(last));
  };
  const categoryName = id => (index?.categories ?? []).find(item => item[0] === id)?.[lang === 'en' ? 2 : 1] ?? '';
  const loadDetails = () => detailLoading ??= getJSON(detailURL)
    .then(data => { details = prepareDetails(data, lang) ?? {failed: true}; })
    .catch(() => { details = {failed: true}; });
  // v42b: results inside the pages (NPC, creature, quest, item, material, recipe, mount…), each linking to its anchor.
  const dbox = document.createElement('div');
  dbox.className = 'wk-dresults'; dbox.hidden = true;
  results?.after(dbox);
  let pageTotal = 0;
  const plural = (n, fr, en) => t(`${n} ${fr}${n > 1 ? 's' : ''}`, `${n} ${en}${n > 1 ? 's' : ''}`);
  const renderDetails = query => {
    dbox.replaceChildren(); dbox.hidden = true;
    const folded = normalizeQuery(query);
    if (folded !== dquery) { dquery = folded; dtype = -1; dlimit = 20; }
    if (folded.length < 2) return;
    if (!details) { loadDetails().then(() => { if (normalizeQuery(input.value.slice(0, 120)) === folded) renderDetails(query); }); return; }
    if (details.failed) return;
    const found = searchDetails(details, {query, type: dtype, limit: dlimit});
    const pages = pageTotal ? plural(pageTotal, 'page', 'page') : t('aucune page', 'no page');
    if (found.total) status.textContent = t(`${pages} · ${found.total} élément${found.total > 1 ? 's' : ''} dans les pages`, `${pages} · ${found.total} item${found.total > 1 ? 's' : ''} inside pages`);
    if (!found.total) return;
    dbox.hidden = false;
    const head = document.createElement('p'); head.className = 'wk-dhead';
    head.textContent = t('Dans les pages : PNJ, objets, quêtes, matériaux, recettes…', 'Inside pages: NPCs, items, quests, materials, recipes…');
    const bar = document.createElement('div'); bar.className = 'wk-dfilters'; bar.setAttribute('role', 'group'); bar.setAttribute('aria-label', t('Filtrer par type', 'Filter by type'));
    const chip = (label, value, n) => {
      const button = document.createElement('button'); button.type = 'button'; button.className = 'wk-dfilter';
      button.setAttribute('aria-pressed', String(dtype === value)); button.textContent = `${label} (${n})`;
      button.addEventListener('click', () => { dtype = dtype === value ? -1 : value; dlimit = 20; renderDetails(input.value.slice(0, 120)); dbox.querySelector('[aria-pressed="true"]')?.focus(); });
      bar.append(button);
    };
    chip(t('Tous', 'All'), -1, found.total);
    for (const [type, n] of Object.entries(found.counts).sort((a, b) => b[1] - a[1])) chip(details.types[type].label, Number(type), n);
    const list = document.createElement('ul'); list.className = 'wk-search-results wk-dlist'; list.setAttribute('aria-label', t('Résultats dans les pages', 'Results inside pages'));
    for (const item of found.results) {
      const page = details.pages[item.page];
      const li = document.createElement('li'); const link = document.createElement('a');
      link.href = new URL(page.path + (preview ? 'index.html' : '') + '#' + item.anchor, indexURL).href;
      link.className = 'wk-result';
      const kind = document.createElement('span'); kind.className = 'wk-result-cat'; kind.textContent = details.types[item.type].label;
      const title = document.createElement('strong'); highlight(title, item.name, found.terms);
      const text = document.createElement('span'); text.className = 'wk-result-text'; text.textContent = [detailSnippet(item, found.terms), page.title].filter(Boolean).join(' — ');
      link.append(kind, title, text); li.append(link); list.append(li);
    }
    dbox.append(head, bar, list);
    if (found.shown > found.results.length) {
      const more = document.createElement('button'); more.type = 'button'; more.className = 'wk-dmore';
      more.textContent = t(`Afficher plus (${found.shown - found.results.length} de plus)`, `Show more (${found.shown - found.results.length} more)`);
      more.addEventListener('click', () => { dlimit += 30; renderDetails(input.value.slice(0, 120)); });
      dbox.append(more);
    }
  };
  const render = () => {
    if (!overlay || (overlay.hidden && !inline)) return;
    const query = input.value.slice(0, 120);
    results.replaceChildren();
    allLink.parentElement.hidden = true;
    if (!normalizeQuery(query)) { status.textContent = ''; dbox.replaceChildren(); dbox.hidden = true; return; }
    if (!index) { status.textContent = t('Chargement…', 'Loading…'); load().then(render); return; }
    if (index.failed) { status.textContent = t('Recherche indisponible pour le moment. Appuyez sur Entrée pour chercher dans le registre.', 'Search is unavailable right now. Press Enter to search the registry.'); return; }
    const {total, results: found, terms} = searchPrepared(prepared, {query, lang, limit: 8});
    pageTotal = total;
    status.textContent = total ? t(`${total} résultat${total > 1 ? 's' : ''}`, `${total} result${total > 1 ? 's' : ''}`) : t('Aucun résultat publié pour cette recherche.', 'No published result for this search.');
    for (const entry of found) {
      const path = localized(entry.url, lang);
      if (!/^(fr|en)\/[a-z0-9-]+\/[a-z0-9-]+\/$/.test(path)) continue;
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = new URL(path + (preview ? 'index.html' : ''), indexURL).href;
      link.className = 'wk-result';
      const kind = document.createElement('span'); kind.className = 'wk-result-cat'; kind.textContent = categoryName(entry.category);
      const title = document.createElement('strong'); highlight(title, entryTitle(entry, lang), terms);
      const text = document.createElement('span'); text.className = 'wk-result-text'; text.textContent = localized(entry.description, lang);
      link.append(kind, title, text);
      item.append(link);
      results.append(item);
    }
    if (total && !preview && !inline) {
      // "Tout le wiki" (/fr/wiki/, /en/wiki/) holds the full registry with filters; ?q= pre-fills its search.
      allLink.href = `${registry}?q=${encodeURIComponent(query)}#catalog-section`;
      allLink.parentElement.hidden = false;
    }
    renderDetails(query);
  };

  // v42c (t412u/t413u): on « Tout le wiki » (/fr/wiki/, /en/wiki/) the search is shown IN the page, not as an overlay, so
  // a reader who lands there (icon tapped before the script ran, old tab, no-JS form) can type and see the same results.
  const box = overlay?.querySelector('.wk-search-box');
  const inline = !!(overlay && box && registry && new URL(registry, location.href).pathname === location.pathname);
  if (inline) {
    const anchor = document.querySelector('.v2-index .v2-lede') ?? document.querySelector('main h1');
    if (anchor) { anchor.after(box); box.classList.add('wk-search-inline'); box.querySelector('.wk-search-close').hidden = true; overlay.hidden = true; }
  }
  const focusables = () => [...overlay.querySelectorAll('input, button, a[href]')].filter(node => node.offsetParent !== null || node === input);
  const openSearch = () => {
    if (!overlay) return;
    if (inline) { input.focus({preventScroll: true}); box.scrollIntoView({behavior: 'instant', block: 'start'}); load().then(render); return; }
    setDrawer(false); closePanels();
    lastFocus = document.activeElement;
    overlay.hidden = false;
    document.documentElement.classList.add('wk-search-open');
    opener.setAttribute('aria-expanded', 'true');
    input.focus();
    load().then(render);
  };
  const closeSearch = () => {
    if (!overlay || overlay.hidden || inline) return;
    overlay.hidden = true;
    document.documentElement.classList.remove('wk-search-open');
    opener.setAttribute('aria-expanded', 'false');
    (lastFocus && document.contains(lastFocus) ? lastFocus : opener).focus();
  };
  if (overlay) {
    opener.setAttribute('role', 'button');
    opener.setAttribute('aria-haspopup', 'dialog');
    opener.setAttribute('aria-expanded', 'false');
    opener.setAttribute('aria-controls', 'wk-search');
    opener.addEventListener('click', event => { event.preventDefault(); openSearch(); });
    opener.addEventListener('keydown', event => { if (event.key === ' ') { event.preventDefault(); openSearch(); } });
    overlay.querySelectorAll('[data-wk-search-close]').forEach(node => node.addEventListener('click', closeSearch));
    // v17: results while typing — immediate once the index is in memory, short debounce otherwise.
    input.addEventListener('input', () => { clearTimeout(timer); if (prepared) render(); else timer = setTimeout(render, 60); });
    // v17: fetch the index as soon as the reader shows intent (touch, hover, focus), before the overlay opens.
    for (const type of ['pointerdown', 'touchstart', 'mouseenter', 'focus']) opener.addEventListener(type, () => { load(); }, {once: true, passive: true});
    (inline ? box : overlay).addEventListener('keydown', event => {
      if (event.key === 'Escape') { if (inline) return; event.preventDefault(); closeSearch(); return; }
      const links = [...results.querySelectorAll('a'), ...dbox.querySelectorAll('a')];
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        if (!links.length) return;
        const at = links.indexOf(document.activeElement);
        const next = event.key === 'ArrowDown' ? (at + 1) % links.length : (at <= 0 ? -1 : at - 1);
        (next === -1 ? input : links[next]).focus();
        event.preventDefault();
        return;
      }
      if (event.key === 'Tab' && !inline) {
        const items = focusables();
        const first = items[0], last = items[items.length - 1];
        if (event.shiftKey && document.activeElement === first) { last.focus(); event.preventDefault(); }
        else if (!event.shiftKey && document.activeElement === last) { first.focus(); event.preventDefault(); }
      }
    });
    if (preview) overlay.querySelector('form').addEventListener('submit', event => event.preventDefault());
    // v42b: with JavaScript, Enter keeps the instant results (the registry page has no text filter).
    else box.querySelector('form').addEventListener('submit', event => { event.preventDefault(); render(); (results.querySelector('a') ?? dbox.querySelector('a'))?.focus(); });
    // v42b: the home search box and any other wiki search form open the same instant search with their words.
    document.querySelectorAll('form[role="search"]').forEach(form => {
      if (box.contains(form)) return;
      form.addEventListener('submit', event => {
        const words = String(new FormData(form).get('q') ?? '').slice(0, 120);
        event.preventDefault(); openSearch(); input.value = words; render();
      });
    });
    // v42b: "Tout le wiki" and the no-JS form fallback arrive with ?q= : reopen the instant search with those words.
    const asked = new URLSearchParams(location.search).get('q');
    if (asked && asked.trim()) { input.value = asked.slice(0, 120); openSearch(); }
    // v42b: a result inside the current page only changes the hash — close the search so the target shows.
    dbox.addEventListener('click', event => { if (event.target instanceof Element && event.target.closest('a')) closeSearch(); });
    input.placeholder = t('Un PNJ, un objet, une quête, une zone…', 'An NPC, an item, a quest, a zone…');
    const hint = document.getElementById('wk-search-hint');
    if (hint) hint.textContent = inline ? t('Tapez un mot : pages publiées et ce qu’elles contiennent (PNJ, objets, quêtes…).', 'Type a word: published pages and what they contain (NPCs, items, quests…).')
      : t('Pages publiées et ce qu’elles contiennent (PNJ, objets, quêtes…). Échap pour fermer.', 'Published pages and what they contain (NPCs, items, quests…). Esc to close.');
    // "/" opens the search from anywhere except text fields.
    document.addEventListener('keydown', event => {
      if (event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey || (!overlay.hidden && !inline)) return;
      const target = event.target;
      if (target instanceof HTMLElement && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return;
      event.preventDefault();
      openSearch();
    });
  }
}

/**
 * v39 (test UI) — tiroir « Catégories » sur téléphone/tablette, raccourci de recherche de l'accueil, section courante
 * surlignée (onglets + « Sur cette page »). Amélioration progressive : sans JavaScript, l'arbre reste en bas de page et
 * les onglets sont de simples ancres. Aucun script ni style en ligne (CSP script-src 'self'), aucune requête réseau.
 */
if (document.body?.classList.contains('v39')) {
  const root = document.documentElement;
  const header = document.querySelector('[data-wk-header]');
  const setHead = () => { if (header) root.style.setProperty('--v39-head', `${Math.round(header.getBoundingClientRect().height)}px`); };
  setHead(); window.addEventListener('resize', setHead, {passive: true});

  // ---- Tiroir des catégories ----
  const side = document.getElementById('v39-side');
  const toggle = document.querySelector('.v39-side-toggle');
  const closer = side?.querySelector('.v39-side-close');
  const backdrop = document.querySelector('.v39-backdrop');
  const drawer = window.matchMedia('(max-width: 1220px)');
  if (side && toggle && closer && backdrop) {
    const fr = (header?.dataset.lang ?? 'fr') !== 'en';
    toggle.hidden = false; closer.hidden = false;
    const isOpen = () => side.classList.contains('is-open');
    const setOpen = (open, refocus = true) => {
      toggle.setAttribute('aria-expanded', String(open));
      side.classList.toggle('is-open', open);
      backdrop.hidden = !open;
      root.classList.toggle('v39-side-open', open);
      if (open) {
        side.setAttribute('role', 'dialog'); side.setAttribute('aria-modal', 'true');
        const cur = side.querySelector('[aria-current="page"]');
        if (cur) side.scrollTop = Math.max(0, cur.offsetTop - side.clientHeight / 2);
        closer.focus({preventScroll: true});
      } else {
        side.removeAttribute('role'); side.removeAttribute('aria-modal');
        if (refocus) toggle.focus();
      }
    };
    closer.setAttribute('aria-label', fr ? 'Fermer les catégories' : 'Close categories');
    toggle.addEventListener('click', () => setOpen(true));
    closer.addEventListener('click', () => setOpen(false));
    backdrop.addEventListener('click', () => setOpen(false));
    side.addEventListener('keydown', event => {
      if (!isOpen()) return;
      if (event.key === 'Escape') { event.preventDefault(); setOpen(false); return; }
      if (event.key !== 'Tab') return;
      const items = [...side.querySelectorAll('a[href], button, summary')].filter(node => node.offsetParent !== null || node === closer);
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { last.focus(); event.preventDefault(); }
      else if (!event.shiftKey && document.activeElement === last) { first.focus(); event.preventDefault(); }
    });
    drawer.addEventListener?.('change', () => { if (!drawer.matches && isOpen()) setOpen(false, false); });
    // Bureau : la page courante visible dans l'arbre (colonne collante qui défile seule).
    // Bureau : faire défiler l'arbre (colonne collante) seulement si la page courante est sous le bas de la colonne.
    if (!drawer.matches) { const cur = side.querySelector('[aria-current="page"]'); if (cur && cur.offsetTop + cur.offsetHeight > side.clientHeight - 24) side.scrollTop = cur.offsetTop + cur.offsetHeight - side.clientHeight + 120; }
  }

  // ---- Recherche de l'accueil : ouvre la recherche instantanée de l'en-tête ----
  const opener = document.querySelector('[data-wk-search-open]');
  document.querySelectorAll('[data-v39-search]').forEach(link => link.addEventListener('click', event => {
    if (!opener || !document.getElementById('wk-search')) return;
    event.preventDefault(); opener.click();
  }));

  // ---- Section courante ----
  const links = [...document.querySelectorAll('.v39-tabs a[href^="#"], .v39-toc a[href^="#"]')];
  const targets = [...new Set(links.map(link => decodeURIComponent(link.hash.slice(1))))].map(id => document.getElementById(id)).filter(Boolean);
  if (targets.length && 'IntersectionObserver' in window) {
    const strip = document.querySelector('.v39-tabs ul');
    const visible = new Set();
    const mark = id => {
      for (const link of links) {
        const on = link.hash.slice(1) === id;
        link.classList.toggle('is-active', on);
        if (on) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
        if (on && strip && strip.contains(link)) strip.scrollLeft = Math.max(0, link.offsetLeft - strip.clientWidth / 3);
      }
    };
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) entry.isIntersecting ? visible.add(entry.target) : visible.delete(entry.target);
      const first = targets.find(node => visible.has(node));
      if (first) mark(first.id);
    }, {rootMargin: '-140px 0px -55% 0px'});
    targets.forEach(node => observer.observe(node));
  }
}
