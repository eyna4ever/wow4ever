// Authoring helpers. Every factual block lists source keys (see sources-2026-10-24.json).
export const P = (fr, en, ...src) => ({type: 'p', fr, en, src});
export const I = (fr, en, ...src) => ({fr, en, src});
export const L = (...items) => ({type: 'list', items});
export const C = (fr, en = fr) => ({fr, en});
export const TB = (caption, head, rows, ...src) => ({type: 'table', caption, head, rows, src});
export const S = (id, fr, en, ...blocks) => ({id, title: {fr, en}, blocks});
export const D = (date, fr, en, ...src) => ({date, fr, en, src});
export const Q = (fr, en) => ({fr, en});
