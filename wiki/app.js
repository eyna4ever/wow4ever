import {entryPagePath, entryTitle, guideProgress, isDisplayableEntry, localized, normalizeLanguage, progressKey, readPersonalState, relatedEntries, safeSourceURL, savePersonalState, searchEntries, searchSuggestions, toggleValue} from './ui-core.mjs';

const instances = new WeakMap();

/** One controller serves the local HTML export and the Next.js integration. No network requests. */
export function initWiki(root = document) {
  const scope = root.querySelector?.('#wiki-app') ?? (root.id === 'wiki-app' ? root : null);
  if (!scope) return () => {};
  instances.get(scope)?.();
  const doc = scope.ownerDocument;
  const view = doc.defaultView;
  const $ = id => scope.querySelector(`#${id}`) ?? doc.getElementById(id);
  const controller = new (view?.AbortController ?? AbortController)();
  const listen = (node, event, callback) => node?.addEventListener(event, callback, {signal: controller.signal});
  let storage;
  try { storage = view?.localStorage; } catch { storage = undefined; }
  const personal = readPersonalState(storage);
  let sourceData = {categories: [], entries: []};
  try {
    const value = JSON.parse($('wiki-data')?.textContent ?? '{}');
    if (value && typeof value === 'object') sourceData = value;
  } catch { /* A broken embedded catalog produces an empty archive, never invented content. */ }
  const categories = (Array.isArray(sourceData.categories) ? sourceData.categories : []).filter(item => Array.isArray(item) && item.length === 3 && item.every(value => typeof value === 'string') && /^[a-z][a-z0-9-]*$/.test(item[0]));
  const categoryIDs = new Set(categories.map(item => item[0]));
  const entries = (Array.isArray(sourceData.entries) ? sourceData.entries : []).filter(item => isDisplayableEntry(item) && categoryIDs.has(item.category));
  const explicitLanguage = [root.dataset?.language, scope.dataset?.language].find(lang => lang === 'fr' || lang === 'en');
  const routeLanguage = view?.location.pathname.match(/^\/(fr|en)(?:\/|$)/)?.[1];
  const state = {lang: normalizeLanguage(explicitLanguage ?? routeLanguage ?? personal.lang ?? doc.documentElement.lang), query: '', category: '', favoritesOnly: false, favorites: personal.favorites, progress: personal.progress, activeId: null, tab: 'entry', feature: null};
  const pagesAvailable = view?.location && /^https?:$/.test(view.location.protocol);
  const rootPrefix = routeLanguage ? '../' : './';
  const categorySlugs = {classes: ['classes', 'classes'], races: ['races', 'races'], zones: ['zones', 'zones'], instances: ['donjons-raids', 'dungeons-raids'], professions: ['metiers', 'professions'], items: ['objets', 'items'], quests: ['quetes', 'quests'], pvp: ['jcj', 'pvp'], creatures: ['creatures', 'creatures'], guides: ['guides', 'guides'], news: ['actualites', 'news'], glossary: ['glossaire', 'glossary']};
  const pageLink = (path, label) => { const link = element('a', label, 'page-link'); link.href = rootPrefix + path; return link; };
  let storageFailed = !storage;
  let dialogOpener = null;
  const t = (fr, en) => state.lang === 'en' ? en : fr;
  const categoryTitle = id => categories.find(item => item[0] === id)?.[state.lang === 'en' ? 2 : 1] ?? '';
  const element = (tag, text = '', className = '') => {
    const node = doc.createElement(tag);
    if (text !== '') node.textContent = String(text);
    if (className) node.className = className;
    return node;
  };
  const button = (label, action, value = '') => {
    const node = element('button', label);
    node.type = 'button';
    node.dataset.action = action;
    if (value) node.dataset.value = value;
    return node;
  };
  const text = (id, value) => { if ($(id)) $(id).textContent = value; };
  const show = (id, visible) => { if ($(id)) $(id).hidden = !visible; };
  const persist = () => {
    storageFailed = !savePersonalState(storage, state);
    show('storage-notice', storageFailed);
  };
  const moveTo = node => {
    node?.scrollIntoView?.({behavior: view?.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start'});
    node?.focus?.({preventScroll: true});
  };
  const updateMenuLabel = () => {
    const menu = $('menu-toggle');
    menu?.setAttribute('aria-label', menu.getAttribute('aria-expanded') === 'true' ? t('Fermer le menu', 'Close menu') : t('Ouvrir le menu', 'Open menu'));
  };
  const closeMenu = () => {
    $('menu-toggle')?.setAttribute('aria-expanded', 'false');
    $('main-nav')?.classList.remove('is-open');
    updateMenuLabel();
  };
  const closeEntry = () => { state.activeId = null; show('entry-panel', false); };
  const closeFeature = () => { state.feature = null; show('feature-panel', false); };
  const openDialog = (id, opener) => {
    const dialog = $(id);
    if (!dialog) return;
    dialogOpener = opener ?? doc.activeElement;
    if (typeof dialog.showModal === 'function') { if (!dialog.open) dialog.showModal(); }
    else { dialog.setAttribute('open', ''); dialog.setAttribute('role', 'dialog'); dialog.setAttribute('aria-modal', 'true'); }
    dialog.querySelector('button')?.focus();
  };
  const closeDialog = id => {
    const dialog = $(id);
    if (typeof dialog?.close === 'function') dialog.close();
    else dialog?.removeAttribute('open');
    dialogOpener?.focus?.();
  };

  function applyTranslations() {
    doc.documentElement.lang = state.lang;
    scope.querySelectorAll('[data-fr][data-en]').forEach(node => { node.textContent = node.dataset[state.lang]; });
    scope.querySelectorAll('[data-fr-aria][data-en-aria]').forEach(node => { node.setAttribute('aria-label', node.getAttribute(`data-${state.lang}-aria`)); });
    scope.querySelectorAll('[data-href-fr][data-href-en]').forEach(node => { node.setAttribute('href', node.getAttribute(`data-href-${state.lang}`)); });
    scope.querySelectorAll('[data-alt-fr][data-alt-en]').forEach(node => { node.setAttribute('alt', node.getAttribute(`data-alt-${state.lang}`)); });
    updateMenuLabel();
    const language = $('language-toggle');
    if (language) {
      const french = element('span', 'FR');
      french.lang = 'fr';
      french.dataset.active = String(state.lang === 'fr');
      const english = element('span', 'EN');
      english.lang = 'en';
      english.dataset.active = String(state.lang === 'en');
      const divider=element('span',' / ','language-divider');
      language.replaceChildren(french,divider,english);
      language.lang = state.lang;
      language.setAttribute('aria-label', t('Switch to English', 'Passer en français'));
    }
    if ($('search-input')) {
      $('search-input').placeholder = t('Rechercher une classe, une zone, un guide…', 'Search for a class, a zone, a guide…');
      $('search-input').setAttribute('aria-label', t('Rechercher dans les fiches validées', 'Search reviewed entries'));
    }
    text('storage-notice', t('Le stockage est indisponible : favoris et progression restent dans cette session.', 'Storage is unavailable: favorites and progress remain in this session.'));
    show('storage-notice', storageFailed);
    scope.querySelectorAll('[data-count-for]').forEach(node => {
      const count = entries.filter(entry => entry.category === node.dataset.countFor).length;
      node.textContent = `${count} ${t(count === 1 ? 'fiche validée' : 'fiches validées', count === 1 ? 'reviewed entry' : 'reviewed entries')}`;
    });
    scope.querySelectorAll('[data-published-count]').forEach(node => { node.textContent = String(entries.length); });
    scope.querySelectorAll('[data-category]').forEach(node => node.setAttribute('aria-pressed', String(node.dataset.category === state.category)));
    scope.querySelectorAll('[data-view]').forEach(node => {
      const selected = state.feature ? node.dataset.view === state.feature : node.dataset.view === (state.category === 'guides' ? 'guides' : 'encyclopedia');
      if (selected) node.setAttribute('aria-current', 'page'); else node.removeAttribute('aria-current');
    });
    if ($('favorites-only')) $('favorites-only').checked = state.favoritesOnly;
    text('category-label', categoryTitle(state.category) || t('Toutes les rubriques', 'All categories'));
    text('account-title', t('Votre espace personnel', 'Your personal space'));
    text('account-description', t('Les comptes et les contributions ne sont pas connectés à un service d’authentification. Vous pouvez déjà conserver vos favoris et votre progression sur cet appareil, sans créer de compte.', 'Accounts and contributions are not connected to an authentication service. You can already keep favorites and progress on this device without an account.'));
  }

  function resultCard(entry) {
    const card = element('article', '', 'result-card');
    card.dataset.entryId = entry.id;
    card.append(element('p', categoryTitle(entry.category), 'eyebrow'));
    const heading = element('h3');
    heading.append(button(entryTitle(entry, state.lang), 'open-entry', entry.id));
    card.append(heading, element('p', localized(entry.description, state.lang)), element('small', `${t('Version', 'Version')} ${entry.version} · ${entry.gameVersion ?? ''}`));
    const path = pagesAvailable ? entryPagePath(entry, state.lang) : null;
    if (path) card.append(pageLink(path, `${entry.hasArticle ? t('Lire l’article', 'Read the article') : t('Ouvrir la page', 'Open the page')} →`));
    const favorite = button(`${state.favorites.includes(entry.id) ? '★' : '☆'} ${t('Favori', 'Favorite')}`, 'favorite', entry.id);
    favorite.setAttribute('aria-pressed', String(state.favorites.includes(entry.id)));
    favorite.setAttribute('aria-label', `${state.favorites.includes(entry.id) ? t('Retirer des favoris', 'Remove from favorites') : t('Ajouter aux favoris', 'Add to favorites')} : ${entryTitle(entry, state.lang)}`);
    card.append(favorite);
    return card;
  }

  function renderSuggestions() {
    const list = $('search-suggestions');
    if (!list) return;
    list.replaceChildren(...searchSuggestions(entries, state).map(entry => {
      const option = element('option');
      option.value = entryTitle(entry, state.lang);
      return option;
    }));
  }

  function renderResults() {
    const results = searchEntries(entries, state);
    text('result-summary', `${results.length} ${t(results.length === 1 ? 'fiche validée' : 'fiches validées', results.length === 1 ? 'reviewed entry' : 'reviewed entries')}${state.category ? ` · ${categoryTitle(state.category)}` : ''}`);
    $('results')?.replaceChildren(...results.map(resultCard));
    let categoryLink = $('category-page-link');
    if (!categoryLink && $('result-summary')) { categoryLink = element('p', '', 'category-page-link'); categoryLink.id = 'category-page-link'; $('result-summary').after(categoryLink); }
    if (categoryLink) {
      const slug = categorySlugs[state.category]?.[state.lang === 'en' ? 1 : 0];
      categoryLink.replaceChildren(...(pagesAvailable && slug ? [pageLink(`${state.lang}/${slug}/`, `${t('Ouvrir la page de la rubrique', 'Open the category page')} : ${categoryTitle(state.category)} →`)] : []));
      categoryLink.hidden = !(pagesAvailable && slug);
    }
    show('empty-state', results.length === 0);
    if (!results.length) {
      if (state.query.trim()) {
        text('empty-title', t(`Aucune fiche validée pour « ${state.query.trim()} »`, `No reviewed entry for “${state.query.trim()}”`));
        text('empty-description', t('Essayez un autre terme ou réinitialisez les filtres. Les fiches sans sources et validation humaine ne figurent pas dans les résultats.', 'Try another term or reset the filters. Entries without sources and human approval do not appear in the results.'));
      } else if (state.favoritesOnly) {
        text('empty-title', t('Aucun favori dans cette sélection', 'No favorites in this selection'));
        text('empty-description', t('Lorsqu’une fiche sera publiée, utilisez son étoile pour la retrouver ici. Vos favoris restent enregistrés sur cet appareil.', 'When an entry is published, use its star to find it here. Your favorites are saved on this device.'));
      } else if (state.category === 'guides') {
        text('empty-title', t('Les premiers guides attendent leur validation', 'The first guides await review'));
        text('empty-description', t('Les guides validés proposeront des étapes à cocher. La progression sera enregistrée sur cet appareil pour chaque version du guide.', 'Reviewed guides will provide checkable steps. Progress will be saved on this device for each guide revision.'));
      } else {
        text('empty-title', state.category ? t('Cette rubrique attend ses premières sources', 'This category awaits its first sources') : t('Les archives se préparent', 'The archives are taking shape'));
        text('empty-description', t('Les 12 rubriques sont ouvertes à l’exploration. Aucune donnée de jeu n’est publiée avant identification de la version, vérification des sources et validation humaine.', 'All 12 categories are ready to explore. Game data is published only after version identification, source verification and human approval.'));
      }
    }
    renderSuggestions();
  }

  function renderEntry({focus = false} = {}) {
    const panel = $('entry-panel');
    const entry = entries.find(item => item.id === state.activeId);
    if (!panel || !entry) { show('entry-panel', false); return; }
    panel.replaceChildren();
    panel.classList.add('entry-detail');
    const header = element('div', '', 'section-heading');
    const heading = element('h2', entryTitle(entry, state.lang));
    heading.id = 'entry-heading';
    panel.setAttribute('aria-labelledby', heading.id);
    header.append(heading, button(t('Fermer la fiche', 'Close entry'), 'close-entry'));
    panel.append(header, element('p', `${categoryTitle(entry.category)} · ${t('Version du jeu', 'Game version')} : ${entry.gameVersion ?? ''} · ${t('Révision', 'Revision')} ${entry.version}`, 'panel-note'));
    const tabs = element('div', '', 'entry-tabs');
    tabs.setAttribute('role', 'group');
    tabs.setAttribute('aria-label', t('Sections de la fiche', 'Entry sections'));
    for (const [id, fr, en] of [['entry', 'Fiche', 'Entry'], ['sources', 'Sources', 'Sources'], ['history', 'Historique', 'History']]) {
      const tab = button(t(fr, en), 'entry-tab', id);
      tab.setAttribute('aria-pressed', String(state.tab === id));
      tab.setAttribute('aria-controls', 'entry-content');
      tabs.append(tab);
    }
    panel.append(tabs);
    const entryPath = pagesAvailable ? entryPagePath(entry, state.lang) : null;
    if (entryPath) panel.append(pageLink(entryPath, `${t('Page permanente de cette fiche', 'Permanent page for this entry')} →`));
    const content = element('div');
    content.id = 'entry-content';
    if (state.tab === 'sources') {
      content.append(element('h3', t('Références et droits', 'References and rights')));
      const list = element('ul', '', 'source-list');
      for (const source of entry.sources) {
        const item = element('li');
        const link = element('a', source.title || source.url);
        link.href = safeSourceURL(source.url);
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        item.append(link, element('p', `${t('Consultée le', 'Accessed')} ${source.accessedAt} · ${source.license}${source.gameVersion ? ` · ${source.gameVersion}` : ''}`));
        list.append(item);
      }
      content.append(list);
    } else if (state.tab === 'history') {
      content.append(element('h3', t('Historique des versions', 'Revision history')));
      const list = element('ol', '', 'history-list');
      for (const change of Array.isArray(entry.history) ? entry.history : []) list.append(element('li', `${change.at ?? ''}${change.version ? ` · ${t('Révision', 'Revision')} ${change.version}` : ''} · ${change.note ?? ''}`));
      content.append(list);
    } else {
      content.append(element('p', localized(entry.description, state.lang)));
      const favorite = button(`${state.favorites.includes(entry.id) ? '★' : '☆'} ${t('Favori', 'Favorite')}`, 'favorite', entry.id);
      favorite.setAttribute('aria-pressed', String(state.favorites.includes(entry.id)));
      content.append(favorite);
      if (Array.isArray(entry.steps) && entry.steps.length) {
        const progress = guideProgress(entry, state.progress);
        content.append(element('h3', t('Votre progression', 'Your progress')));
        const bar = element('progress');
        bar.max = progress.total;
        bar.value = progress.done;
        bar.setAttribute('aria-label', t('Progression du guide', 'Guide progress'));
        const summary = element('p', `${progress.done} / ${progress.total} · ${progress.percent} %`, 'progress-summary');
        summary.setAttribute('aria-live', 'polite');
        content.append(bar, summary);
        const steps = element('ol', '', 'guide-steps');
        entry.steps.forEach((step, index) => {
          const item = element('li');
          const label = element('label');
          const checkbox = element('input');
          checkbox.type = 'checkbox';
          checkbox.checked = state.progress.includes(progressKey(entry, index));
          checkbox.dataset.step = String(index);
          checkbox.dataset.entry = entry.id;
          label.append(checkbox, doc.createTextNode(` ${localized(step, state.lang)}`));
          item.append(label);
          steps.append(item);
        });
        content.append(steps, element('small', t('Progression conservée sur cet appareil pour cette révision du guide.', 'Progress is saved on this device for this guide revision.')));
      }
      const related = relatedEntries(entry, entries);
      if (related.length) {
        content.append(element('h3', t('Pour poursuivre votre exploration', 'Continue exploring')));
        const links = element('div', '', 'related-entries');
        related.forEach(item => links.append(button(entryTitle(item, state.lang), 'open-entry', item.id)));
        content.append(links);
      }
    }
    panel.append(content);
    panel.hidden = false;
    if (focus) moveTo(panel);
  }

  function renderFeature({focus = false} = {}) {
    const panel = $('feature-panel');
    const body = $('feature-body');
    if (!panel || !body || !state.feature) { show('feature-panel', false); return; }
    body.replaceChildren();
    const note = message => body.append(element('p', message, 'panel-note'));
    if (state.feature === 'maps') {
      text('feature-title', t('Cartes et exploration', 'Maps and exploration'));
      note(t('Aucune carte ni aucun marqueur validé n’est disponible.', 'No reviewed map or marker is available.'));
      body.append(element('p', t('Les points d’intérêt seront ajoutés après confirmation de la version du jeu, de leurs coordonnées et des droits de la carte. Les illustrations de l’accueil ne sont pas des cartes de jeu.', 'Points of interest will be added after confirming the game version, coordinates and map rights. Homepage illustrations are not game maps.')));
      body.append(button(t('Explorer la rubrique Zones', 'Explore the Zones category'), 'category', 'zones'));
    } else if (state.feature === 'community') {
      text('feature-title', t('La communauté des archives', 'The archive community'));
      note(t('Les contributions publiques et la réputation attendent la connexion du service de comptes et de modération.', 'Public contributions and reputation await a connected account and moderation service.'));
      body.append(element('p', t('Préparez une référence officielle, la version concernée et une synthèse originale en français et en anglais. Chaque fiche suivra une revue humaine avant publication.', 'Prepare an official reference, the relevant version and an original summary in French and English. Every entry will undergo human review before publication.')));
      body.append(button(t('État des comptes', 'Account status'), 'account'));
    } else if (state.feature === 'admin') {
      text('feature-title', t('Atelier documentaire', 'Documentary workshop'));
      note(t('Console publique en lecture seule. Aucun compte administrateur ni service de publication n’est connecté à cette interface.', 'Public read-only console. No administrator account or publishing service is connected to this interface.'));
      const table = element('table', '', 'admin-table');
      const caption = element('caption', t('État du catalogue public', 'Public catalog status'));
      table.append(caption);
      const tbody = element('tbody');
      for (const [label, value] of [[t('Fiches publiées et validées', 'Published reviewed entries'), entries.length], [t('Rubriques', 'Categories'), categories.length], [t('Références publiques', 'Public references'), new Set(entries.flatMap(item => item.sources.map(source => source.url))).size], [t('Brouillons et revue interne', 'Drafts and internal review'), t('Accès restreint, service à connecter', 'Restricted access, service required')]]) {
        const row = element('tr');
        const th = element('th', label);
        th.scope = 'row';
        row.append(th, element('td', value));
        tbody.append(row);
      }
      table.append(tbody);
      body.append(table, element('p', t('Sources → extraction autorisée → normalisation → déduplication → vérification → traduction → prévisualisation → validation humaine → publication.', 'Sources → authorized extraction → normalization → deduplication → verification → translation → preview → human approval → publication.')));
    }
    panel.hidden = false;
    if (focus) moveTo(panel);
  }

  function render() {
    applyTranslations();
    renderResults();
    renderEntry();
    renderFeature();
  }

  function selectCategory(id, {toggle = true} = {}) {
    if (id && !categoryIDs.has(id)) return;
    closeEntry();
    closeFeature();
    state.category = toggle && state.category === id ? '' : id;
    render();
    moveTo($('catalog-section') ?? $('result-summary'));
  }

  function navigate(name) {
    closeMenu();
    closeEntry();
    if (name === 'guides') {
      state.query = '';
      state.favoritesOnly = false;
      if ($('search-input')) $('search-input').value = '';
      selectCategory('guides', {toggle: false});
    } else if (['maps', 'community', 'admin'].includes(name)) {
      state.feature = name;
      render();
      renderFeature({focus: true});
    } else {
      closeFeature();
      state.category = '';
      render();
      moveTo($('archives') ?? $('result-summary'));
    }
  }

  function showInfo(name, opener) {
    const content = {
      sources: [t('Des sources avant des certitudes', 'Sources before certainty'), t('Chaque fiche publiée doit identifier sa version du jeu, citer des références consultables avec leur date de consultation et leur licence, puis recevoir une validation humaine. Les contenus non vérifiés restent en brouillon.', 'Each published entry must identify its game version, cite accessible references with access dates and licenses, and receive human approval. Unverified content stays in draft.')],
      contributions: [t('Contribuer aux archives', 'Contribute to the archives'), t('Le service de contribution est en préparation. Une future proposition devra fournir des sources, sa version de jeu et des textes originaux FR/EN. La publication et la réputation exigeront un compte et une modération configurés.', 'The contribution service is being prepared. Future submissions must include sources, a game version and original FR/EN text. Publication and reputation require configured accounts and moderation.')],
      legal: [t('Informations et droits', 'Information and rights'), t('WoW Forever Wiki est un projet indépendant de WORLD OF HACKCRAFT, ForgeCraft et RaveForge, sans affiliation à Blizzard Entertainment. Les noms cités appartiennent à leurs titulaires respectifs. Les illustrations d’ambiance ne documentent aucune zone ni mécanique du jeu. Favoris, langue et progression sont stockés localement, sans compte.', 'WoW Forever Wiki is independent of WORLD OF HACKCRAFT, ForgeCraft and RaveForge, with no affiliation to Blizzard Entertainment. Mentioned names belong to their respective owners. Atmospheric illustrations do not document game zones or mechanics. Favorites, language and progress are stored locally without an account.')]
    }[name];
    if (!content) return;
    text('info-title', content[0]);
    text('info-body', content[1]);
    if ($('info-dialog')) $('info-dialog').dataset.info = name;
    openDialog('info-dialog', opener);
  }

  listen(scope, 'click', event => {
    const target = event.target.closest?.('button, a, [data-info]');
    if (!target || !scope.contains(target)) return;
    if (target.dataset.view) { event.preventDefault(); navigate(target.dataset.view); return; }
    if (target.dataset.category) { event.preventDefault(); closeMenu(); selectCategory(target.dataset.category); return; }
    if (target.dataset.info) { event.preventDefault(); showInfo(target.dataset.info, target); return; }
    const action = target.dataset.action;
    if (!action) return;
    if (action === 'open-entry') {
      state.activeId = target.dataset.value;
      state.tab = 'entry';
      renderEntry({focus: true});
    } else if (action === 'close-entry') {
      closeEntry();
      moveTo($('result-summary'));
    } else if (action === 'entry-tab') {
      state.tab = target.dataset.value;
      const nextTab = state.tab;
      renderEntry();
      $('entry-panel')?.querySelector(`[data-value="${nextTab}"]`)?.focus();
    } else if (action === 'favorite') {
      const entry = entries.find(item => item.id === target.dataset.value);
      if (!entry) return;
      const fromEntryPanel = Boolean($('entry-panel')?.contains(target));
      state.favorites = toggleValue(state.favorites, entry.id);
      persist();
      render();
      const replacement = (fromEntryPanel ? $('entry-panel') : $('results'))?.querySelector(`[data-action="favorite"][data-value="${entry.id}"]`);
      replacement?.focus?.({preventScroll: true});
    } else if (action === 'category') selectCategory(target.dataset.value, {toggle: false});
    else if (action === 'account') openDialog('account-dialog', target);
  });
  listen($('menu-toggle'), 'click', () => {
    const expanded = $('menu-toggle').getAttribute('aria-expanded') !== 'true';
    $('menu-toggle').setAttribute('aria-expanded', String(expanded));
    $('main-nav')?.classList.toggle('is-open', expanded);
    updateMenuLabel();
  });
  listen(scope, 'keydown', event => { if (event.key === 'Escape') closeMenu(); });
  listen($('language-toggle'), 'click', () => {
    state.lang = state.lang === 'fr' ? 'en' : 'fr';
    persist();
    render();
    const dialog = $('info-dialog');
    if (dialog?.open && dialog.dataset.info) showInfo(dialog.dataset.info, dialogOpener);
    // Preserve the FR/EN route on the local app without loading an unavailable remote service.
    if (routeLanguage && view?.location.protocol !== 'file:') {
      try { view.history.replaceState(null, '', view.location.pathname.replace(/^\/(fr|en)(?=\/|$)/, `/${state.lang}`) + view.location.search + view.location.hash); } catch { /* Sandboxed previews may disallow history changes. */ }
    }
  });
  listen($('search-input'), 'input', event => {
    state.query = event.target.value;
    closeEntry();
    closeFeature();
    applyTranslations();
    renderResults();
  });
  listen($('search-form'), 'submit', event => {
    event.preventDefault();
    state.query = $('search-input')?.value ?? '';
    closeEntry();
    closeFeature();
    render();
    moveTo($('catalog-section') ?? $('result-summary'));
  });
  listen($('favorites-only'), 'change', event => {
    state.favoritesOnly = event.target.checked;
    closeEntry();
    closeFeature();
    render();
  });
  listen($('reset-filters'), 'click', () => {
    state.query = '';
    state.category = '';
    state.favoritesOnly = false;
    if ($('search-input')) $('search-input').value = '';
    closeEntry();
    closeFeature();
    render();
  });
  listen($('entry-panel'), 'change', event => {
    const input = event.target;
    if (input.dataset.step === undefined) return;
    const entry = entries.find(item => item.id === input.dataset.entry);
    const index = Number(input.dataset.step);
    if (!entry || !Array.isArray(entry.steps) || !entry.steps[index]) return;
    const key = progressKey(entry, index);
    state.progress = input.checked ? [...new Set([...state.progress, key])] : state.progress.filter(item => item !== key);
    persist();
    const progress = guideProgress(entry, state.progress);
    const bar = $('entry-panel').querySelector('progress');
    if (bar) bar.value = progress.done;
    const summary = $('entry-panel').querySelector('.progress-summary');
    if (summary) summary.textContent = `${progress.done} / ${progress.total} · ${progress.percent} %`;
  });
  listen($('feature-close'), 'click', () => { closeFeature(); render(); moveTo($('archives') ?? $('result-summary')); });
  listen($('account-open'), 'click', event => openDialog('account-dialog', event.currentTarget));
  listen($('account-close'), 'click', () => closeDialog('account-dialog'));
  listen($('info-close'), 'click', () => closeDialog('info-dialog'));
  for (const id of ['account-dialog', 'info-dialog']) {
    listen($(id), 'click', event => { if (event.target === $(id)) closeDialog(id); });
    listen($(id), 'close', () => dialogOpener?.focus?.());
  }
  try {
    const params = new URLSearchParams(view?.location.search ?? '');
    const query = (params.get('q') ?? '').slice(0, 120);
    const category = params.get('cat') ?? '';
    if (query) { state.query = query; if ($('search-input')) $('search-input').value = query; }
    if (categoryIDs.has(category)) state.category = category;
  } catch { /* Ignore malformed query strings. */ }
  const initialView=view?.location.hash;
  if(initialView==='#workshop')state.feature='admin';
  else if(initialView==='#maps')state.feature='maps';
  else if(initialView==='#community')state.feature='community';
  render();
  const cleanup = () => { controller.abort(); instances.delete(scope); };
  instances.set(scope, cleanup);
  return cleanup;
}

if (typeof document !== 'undefined') {
  globalThis.WowForeverWiki = {initWiki};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => initWiki(), {once: true});
  else initWiki();
}
