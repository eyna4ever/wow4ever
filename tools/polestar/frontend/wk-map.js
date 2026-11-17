// Wowkipedia : carte interactive de zone. Module sans dépendance, compatible CSP (script-src 'self', style-src 'self') :
// les positions passent par le CSSOM (element.style), jamais par un attribut style dans le HTML.
const ROLE_FR = { giver: 'Donne une quête', ender: 'Reçoit une quête', target: 'Cible de quête', dropper: 'Porte un objet de quête', holder: 'Contient un objet de quête' };
const ORDER = ['giver', 'ender', 'target', 'dropper', 'holder'];

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
  const url = box.getAttribute('data-map');
  const layer = box.querySelector('.wk-map-pins');
  const card = box.querySelector('.wk-map-card');
  let data;
  try {
    const res = await fetch(url, { credentials: 'same-origin' });
    if (!res.ok) throw new Error(res.status);
    data = await res.json();
  } catch (e) {
    card.hidden = false;
    card.textContent = 'La carte n’a pas pu être chargée. La liste des repères reste disponible ci-dessous.';
    return;
  }
  const pins = [];
  for (const p of data.pins) {
    const role = mainRole(p.r);
    const b = el('button', { type: 'button', class: 'wk-pin', 'data-role': role, 'aria-pressed': 'false',
      'aria-label': `${p.n || 'Repère'} (${ROLE_FR[role]}), position ${p.x}, ${p.y}` }, role === 'giver' ? '!' : role === 'ender' ? '?' : '');
    b.style.left = p.x + '%';
    b.style.top = p.y + '%';
    b.addEventListener('click', () => show(p, b));
    layer.appendChild(b);
    pins.push({ p, b, role });
  }
  // Towns are dense: a tap lists every visible marker within NEAR % of the tapped one.
  const NEAR = 2.5;
  function entry(p) {
    const frag = document.createDocumentFragment();
    frag.appendChild(el('h3', {}, p.n || 'Repère'));
    frag.appendChild(el('p', {}, p.r.map(r => ROLE_FR[r] || r).join(' · ') + ` — position ${p.x}, ${p.y}`));
    const q = data.quests[`${p.k}:${p.id}`] || {};
    for (const [key, label] of [['g', 'Quêtes données'], ['e', 'Quêtes à rendre']]) {
      if (!q[key] || !q[key].length) continue;
      frag.appendChild(el('p', {}, label + ' :'));
      const ul = el('ul');
      for (const t of q[key]) ul.appendChild(el('li', {}, t));
      frag.appendChild(ul);
    }
    return frag;
  }
  function show(p, b) {
    for (const x of pins) x.b.setAttribute('aria-pressed', x.b === b ? 'true' : 'false');
    card.replaceChildren();
    const seen = new Set([`${p.k}:${p.id}`]);
    card.appendChild(entry(p));
    for (const x of pins) {
      const key = `${x.p.k}:${x.p.id}`;
      if (x.b.hidden || seen.has(key) || Math.hypot(x.p.x - p.x, x.p.y - p.y) > NEAR) continue;
      seen.add(key);
      card.appendChild(entry(x.p));
    }
    card.appendChild(el('p', { class: 'wk-map-credit' }, 'Donnée communautaire, à confirmer en jeu.'));
    const close = el('button', { type: 'button' }, 'Fermer');
    close.addEventListener('click', () => { card.hidden = true; b.setAttribute('aria-pressed', 'false'); b.focus(); });
    card.appendChild(close);
    card.hidden = false;
  }
  function filter() {
    const on = new Set([...box.querySelectorAll('.wk-map-filters input:checked')].map(i => i.getAttribute('data-role')));
    for (const x of pins) x.b.hidden = !on.has(x.role);
  }
  for (const i of box.querySelectorAll('.wk-map-filters input')) i.addEventListener('change', filter);
  box.addEventListener('keydown', e => { if (e.key === 'Escape' && !card.hidden) { card.hidden = true; } });
  filter();
}

for (const box of document.querySelectorAll('.wk-map[data-map]')) setup(box);
