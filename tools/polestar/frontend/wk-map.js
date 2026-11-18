// Wowkipedia : carte interactive de zone. Module sans dépendance, compatible CSP (script-src 'self', style-src 'self') :
// les positions passent par le CSSOM (element.style), jamais par un attribut style dans le HTML.
const T = {
  fr: { roles: { giver: 'Donne une quête', ender: 'Reçoit une quête', target: 'Cible de quête', dropper: 'Porte un objet de quête', holder: 'Contient un objet de quête' },
        pos: 'position', given: 'Quêtes données', ended: 'Quêtes à rendre', here: n => n > 1 ? `${n} repères ici` : '1 repère', more: n => `+ ${n} autres repères proches`,
        unconfirmed: 'Donnée communautaire, à confirmer en jeu.', close: 'Fermer', fail: 'La carte n’a pas pu être chargée. La liste des repères reste disponible ci-dessous.',
        quests: n => n > 1 ? `${n} quêtes` : `${n} quête`, marker: 'Repère' },
  en: { roles: { giver: 'Gives a quest', ender: 'Takes a quest', target: 'Quest target', dropper: 'Carries a quest item', holder: 'Holds a quest item' },
        pos: 'position', given: 'Quests given', ended: 'Quests to turn in', here: n => n > 1 ? `${n} markers here` : '1 marker', more: n => `+ ${n} more markers nearby`,
        unconfirmed: 'Community data, to be confirmed in game.', close: 'Close', fail: 'The map could not be loaded. The list of markers is still available below.',
        quests: n => n > 1 ? `${n} quests` : `${n} quest`, marker: 'Marker' },
};
const ORDER = ['giver', 'ender', 'target', 'dropper', 'holder'];
const NEAR = 2.5;      // % of the map: markers this close are listed together (towns are dense)
const MAX_LIST = 8;    // compact card: at most this many entries, nearest first

function el(tag, attrs = {}, text) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text != null) e.textContent = text;
  return e;
}
function mainRole(roles) {
  for (const r of ORDER) if (roles.includes(r)) return r === 'holder' ? 'dropper' : r;
  return 'target';
}

async function setup(box) {
  const t = T[box.getAttribute('data-lang')] || T.fr;
  const layer = box.querySelector('.wk-map-pins');
  const card = box.querySelector('.wk-map-card');
  let data;
  try {
    const res = await fetch(box.getAttribute('data-map'), { credentials: 'same-origin' });
    if (!res.ok) throw new Error(res.status);
    data = await res.json();
  } catch (e) {
    card.hidden = false;
    card.textContent = t.fail;
    return;
  }
  const pins = [];
  for (const p of data.pins) {
    const role = mainRole(p.r);
    const b = el('button', { type: 'button', class: 'wk-pin', 'data-role': role, 'aria-pressed': 'false',
      'aria-label': `${p.n || t.marker} (${t.roles[role]}), ${t.pos} ${p.x}, ${p.y}` }, role === 'giver' ? '!' : role === 'ender' ? '?' : '');
    b.style.left = p.x + '%';
    b.style.top = p.y + '%';
    b.addEventListener('click', () => show(p, b));
    layer.appendChild(b);
    pins.push({ p, b, role });
  }
  function entry(p, open) {
    const q = data.quests[`${p.k}:${p.id}`] || {};
    const n = new Set([...(q.g || []), ...(q.e || [])]).size;
    const d = el('details');
    if (open) d.open = true;
    const s = el('summary', {}, p.n || t.marker);
    s.appendChild(el('small', {}, `${p.r.map(r => t.roles[r] || r).join(' · ')}${n ? ' — ' + t.quests(n) : ''}`));
    d.appendChild(s);
    d.appendChild(el('p', {}, `${t.pos} ${p.x}, ${p.y}`));
    for (const [key, label] of [['g', t.given], ['e', t.ended]]) {
      if (!q[key] || !q[key].length) continue;
      d.appendChild(el('p', {}, `${label} : ${[...new Set(q[key])].join(' · ')}`));
    }
    return d;
  }
  function show(p, b) {
    for (const x of pins) x.b.setAttribute('aria-pressed', x.b === b ? 'true' : 'false');
    const near = [];
    const seen = new Set([`${p.k}:${p.id}`]);
    for (const x of pins) {
      const key = `${x.p.k}:${x.p.id}`;
      const dist = Math.hypot(x.p.x - p.x, x.p.y - p.y);
      if (x.b.hidden || seen.has(key) || dist > NEAR) continue;
      seen.add(key);
      near.push([dist, x.p]);
    }
    near.sort((a, b2) => a[0] - b2[0]);
    card.replaceChildren();
    const head = el('div', { class: 'wk-card-head' });
    head.appendChild(el('strong', {}, t.here(near.length + 1)));
    const close = el('button', { type: 'button' }, t.close);
    close.addEventListener('click', () => { card.hidden = true; b.setAttribute('aria-pressed', 'false'); b.focus(); });
    head.appendChild(close);
    card.appendChild(head);
    card.appendChild(entry(p, true));
    for (const [, x] of near.slice(0, MAX_LIST - 1)) card.appendChild(entry(x, false));
    if (near.length > MAX_LIST - 1) card.appendChild(el('p', {}, t.more(near.length - (MAX_LIST - 1))));
    card.appendChild(el('p', { class: 'wk-map-credit' }, t.unconfirmed));
    card.hidden = false;
    card.scrollTop = 0;
  }
  function filter() {
    const on = new Set([...box.querySelectorAll('.wk-map-filters input:checked')].map(i => i.getAttribute('data-role')));
    for (const x of pins) x.b.hidden = !on.has(x.role);
  }
  for (const i of box.querySelectorAll('.wk-map-filters input')) i.addEventListener('change', filter);
  box.addEventListener('keydown', e => { if (e.key === 'Escape' && !card.hidden) card.hidden = true; });
  filter();
}

for (const box of document.querySelectorAll('.wk-map[data-map]')) setup(box);
