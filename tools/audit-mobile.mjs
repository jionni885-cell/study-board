#!/usr/bin/env node
/**
 * AUDIT MOBILE / TÉLÉPHONE — Study Board (navigateur réel, moteur Chromium)
 * =========================================================================
 * Le site est fabriqué pour être lu sur téléphone : cet audit charge index.html
 * et vocal.html dans un VRAI navigateur, en 320 / 360 / 390 / 414 px de large
 * (plus la tablette 768), et vérifie ce qu'un œil humain verrait :
 *
 *   1. débordement horizontal (la page qu'on peut tirer sur le côté) ;
 *   2. éléments qui sortent de l'écran (titre coupé, bouton hors champ) ;
 *   3. boutons trop petits pour un doigt (< 44 px, seuil Apple/Google) ;
 *   4. textes illisibles (< 12 px) et étirement forcé → zoom auto iOS ;
 *   5. zones non atteignables : bandeau collant, barre de défilement, marges
 *      de sécurité (encoche / barre d'accueil) ;
 *   6. fenêtres plein écran (défis, quiz) qui dépassent la hauteur du téléphone ;
 *   7. erreurs JavaScript et erreurs console pendant la navigation ;
 *   8. contraste insuffisant (WCAG 2.1, calcul de luminance réelle).
 *
 * Le navigateur est cherché automatiquement :
 *   CHROME_PATH=/chemin/chrome        (recommandé en CI ou sur un PC)
 *   npm i puppeteer-core @sparticuz/chromium   (repli autonome, sans réseau)
 * S'il n'y a aucun navigateur, l'audit s'arrête proprement (code 0) en
 * expliquant comment l'installer — il ne bloque jamais la livraison.
 *
 *   node tools/audit-mobile.mjs                 # rapport + code de sortie
 *   node tools/audit-mobile.mjs --shots=/tmp/x  # + captures PNG par écran
 *   node tools/audit-mobile.mjs --json          # rapport machine (CI)
 */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CACHE = path.join(ROOT, 'tools', '.browser-cache');
const ARGV = process.argv.slice(2);
const SHOTS = (ARGV.find((a) => a.startsWith('--shots=')) || '').split('=')[1] || null;
const JSON_OUT = ARGV.includes('--json');

/* Largeurs testées : les vrais téléphones (le plus petit est le plus dur). */
const DEVICES = [
  { nom: 'iPhone SE (320 px)', w: 320, h: 568 },
  { nom: 'Android (360 px)', w: 360, h: 740 },
  { nom: 'iPhone 14 (390 px)', w: 390, h: 844 },
  { nom: 'iPhone Plus (414 px)', w: 414, h: 896 },
  { nom: 'Tablette (768 px)', w: 768, h: 1024 },
];

/** Attend la fin des transitions CSS et des animations : une mesure prise à
 *  mi-transition (couleurs qui s'animent) donne un contraste faux. */
const stable = (page, ms = 1500) => page.evaluate((limite) => new Promise((r) => {
  const t0 = Date.now();
  const fini = () => {
    const a = document.getAnimations ? document.getAnimations() : [];
    if (!a.length || Date.now() - t0 > limite) return r(a.length);
    Promise.all(a.map((x) => x.finished.catch(() => { }))).then(() => r(0)).catch(() => r(0));
  };
  setTimeout(fini, 30);
}), ms);

const erreurs = [];
const avertissements = [];
const info = [];
const err = (c, m) => erreurs.push({ code: c, msg: m });
const warn = (c, m) => avertissements.push({ code: c, msg: m });

/* ------------------------------------------------------------------ */
/* 1. Serveur statique local (le site est servi comme sur GitHub Pages) */
/* ------------------------------------------------------------------ */
const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css',
  '.mp3': 'audio/mpeg', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml',
};
function serve(port) {
  const srv = http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split('?')[0]);
    if (p === '/') p = '/index.html';
    const file = path.join(ROOT, path.normalize(p).replace(/^(\.\.[/\\])+/, ''));
    if (p === '/api/vocals') { res.writeHead(200, { 'content-type': 'application/json' }); return res.end('[]'); }
    if (p === '/api/health') { res.writeHead(200, { 'content-type': 'application/json' }); return res.end('{"ok":true}'); }
    if (p.startsWith('/api/')) { res.writeHead(404, { 'content-type': 'application/json' }); return res.end('{"error":"hors serveur local"}'); }
    fs.readFile(file, (e, buf) => {
      if (e) { res.writeHead(404, { 'content-type': 'text/plain' }); return res.end('404'); }
      res.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream' });
      res.end(buf);
    });
  });
  return new Promise((r) => srv.listen(port, '127.0.0.1', () => r(srv)));
}

/* ------------------------------------------------------------------ */
/* 2. Trouver un navigateur réel                                     */
/* ------------------------------------------------------------------ */
async function libPath() {
  /* Les binaires « serverless » (@sparticuz/chromium) ont besoin des
     bibliothèques NSS livrées à part : on les décompresse une fois. */
  const dir = path.join(CACHE, 'lib');
  if (fs.existsSync(path.join(dir, 'libnss3.so'))) return dir;
  const bin = path.join(ROOT, 'tools', 'node_modules', '@sparticuz', 'chromium', 'bin');
  if (!fs.existsSync(bin)) return null;
  fs.mkdirSync(CACHE, { recursive: true });
  const { execFileSync } = await import('node:child_process');
  const brotli = await import('node:zlib');
  for (const f of ['al2023.tar.br', 'al2.tar.br']) {
    const src = path.join(bin, f);
    if (!fs.existsSync(src)) continue;
    const tar = path.join(CACHE, f.replace('.br', ''));
    fs.writeFileSync(tar, brotli.brotliDecompressSync(fs.readFileSync(src)));
    try { execFileSync('tar', ['-xf', tar, '-C', CACHE], { stdio: 'ignore' }); } catch { /* tar absent : sans gravité */ }
    fs.unlinkSync(tar);
  }
  return fs.existsSync(path.join(dir, 'libnss3.so')) ? dir : null;
}

async function findBrowser() {
  let puppeteer;
  try { puppeteer = (await import('puppeteer-core')).default; } catch {
    try { puppeteer = (await import('puppeteer')).default; } catch { return { skip: 'puppeteer-core absent (npm i -D puppeteer-core)' }; }
  }
  const cands = [];
  if (process.env.CHROME_PATH) cands.push({ exe: process.env.CHROME_PATH, args: [] });
  try { const p = puppeteer.executablePath(); if (p && fs.existsSync(p)) cands.push({ exe: p, args: [] }); } catch { /* pas de Chrome embarqué */ }
  for (const mod of ['@sparticuz/chromium', 'chrome-aws-lambda']) {
    try {
      const m = (await import(mod)).default;
      const exe = await m.executablePath();
      if (!exe || !fs.existsSync(exe)) continue;
      let fonts = null;
      try {
        if (typeof m.font === 'function') {
          const dir = path.join(CACHE, 'fonts');
          fs.mkdirSync(CACHE, { recursive: true });
          fonts = await m.font(dir);
        }
      } catch { /* polices fournies avec le paquet : optionnel */ }
      cands.push({ exe, args: m.args || [], lib: await libPath(), fonts });
    } catch { /* module absent */ }
  }
  for (const p of ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']) {
    if (fs.existsSync(p)) cands.push({ exe: p, args: [] });
  }
  if (!cands.length) return { skip: 'aucun navigateur trouvé (CHROME_PATH=… ou npm i puppeteer-core @sparticuz/chromium)' };
  return { puppeteer, cand: cands[0] };
}

/* ------------------------------------------------------------------ */
/* 3. Contrôles injectés dans la page                                */
/* ------------------------------------------------------------------ */
/** Analyse une vue : débordements, cibles tactiles, tailles de texte, contraste. */
const ANALYSE = () => {
  const out = { overflowPage: 0, horsEcran: [], petitesCibles: [], petitsTextes: [], contrastes: [], docWidth: 0, vw: 0 };
  const de = document.documentElement;
  out.vw = window.innerWidth;
  out.docWidth = de.scrollWidth;
  out.overflowPage = Math.max(0, de.scrollWidth - window.innerWidth);

  const nom = (el) => {
    const id = el.id ? '#' + el.id : '';
    const cl = (typeof el.className === 'string' && el.className) ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
    return el.tagName.toLowerCase() + id + cl;
  };
  const visible = (el, r) => {
    if (!r.width || !r.height) return false;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none' || +st.opacity === 0) return false;
    return true;
  };
  /* Un élément qui dépasse n'est un DÉFAUT que s'il est inaccessible :
     - un ancêtre qui DÉFILE (overflow auto/scroll) → atteignable au doigt, OK ;
     - un ancêtre qui COUPE (overflow hidden/clip) → décor décoratif toléré,
       mais contenu porteur de texte signalé séparément. */
  const chemin = (el) => { const a = []; for (let n = el; n && n !== document.body; n = n.parentElement) a.push([...n.parentElement.children].indexOf(n)); return a.reverse().join('.'); };
  const conteneur = (el) => {
    for (let n = el.parentElement; n && n !== document.body; n = n.parentElement) {
      const st = getComputedStyle(n);
      const ox = st.overflowX, oy = st.overflowY;
      if (/(auto|scroll)/.test(ox) || /(auto|scroll)/.test(oy)) return 'defile';
      if (/(hidden|clip)/.test(ox) || /(hidden|clip)/.test(oy)) return 'coupe';
    }
    return null;
  };

  const all = document.querySelectorAll('body *');
  for (const el of all) {
    const r = el.getBoundingClientRect();
    if (!visible(el, r)) continue;
    const deborde = r.right > window.innerWidth + 1.5 || r.left < -1.5;
    if (!deborde) continue;
    const c = conteneur(el);
    if (c === 'defile') continue;                       // le doigt peut y arriver
    const txt = (el.textContent || '').trim();
    if (c === 'coupe' && !txt) continue;                // halo/décor coupé exprès
    if (!txt && !/^(IMG|VIDEO|CANVAS|svg|path|circle|rect)$/i.test(el.tagName)) continue;
    out.horsEcran.push({ sel: nom(el), right: Math.round(r.right), left: Math.round(r.left), coupe: c === 'coupe', txt: txt.slice(0, 40), ids: chemin(el) });
  }
  /* On ne garde que le responsable le plus haut : si un ancêtre est déjà fautif,
     ses enfants ne sont pas une deuxième erreur (même défaut, même correctif). */
  const haut = out.horsEcran.filter((e) => !out.horsEcran.some((o) => o !== e && o.ids && e.ids && o.ids.startsWith(e.ids) ));
  out.horsEcran = (haut.length ? haut : out.horsEcran).slice(0, 12);

  /* cibles tactiles */
  const cliquables = document.querySelectorAll('button,a[href],[onclick],input[type=checkbox],select,summary');
  for (const el of cliquables) {
    const r = el.getBoundingClientRect();
    if (!visible(el, r)) continue;
    if (Math.min(r.width, r.height) < 40) {
      if (Math.min(r.width, r.height) < 24) out.petitesCibles.push({ sel: nom(el), w: Math.round(r.width), h: Math.round(r.height), grave: 1, txt: (el.textContent || '').trim().slice(0, 28) });
      else out.petitesCibles.push({ sel: nom(el), w: Math.round(r.width), h: Math.round(r.height), grave: 0, txt: (el.textContent || '').trim().slice(0, 28) });
    }
  }

  /* textes et contraste (WCAG 2.1, transparences composées) */
  const opacite = (el) => { let o = 1; for (let n = el; n && n.tagName !== 'HTML'; n = n.parentElement) o *= +getComputedStyle(n).opacity; return o; };
  const lireCouleur = (str) => {
    if (!str || str === 'transparent') return null;
    let m = str.match(/^rgba?\(([^)]+)\)/);
    if (m) { const p = m[1].split(/[,\/ ]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; }
    m = str.match(/^color\(srgb ([^)]+)\)/);          // color-mix() calculé par Chrome
    if (m) { const p = m[1].split(/[\/ ]+/).filter(Boolean).map(Number); return { r: p[0] * 255, g: p[1] * 255, b: p[2] * 255, a: p.length > 3 ? p[3] : 1 }; }
    return null;
  };
  const sur = (a, b) => ({ r: a.r * a.a + b.r * (1 - a.a), g: a.g * a.a + b.g * (1 - a.a), b: a.b * a.a + b.b * (1 - a.a), a: 1 });
  const lum = (c) => { const [r, g, b] = [c.r, c.g, c.b].map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const contraste = (a, b) => { const l1 = lum(a), l2 = lum(b); return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05); };
  const fondDe = (el) => {
    let fond = { r: 255, g: 255, b: 255, a: 1 };
    const pile = [];
    for (let n = el; n; n = n.parentElement) pile.push(n);
    const racine = getComputedStyle(document.documentElement).backgroundColor;
    const base = lireCouleur(racine);
    if (base && base.a === 1) fond = base;
    for (const n of pile.reverse()) {
      const st = getComputedStyle(n);
      if (st.backgroundImage && st.backgroundImage !== 'none') return null;   // dégradé : non calculable
      const c = lireCouleur(st.backgroundColor);
      if (c && c.a > 0.02) fond = sur(c, fond);
    }
    return fond;
  };
  const vus = new Set();
  for (const el of all) {
    if (!el.childNodes.length) continue;
    const txt = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(' ').trim();
    if (!txt || !/[a-zA-ZÀ-ÿ0-9]/.test(txt)) continue;    // emoji / déco seulement
    const r = el.getBoundingClientRect();
    if (!visible(el, r)) continue;
    const st = getComputedStyle(el);
    if (st.backgroundClip === 'text' || (st.webkitTextFillColor && st.webkitTextFillColor !== st.color)) continue;
    const taille = parseFloat(st.fontSize);
    if (taille < 12) out.petitsTextes.push({ sel: nom(el), px: +taille.toFixed(1), txt: txt.slice(0, 40) });
    const c1 = lireCouleur(st.color), c2 = fondDe(el);
    if (c1 && c2) {
      const col = c1.a < 1 ? sur(c1, c2) : c1;
      const ratio = contraste(col, c2);
      const gros = taille >= 24 || (taille >= 18.66 && +st.fontWeight >= 700);
      const mini = gros ? 3 : 4.5;
      if (ratio < mini) {
        const cle = nom(el) + '|' + Math.round(ratio * 10);
        if (!vus.has(cle)) {
          vus.add(cle);
          const hx = (c) => '#' + [c.r, c.g, c.b].map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');
          out.contrastes.push({ sel: nom(el), ratio: +ratio.toFixed(2), mini, px: +taille.toFixed(1), txt: txt.slice(0, 40), fg: hx(col), bg: hx(c2), brut: st.color, op: +opacite(el).toFixed(2), ou: el.outerHTML.slice(0, 150), parent: el.parentElement ? el.parentElement.className || el.parentElement.tagName : '' });
        }
      }
    }
  }
  out.contrastes = out.contrastes.slice(0, 12);
  out.petitsTextes = out.petitsTextes.slice(0, 12);
  out.petitesCibles = out.petitesCibles.slice(0, 20);
  out.petitsTextes = out.petitsTextes.slice(0, 12);
  out.contrastes = out.contrastes.slice(0, 12);
  return out;
};

/* ------------------------------------------------------------------ */
/* 4. Parcours                                                       */
/* ------------------------------------------------------------------ */
const ROUTES = (D) => {
  const r = [['accueil', '#/'], ['exposé Yémen', '#/expose/yemen']];
  for (let mi = 0; mi < D.length; mi++) {
    for (let fi = 0; fi < D[mi].fiches.length; fi++) {
      for (const [t, lab] of [['lire', 'Lire'], ['fc', 'Cartes'], ['quiz', 'Quiz']])
        r.push([`${D[mi].nom} ${mi}-${fi} ${lab}`, `#/f/${mi}/${fi}/${t}`]);
    }
  }
  return r;
};

let parcours = 0;          // nombre d'interactions réellement jouées (preuve du parcours)

async function main() {
  const found = await findBrowser();
  if (found.skip) {
    if (JSON_OUT) console.log(JSON.stringify({ skip: true, raison: found.skip }));
    else {
      console.log('='.repeat(66));
      console.log('AUDIT MOBILE — IGNORÉ (aucun navigateur réel disponible)');
      console.log('='.repeat(66));
      console.log('  ' + found.skip);
      console.log('  Pour l\'activer :  npm exec --prefix tools -- audit:mobile');
      console.log('  ou :  CHROME_PATH=/usr/bin/chromium node tools/audit-mobile.mjs');
    }
    return 0;
  }
  const { puppeteer, cand } = found;
  const port = 4780 + Math.floor(Math.random() * 100);
  const srv = await serve(port);
  const base = `http://127.0.0.1:${port}`;
  info.push(`navigateur : ${cand.exe}`);
  info.push(`serveur : ${base}`);

  const browser = await puppeteer.launch({
    executablePath: cand.exe,
    args: [...(cand.args || []), '--no-sandbox', '--disable-dev-shm-usage', '--hide-scrollbars'],
    headless: true,
    env: { ...process.env, ...(cand.lib ? { LD_LIBRARY_PATH: cand.lib + (process.env.LD_LIBRARY_PATH ? ':' + process.env.LD_LIBRARY_PATH : '') } : {}), ...(cand.fonts ? { FONTCONFIG_PATH: cand.fonts } : {}) },
  });

  const D = await (async () => {
    const p = await browser.newPage();
    await p.goto(base + '/index.html', { waitUntil: 'domcontentloaded' });
    const d = await p.evaluate(() => { try { return D.map((m) => ({ nom: m.nom, fiches: m.fiches.map((f) => ({ titre: f.titre, fc: f.flashcards.length, quiz: f.quiz.length })) })); } catch { return null; } });
    await p.close();
    return d;
  })();

  const routes = ROUTES(D || [{ nom: 'SES', fiches: [{ titre: '', fc: 0, quiz: 0 }] }]);
  if (SHOTS) fs.mkdirSync(SHOTS, { recursive: true });

  for (const dev of DEVICES) {
    const page = await browser.newPage();
    await page.setViewport({ width: dev.w, height: dev.h, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const errs = [];
    page.on('pageerror', (e) => errs.push('pageerror: ' + String(e.message).split('\n')[0]));
    page.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push('console: ' + m.text().slice(0, 120)); });
    page.on('response', (r) => {
      if (r.status() < 400) return;
      const u = r.url().replace(base, '');
      if (/\.m4a$/.test(u)) return;      // vocaux privés : absents par conception, lecteurs masqués
      errs.push(`ressource ${r.status()} : ${u}`);
    });
    await page.goto(base + '/index.html', { waitUntil: 'load' });
    await page.evaluate(() => { try { localStorage.clear(); } catch { } });

    for (const [label, hash] of routes) {
      await page.evaluate((h) => { location.hash = h; window.dispatchEvent(new HashChangeEvent('hashchange')); }, hash);
      await new Promise((r) => setTimeout(r, 140));
      await stable(page);
      const a = await page.evaluate(ANALYSE);
      const tag = `${dev.nom} · ${label}`;
      const th = await page.evaluate(() => { const t = document.querySelector('.top-in'); return t ? Math.round(t.getBoundingClientRect().height) : null; });
      if (th && th > 84) err('en-tête', `${tag} : en-tête de ${th} px (le bandeau se casse en plusieurs lignes)`);
      if (a.overflowPage > 1) err('débordement', `${tag} : la page déborde de ${a.overflowPage} px (scrollWidth ${a.docWidth} > ${a.vw}).`);
      const grosHors = a.horsEcran.filter((e) => (e.right || 0) > dev.w + 6 || (e.left || 0) < -6);
      if (grosHors.length) err('hors-écran', `${tag} : ${grosHors.length} élément(s) hors de l'écran → ` + grosHors.slice(0, 3).map((e) => `${e.sel} (${e.right ? 'right ' + e.right : 'left ' + e.left}) « ${e.txt} »`).join(' ; '));
      const graves = a.petitesCibles.filter((c) => c.grave);
      if (graves.length) err('cible-tactile', `${tag} : ${graves.length} bouton(s) < 24 px → ` + graves.slice(0, 4).map((c) => `${c.sel} ${c.w}×${c.h} « ${c.txt} »`).join(' ; '));
      const petites = a.petitesCibles.filter((c) => !c.grave);
      if (petites.length) warn('cible-tactile', `${tag} : ${petites.length} bouton(s) entre 24 et 44 px → ` + petites.slice(0, 3).map((c) => `${c.sel} ${c.w}×${c.h}`).join(' ; '));
      if (a.petitsTextes.length) warn('texte', `${tag} : texte < 12 px → ` + a.petitsTextes.slice(0, 3).map((x) => `${x.sel} ${x.px}px`).join(' ; '));
      if (a.contrastes.length) warn('contraste', `${tag} : contraste faible → ` + a.contrastes.slice(0, 3).map((c) => `${c.sel} ${c.ratio}:1 (min ${c.mini}) ${c.fg} sur ${c.bg} [couleur ${c.brut}, opacité ${c.op}, parent ${c.parent}] « ${c.txt} »`).join(' ; '));
      if (SHOTS && (hash === '#/' || dev.w === 390)) {
        await page.screenshot({ path: path.join(SHOTS, `${dev.w}-${hash.replace(/[#/]/g, '_') || 'accueil'}.png`), fullPage: false });
      }
    }

    /* --- interactions réelles sur le plus petit écran --- */
    if (dev.w === 320) {
      await page.evaluate(() => { location.hash = '#/f/0/0/lire'; window.dispatchEvent(new HashChangeEvent('hashchange')); });
      await new Promise((r) => setTimeout(r, 150));
      /* défis express : la fenêtre doit tenir dans l'écran */
      const ouvert = await page.evaluate(() => { const b = [...document.querySelectorAll('button')].find((x) => /Défis express/i.test(x.textContent)); if (b) { b.click(); return true; } return false; });
      if (!ouvert) err('défis', `${dev.nom} : aucun bouton « Défis express » sur la fiche`);
      else {
        await new Promise((r) => setTimeout(r, 350));
        const f = await page.evaluate(() => {
          const s = document.querySelector('.dfov .sheet');
          if (!s) return null;
          const r = s.getBoundingClientRect();
          const body = s.querySelector('.dfbody');
          const x = s.querySelector('.dfhead .x');
          const xr = x ? x.getBoundingClientRect() : null;
          return { h: Math.round(r.height), w: Math.round(r.width), vh: window.innerHeight, vw: window.innerWidth, top: Math.round(r.top),
            bodyScroll: body ? (/(auto|scroll)/.test(getComputedStyle(body).overflowY) || body.scrollHeight > body.clientHeight + 2) : null, closeReachable: xr ? (xr.top >= 0 && xr.bottom <= window.innerHeight && xr.right <= window.innerWidth) : false,
            closeSize: xr ? `${Math.round(xr.width)}×${Math.round(xr.height)}` : null };
        });
        if (!f) err('défis', `${dev.nom} : la fenêtre des défis ne s'affiche pas`);
        else {
          if (f.h > f.vh) err('défis', `${dev.nom} : la fenêtre des défis (${f.h} px) dépasse la hauteur de l'écran (${f.vh} px)`);
          if (f.top < 0) err('défis', `${dev.nom} : la fenêtre des défis dépasse en haut (top ${f.top})`);
          if (!f.closeReachable) err('défis', `${dev.nom} : bouton fermer inaccessible (${f.closeSize})`);
          if (!f.bodyScroll) warn('défis', `${dev.nom} : le contenu des défis n'est pas défilable (question longue coupée ?)`);
        }
        /* on joue VRAIMENT un défi : la réponse doit faire avancer l'écran */
        const avant = await page.evaluate(() => document.querySelector('.dfov').innerHTML.length);
        const clique = await page.evaluate(() => {
          const ov = document.querySelector('.dfov');
          const b = [...ov.querySelectorAll('button')].find((x) => /^\s*(✓|✗|Vrai|Faux)/.test(x.textContent.trim()) && !x.disabled);
          if (!b) return false;
          b.click(); return true;
        });
        await new Promise((r) => setTimeout(r, 500));
        const apres = await page.evaluate(() => {
          const ov = document.querySelector('.dfov');
          const r = ov.querySelector('.dfbody');
          return { longueur: ov.innerHTML.length, deborde: r ? r.getBoundingClientRect().right > window.innerWidth + 1 : false, score: (ov.textContent.match(/\b[0-9]+\s*\/\s*[0-9]+|Défi [0-9]+\/[0-9]+/) || [''])[0] };
        });
        if (!clique) err('parcours', `${dev.nom} : aucun bouton de réponse jouable dans les défis`);
        else {
          parcours++;
          if (apres.longueur === avant) err('parcours', `${dev.nom} : répondre à un défi ne change rien à l'écran`);
          if (apres.deborde) err('parcours', `${dev.nom} : le contenu du défi déborde de l'écran après la réponse`);
          info.push(`défi joué en ${dev.w} px → ${apres.score || 'état suivant affiché'}`);
        }
        if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `320-defis.png`), fullPage: false });
        await page.evaluate(() => window.closeDefis && window.closeDefis());
      }
      /* --- on joue vraiment : une question de quiz et un défi, en 320 px --- */
      await page.evaluate(() => { location.hash = '#/f/0/0/quiz'; window.dispatchEvent(new HashChangeEvent('hashchange')); });
      await new Promise((r) => setTimeout(r, 250));
      const quiz = await page.evaluate(() => {
        const b = document.querySelector('#quizBody .q-opt');
        if (!b) return null;
        b.click();
        const exp = document.querySelector('#qexp');
        const r = exp ? exp.getBoundingClientRect() : null;
        return { repondu: true, expVisible: exp ? exp.classList.contains('show') : false, expDeborde: r ? (r.right > window.innerWidth + 1 || r.left < -1) : false, explicationVide: exp ? !exp.textContent.trim() : true };
      });
      if (!quiz) err('parcours', `${dev.nom} : la première question de quiz ne s'affiche pas`);
      else {
        parcours++;
        if (!quiz.expVisible) err('parcours', `${dev.nom} : cliquer une réponse n'affiche pas l'explication`);
        if (quiz.explicationVide) err('parcours', `${dev.nom} : explication vide après la réponse`);
        if (quiz.expDeborde) err('parcours', `${dev.nom} : l'explication sort de l'écran`);
      }
      /* thème sombre : même contrôle de débordement */
      await page.evaluate(() => { window.setTheme('dark'); location.hash = '#/f/0/0/quiz'; window.dispatchEvent(new HashChangeEvent('hashchange')); });
      await new Promise((r) => setTimeout(r, 300));
      await stable(page);
      const dark = await page.evaluate(ANALYSE);
      if (dark.overflowPage > 1) err('débordement', `${dev.nom} · thème sombre : débordement de ${dark.overflowPage} px`);
      if (dark.contrastes.length) warn('contraste', `${dev.nom} · thème sombre : ` + dark.contrastes.slice(0, 3).map((c) => `${c.sel} ${c.ratio}:1 (${c.fg} sur ${c.bg} [couleur ${c.brut}, opacité ${c.op}] « ${c.txt} »)`).join(' ; '));
      await page.evaluate(() => window.setTheme('light'));
    }

    /* --- vocal.html : page prioritaire sur téléphone --- */
    await page.goto(base + '/vocal.html', { waitUntil: 'load' });
    await new Promise((r) => setTimeout(r, 250));
    await stable(page);
    const av = await page.evaluate(ANALYSE);
    const tag = `${dev.nom} · Studio Vocal`;
    /* en-tête : s'il tient sur plusieurs lignes, il mange l'écran */
    const entete = await page.evaluate(() => {
      const t = document.querySelector('.top-in') || document.querySelector('header');
      if (!t) return null;
      const r = t.getBoundingClientRect();
      const marque = t.querySelector('.brand b');
      const mr = marque ? marque.getBoundingClientRect() : null;
      return { h: Math.round(r.height), marqueLignes: mr ? Math.round(mr.height / parseFloat(getComputedStyle(marque).lineHeight || 20)) : null };
    });
    if (entete && entete.h > 84) err('en-tête', `${tag} : l'en-tête fait ${entete.h} px de haut (trop : le contenu passe sous la ligne de flottaison)`);
    if (av.overflowPage > 1) err('débordement', `${tag} : débordement de ${av.overflowPage} px`);
    const hz = av.horsEcran.filter((e) => (e.right || 0) > dev.w + 6 || (e.left || 0) < -6);
    if (hz.length) err('hors-écran', `${tag} : ` + hz.slice(0, 3).map((e) => `${e.sel} (${e.right}) « ${e.txt} »`).join(' ; '));
    const gv = av.petitesCibles.filter((c) => c.grave);
    if (gv.length) err('cible-tactile', `${tag} : ` + gv.slice(0, 4).map((c) => `${c.sel} ${c.w}×${c.h} « ${c.txt} »`).join(' ; '));
    /* zooms automatiques iOS : champ de saisie < 16 px */
    const zooms = await page.evaluate(() => [...document.querySelectorAll('input,textarea,select')]
      .filter((e) => parseFloat(getComputedStyle(e).fontSize) < 16 && e.type !== 'checkbox' && e.type !== 'range')
      .map((e) => `${e.tagName.toLowerCase()}#${e.id || '?'} ${getComputedStyle(e).fontSize}`));
    if (zooms.length) err('zoom-ios', `${tag} : champ(s) < 16 px (iOS zoome tout seul) → ${zooms.slice(0, 4).join(' ; ')}`);
    if (SHOTS && dev.w === 390) await page.screenshot({ path: path.join(SHOTS, `390-vocal.png`), fullPage: false });
    if (errs.length) { for (const e of [...new Set(errs)].slice(0, 6)) err('js', `${dev.nom} : ${e}`); errs.length = 0; }
    await page.close();
  }

  /* --- marge de sécurité (encoche / barre d'accueil) : contrôle statique --- */
  const srcIndex = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  const srcVocal = fs.readFileSync(path.join(ROOT, 'vocal.html'), 'utf8');
  const viewportCover = /viewport-fit=cover/.test(srcIndex);
  const insets = /env\(safe-area-inset-/.test(srcIndex);
  if (viewportCover && !insets) err('encoche', 'index.html : viewport-fit=cover sans marge de sécurité env(safe-area-inset-*) → contenu sous l\'encoche / la barre d\'accueil iPhone');
  if (!/env\(safe-area-inset-/.test(srcVocal)) warn('encoche', 'vocal.html : aucune marge de sécurité env(safe-area-inset-*) (contenu sous la barre d\'accueil iPhone)');
  if (!/100dvh|100svh|min-height:100vh;?\s*}?/.test(srcIndex) || !/dvh|svh/.test(srcIndex)) warn('hauteur', 'index.html : aucune unité dynamique (dvh/svh) → hauteur faussée par la barre d\'adresse mobile');
  if (!/dvh|svh/.test(srcVocal)) warn('hauteur', 'vocal.html : aucune unité dynamique (dvh/svh)');

  await browser.close();
  srv.close();

  /* ---------------------------- rapport ---------------------------- */
  const uniqE = [...new Map(erreurs.map((e) => [e.code + e.msg, e])).values()];
  const uniqW = [...new Map(avertissements.map((e) => [e.code + e.msg, e])).values()];
  if (parcours < 2) err('parcours', `seulement ${parcours} interaction(s) réellement jouée(s) — le parcours n'a pas été testé`);
  if (JSON_OUT) {
    console.log(JSON.stringify({ erreurs: uniqE, avertissements: uniqW, info, parcours }, null, 2));
  } else {
    console.log('='.repeat(66));
    console.log('AUDIT MOBILE / TÉLÉPHONE — navigateur réel (Chromium)');
    console.log('='.repeat(66));
    info.forEach((i) => console.log('  ' + i));
    console.log(`  ${DEVICES.length} tailles d'écran (${DEVICES.map((d) => d.w).join(' / ')} px) · ${routes.length} écrans chacune`);
    console.log(`  ${parcours} interaction(s) réellement jouée(s) (quiz + défi) : aucune vérification n'est sautée en silence`);
    console.log(`\nErreurs : ${uniqE.length}`);
    uniqE.slice(0, 40).forEach((e) => console.log(`  ✗ [${e.code}] ${e.msg}`));
    console.log(`\nAvertissements : ${uniqW.length}`);
    uniqW.slice(0, 25).forEach((e) => console.log(`  ! [${e.code}] ${e.msg}`));
    console.log(uniqE.length ? '\n❌ Téléphone : défauts à corriger.' : '\n✅ Téléphone : aucun défaut bloquant.');
  }
  return uniqE.length ? 1 : 0;
}

process.exit(await main().catch((e) => { console.error('audit-mobile : erreur interne →', e.message); return 1; }));
