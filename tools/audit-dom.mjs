#!/usr/bin/env node
/**
 * Audit fonctionnel de Study Board : exécute réellement index.html dans un DOM
 * (jsdom), joue les défis express, les quiz, les 4 modes de cartes et vérifie la
 * robustesse (état local abîmé, adresses invalides, fichiers audio absents).
 *
 *    cd tools && npm install        # installe jsdom (une seule fois)
 *    node tools/audit-dom.mjs       # code de sortie 1 si un défaut est trouvé
 *
 * Complète tools/audit.py, qui contrôle la structure, les compteurs, la
 * cohérence de README.md / REPRISE.md et l'archive ZIP sans aucune dépendance.
 * Les deux audits tournent aussi en CI (voir tools/audit-workflow.yml).
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { JSDOM, VirtualConsole } from 'jsdom';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const problems = [], warnings = [], jsErrors = [];
const bad = (c, m) => problems.push(`[${c}] ${m}`);
const warn = (c, m) => warnings.push(`[${c}] ${m}`);

let html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
// instrumentation : exposer les constantes enfermées dans les IIFE (copie de test uniquement)
html = html.replace('const DF6 = {', 'const DF6 = window.__DF6 = {');
html = html.replace('const EX6 = {', 'const EX6 = window.__EX6 = {');
html = html.replace('const AUDIOF={', 'const AUDIOF=window.__AUDIOF={');

const vc = new VirtualConsole();
vc.on('jsdomError', (e) => {
  const m = String(e.message || '');
  if (/Not implemented/.test(m)) return;                       // window.scrollTo, etc.
  if (/matchMedia is not a function/.test(m)) return;          // non implémenté par jsdom
  jsErrors.push('jsdomError: ' + m.split('\n')[0]);
});
vc.on('error', (...a) => {
  const m = a.join(' ');
  if (/Not implemented/.test(m)) return;
  jsErrors.push('console.error: ' + m.split('\n')[0]);
});

const dom = new JSDOM(html, { url: 'http://localhost/', runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc });
const { window } = dom;
await new Promise((r) => setTimeout(r, 250));
const doc = window.document;
const D = window.eval('D');
const EXTRA = window.eval('typeof EXTRA!=="undefined"?EXTRA:{}');
const DF6 = window.__DF6 || {}, EX6 = window.__EX6 || {}, AUDIOF = window.__AUDIOF || {};
const $ = (s) => doc.querySelector(s), $$ = (s) => Array.from(doc.querySelectorAll(s));
const sleep = (ms = 30) => new Promise((r) => setTimeout(r, ms));
const nav = async (h) => { window.location.hash = h; window.dispatchEvent(new window.HashChangeEvent('hashchange')); await sleep(70); };
const btn = (t) => $$('.fc-toolbar .seg button').find((b) => b.textContent.includes(t));
const bucketOf = (key, txt) => {
  for (const g of ((DF6[key] || {}).ch || []))
    if (g.t === 'sort' && g.buckets) for (const [cat, items] of Object.entries(g.buckets)) if (items.includes(txt)) return cat;
  return null;
};
const stats = { fiches: 0, defis: 0, quiz: 0 };

/* ---------------- 1. Défis express ---------------- */
/** joue un défi : bonne réponse (ou mauvaise une fois par défi), en tenant compte
    des verrous et des transitions animées du moteur (400 à 1800 ms). */
async function playDefis(key, { wrong = false } = {}) {
  const [mi, fi] = key.split('-').map(Number);
  window.openDefis(mi, fi);
  await sleep(80);
  let st = window.dfState(), guard = 0;
  const vus = new Set(), dejaFaux = new Set();
  while (st && !st.end && guard++ < 400) {
    const type = st.type, i0 = st.i, bad0 = st.bad, ph0 = st.ph;
    vus.add(type);
    const veutFaux = wrong && !dejaFaux.has(i0);
    if (veutFaux) dejaFaux.add(i0);
    let progresse = false, tentative = 0;

    const clicJuste = () => {
      if (type === 'sort') {
        const span = $('#dfplace span');
        if (!span) return false;
        const txt = span.textContent.trim();
        const el = $$('#dfcats .dfcat').find((x) => decodeURIComponent(x.getAttribute('data-cat')) === bucketOf(key, txt) && !x.classList.contains('full'));
        if (!el) return false;
        el.click(); return true;
      }
      return window.dfClickBest();
    };
    const clicFaux = () => {
      if (type === 'sort') {
        const txt = ($('#dfplace span') || {}).textContent;
        const el = $$('#dfcats .dfcat').find((x) => decodeURIComponent(x.getAttribute('data-cat')) !== bucketOf(key, txt) && !x.classList.contains('full'));
        if (el) { el.click(); return true; }
        return false;
      }
      if (type === 'order') {
        const el = $$('.dfopts .dfopt').find((x) => +x.getAttribute('data-i') !== ph0 && !x.classList.contains('off'));
        if (el) { el.click(); return true; }
        return false;
      }
      return window.dfPickWrong();
    };

    while (!progresse && tentative++ < 8) {
      const s = window.dfState();
      if (s.end || s.i !== i0) { progresse = true; break; }
      const clic = (veutFaux && tentative === 1) ? clicFaux() : clicJuste();
      if (!clic) { await sleep(250); continue; }
      const t0 = Date.now();
      while (Date.now() - t0 < 1400) {
        await sleep(40);
        const s2 = window.dfState();
        if (s2.end || s2.i !== i0 || s2.bad !== bad0 || s2.ph !== ph0) { progresse = true; break; }
      }
    }
    st = window.dfState();
    if (!progresse) {
      process.stderr.write(`   diag blocage ${key} défi ${i0 + 1} ${type} → ${JSON.stringify({ end: st.end, i: st.i, bad: st.bad, ph: st.ph, expl: $('#dfexpl') ? $('#dfexpl').textContent.slice(0, 50) : null })}\n`);
      bad('défis', `${key} : blocage au défi ${i0 + 1} (${type}) — le jeu ne progresse pas`);
      break;
    }
  }
  if (!st || !st.end) bad('défis', `${key} : partie non terminée (défi ${st ? st.i + 1 : '?'}/${st ? st.tot : '?'})`);
  else {
    stats.defis++;
    const fin = $('#dfbody').innerHTML;
    if (!/Défi terminé/.test(fin)) bad('défis', `${key} : écran final sans titre`);
    if (!/⭐/.test(fin)) bad('défis', `${key} : étoiles absentes`);
    if (!/Rejouer/.test(fin)) bad('défis', `${key} : bouton « Rejouer » absent`);
    if (wrong && st.bad === 0) bad('défis', `${key} : aucune erreur comptée alors qu'on répond mal`);
    try {
      if (JSON.parse(window.localStorage.getItem('sbdef6') || '{}')[key] == null) bad('défis', `${key} : étoiles non enregistrées`);
    } catch (e) { bad('défis', `${key} : localStorage sbdef6 illisible`); }
    const rb = $$('#dfbody button').find((b) => /Rejouer/.test(b.textContent));
    if (rb) {
      rb.click(); await sleep(120);
      const s = window.dfState();
      if (!s || s.end || s.tot === 0) bad('défis', `${key} : « Rejouer » ne relance pas la partie`);
    }
  }
  window.closeDefis();
  await sleep(30);
  return vus;
}

for (const key of Object.keys(DF6)) {
  const vus = await playDefis(key);
  new Set(DF6[key].ch.map((g) => g.t)).forEach((t) => { if (!vus.has(t)) bad('défis', `${key} : format « ${t} » jamais proposé`); });
  if (DF6[key].ch.length < 4) warn('défis', `${key} : seulement ${DF6[key].ch.length} blocs de défis`);
  if (!(EX6[key] || []).length) bad('astuces', `${key} : aucun encadré astuce/piège`);
  else if (EX6[key].length < 2) warn('astuces', `${key} : moins de 2 astuces/pièges`);
}
for (const key of ['0-0', '2-0', '3-0']) await playDefis(key, { wrong: true });

/* ---------------- 2. Quiz ---------------- */
for (let mi = 0; mi < D.length; mi++) for (let fi = 0; fi < D[mi].fiches.length; fi++) {
  const f = D[mi].fiches[fi], tag = `${mi}-${fi}`;
  if (!f.quiz.length) continue;
  await nav(`#/f/${mi}/${fi}/quiz`);
  for (let i = 0; i < f.quiz.length; i++) {
    const q = f.quiz[i], opts = $$('#quizBody .q-opt');
    if (!opts.length) { bad('quiz', `${tag} : question ${i + 1} non rendue`); break; }
    if (opts.length !== (q.options || ['Vrai', 'Faux']).length) bad('quiz', `${tag} : nombre d'options affichées ≠ données (q${i + 1})`);
    opts[q.reponse].click(); await sleep(20);
    if (!$('#qexp').classList.contains('show')) bad('quiz', `${tag} : explication masquée (q${i + 1})`);
    if (!$('#qnext').classList.contains('show')) bad('quiz', `${tag} : bouton suivant masqué (q${i + 1})`);
    if (!$('#qexp').textContent.includes(String(q.expl).slice(0, 15))) bad('quiz', `${tag} : explication affichée ≠ donnée (q${i + 1})`);
    $('#qnext button').click(); await sleep(20);
  }
  const m = /<div class="sc">(\d+)<\/div>\s*<div class="sc2">sur (\d+)/.exec($('#quizBody').innerHTML);
  if (!m) bad('quiz', `${tag} : écran de résultat absent`);
  else {
    stats.quiz += f.quiz.length;
    if (+m[1] !== f.quiz.length) bad('quiz', `${tag} : score parfait ${m[1]}/${m[2]} (attendu ${f.quiz.length})`);
  }
  if (window.bestS(mi, fi) !== f.quiz.length) bad('quiz', `${tag} : meilleur score non enregistré`);
  // quiz volontairement raté puis reprise
  await nav(`#/f/${mi}/${fi}/quiz`);
  for (let i = 0; i < f.quiz.length; i++) {
    const q = f.quiz[i], opts = $$('#quizBody .q-opt');
    if (!opts.length) break;
    opts[(q.reponse + 1) % opts.length].click(); await sleep(15);
    $('#qnext button').click(); await sleep(15);
  }
  const rep = $$('#quizBody button').find((b) => /Corriger|Recommencer/.test(b.textContent));
  if (!rep) bad('quiz', `${tag} : aucun bouton de reprise après un quiz raté`);
  else {
    rep.click(); await sleep(60);
    if (!$$('#quizBody .q-opt').length) bad('quiz', `${tag} : la reprise après erreurs n'affiche aucune question`);
  }
}

/* ---------------- 3. Cartes : 4 modes × 2 filtres ---------------- */
const mods = [['Étudier', 'study'], ['Écrire', 'write'], ['Associer', 'match'], ['Grille', 'grid']];
for (let mi = 0; mi < D.length; mi++) for (let fi = 0; fi < D[mi].fiches.length; fi++) {
  const f = D[mi].fiches[fi], tag = `${mi}-${fi}`;
  if (!f.flashcards.length) continue;
  stats.fiches++;
  // a) toutes les cartes disponibles
  for (const [label] of mods) for (const [flabel, filter] of [['À réviser', 'rev'], ['Toutes', 'all']]) {
    await nav(`#/f/${mi}/${fi}/fc`);
    if (!btn(flabel)) { bad('cartes', `${tag} : bouton filtre « ${flabel} » absent`); continue; }
    btn(flabel).click(); await sleep(20);
    if (!btn(label)) { bad('cartes', `${tag} : bouton mode « ${label} » absent`); continue; }
    btn(label).click(); await sleep(50);
    const attendu = filter === 'all' ? f.flashcards.length : f.flashcards.length - window.mast(mi, fi).length;
    if (label === 'Grille') {
      const n = $$('#fcBody .gcard').length;
      if (n !== f.flashcards.length) bad('cartes', `${tag}/grille/${flabel} : ${n} cartes affichées (attendu ${f.flashcards.length})`);
    } else if (label === 'Associer') {
      const n = $$('#fcBody .mc').length / 2;
      const exp = Math.min(7, attendu) < 3 ? Math.min(7, f.flashcards.length) : Math.min(7, attendu);
      if (n < 2) bad('cartes', `${tag}/associer/${flabel} : ${n} paires`);
      else if (n !== exp) warn('cartes', `${tag}/associer/${flabel} : ${n} paires (attendu ${exp})`);
    } else {
      if (!$('#carte') && !/study-done/.test($('#fcBody').innerHTML) && !/wIn/.test($('#fcBody').innerHTML))
        bad('cartes', `${tag}/${label}/${flabel} : ni carte ni écran de fin`);
      const pos = /(?:Carte|Écrire) (\d+)\/(\d+)/.exec($('#fcBody').innerHTML);
      if (pos && +pos[2] !== Math.max(1, attendu)) bad('cartes', `${tag}/${label}/${flabel} : file de ${pos[2]} cartes (attendu ${attendu})`);
      if (!pos && /wIn/.test($('#fcBody').innerHTML) && attendu > 0) { /* mode écrire prêt */ }
    }
  }
  // b) régression : maîtrise partielle → le filtre « À réviser » ne sert que les cartes non sues
  for (let i = 0; i < Math.min(5, f.flashcards.length); i++) window.setM(mi, fi, i, true);
  const restantes = f.flashcards.length - Math.min(5, f.flashcards.length);
  for (const [label, mode] of [['Étudier', 'study'], ['Écrire', 'write']]) {
    await nav(`#/f/${mi}/${fi}/fc`);
    btn('À réviser').click(); await sleep(20);
    btn(label).click(); await sleep(50);
    const pos = /(?:Carte|Écrire) (\d+)\/(\d+)/.exec($('#fcBody').innerHTML);
    if (pos && +pos[2] !== restantes) bad('cartes', `${tag}/${label}/À réviser : ${pos[2]} cartes servies au lieu de ${restantes} (filtre ignoré)`);
    await nav(`#/f/${mi}/${fi}/fc`);
    btn('Toutes').click(); await sleep(20);
    btn(label).click(); await sleep(50);
    const pos2 = /(?:Carte|Écrire) (\d+)\/(\d+)/.exec($('#fcBody').innerHTML);
    if (pos2 && +pos2[2] !== f.flashcards.length) bad('cartes', `${tag}/${label}/Toutes : ${pos2[2]} cartes servies au lieu de ${f.flashcards.length}`);
  }
  // c) tout est su → écran de fin, et « Toutes les cartes » permet de continuer
  for (let i = 0; i < f.flashcards.length; i++) window.setM(mi, fi, i, true);
  await nav(`#/f/${mi}/${fi}/fc`);
  btn('À réviser').click(); await sleep(20);
  btn('Étudier').click(); await sleep(50);
  const vide = $('#fcBody').innerHTML;
  if (!/study-done|Séance terminée/.test(vide)) bad('cartes', `${tag} : pas d'écran de fin quand toutes les cartes sont sues`);
  const suite = $$('#fcBody button').find((b) => /Toutes les cartes/.test(b.textContent));
  if (!suite) bad('cartes', `${tag} : aucun bouton « Toutes les cartes » quand tout est su`);
  else {
    suite.click(); await sleep(60);
    if (!$('#carte')) bad('cartes', `${tag} : « Toutes les cartes » n'affiche pas les cartes`);
  }
  for (let i = 0; i < f.flashcards.length; i++) window.setM(mi, fi, i, false);
}

/* ---------------- 4. Mode Écrire : validation des réponses ---------------- */
await nav('#/f/0/0/fc');
btn('Toutes').click(); await sleep(20);
btn('Écrire').click(); await sleep(50);
{
  const attendu = window.eval('D[0].fiches[0].flashcards[FQ.queue[0]].verso');
  const inp = $('#wIn');
  if (!inp) bad('cartes', '0-0/écrire : champ de saisie absent');
  else {
    const essai = (valeur, motif, nom) => {
      inp.value = valeur; window.checkW();
      if (!motif.test($('#wMatch').textContent)) bad('cartes', `0-0/écrire : ${nom} → « ${$('#wMatch').textContent} »`);
    };
    essai('  ' + attendu.toUpperCase() + '  ', /Bonne réponse/, 'réponse exacte (majuscules et espaces) refusée');
    essai('complètement faux', /Pas exact/, 'mauvaise réponse acceptée');
    essai(attendu.normalize('NFD').replace(/[\u0300-\u036f]/g, ''), /Bonne réponse/, 'réponse sans accents refusée');
  }
}

/* ---------------- 5. Audio ---------------- */
{
  for (const [key, slug] of Object.entries(AUDIOF)) {
    if (!fs.existsSync(path.join(ROOT, 'media/audio', slug + '.mp3'))) bad('audio', `${key} : ${slug}.mp3 absent`);
  }
  await nav('#/f/0/0/lire');
  const boite = $$('.audio-box').find((b) => b.querySelector('audio[src*=".m4a"]'));
  if (!boite) warn('audio', 'aucun lecteur .m4a dans la fiche 0-0 (sources attendues)');
  else {
    if (!/display\s*:\s*none/.test(boite.getAttribute('style') || '')) bad('audio', 'la boîte .m4a est visible alors qu\'aucun fichier n\'est confirmé (lecteur cassé)');
    boite.querySelectorAll('audio').forEach((a) => { a.dispatchEvent(new window.Event('loadedmetadata')); });
    await sleep(30);
    if (/display\s*:\s*none/.test(boite.getAttribute('style') || '')) bad('audio', 'un fichier .m4a présent localement n\'affiche pas le lecteur');
    boite.querySelectorAll('audio').forEach((a) => a.dispatchEvent(new window.Event('error')));
    await sleep(30);
    if ($$('.audio-box').some((b) => b.querySelector('audio[src*=".m4a"]'))) bad('audio', 'la boîte .m4a reste affichée alors que tous les fichiers sont absents');
  }
  if (!$$('audio[src*="media/audio/"]').length) bad('audio', 'aucun lecteur MP3 de récapitulatif sur la fiche 0-0');
}

/* ---------------- 6. Robustesse ---------------- */
{
  const etats = ['{}', '5', '"x"', 'null', '{"m":null}', '{"m":{"ses_0":"x"},"best":null}', '{oops', '{"m":{"ses_0":[0,1,2,999,-3,2]},"best":{"ses_0":99}}'];
  for (const st of etats) {
    const html2 = html.replace('</head>', `<script>try{localStorage.setItem('sbv1',${JSON.stringify(st)});localStorage.setItem('sbdef6',${JSON.stringify(st)})}catch(e){}</script></head>`);
    const d2 = new JSDOM(html2, { url: 'http://localhost/', runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc });
    await new Promise((r) => setTimeout(r, 160));
    const app = d2.window.document.querySelector('#app');
    if (!app || !app.innerHTML.trim()) bad('robustesse', `état localStorage ${st} → page d'accueil vide (plantage)`);
    else if (st.includes('ses_0":[0,1,2,999')) {
      const pct = d2.window.document.querySelector('.pct');
      const n = pct ? parseInt(pct.textContent, 10) : null;
      if (n !== null && (n < 0 || n > 100)) bad('robustesse', `progression hors bornes (${n}%) avec des index de cartes périmés`);
    }
    d2.window.close();
  }
  for (const h of ['#/f/abc', '#/f/99/99/lire', '#/f/0/0/xyz', '#/nawak', '#/f/-1/0/fc', '#/f/1/9/lire']) {
    await nav(h);
    if (!$('#app') || !$('#app').innerHTML.trim()) bad('robustesse', `adresse ${h} → page vide`);
  }
  await nav('#/f/0/0/lire');
  window.setTheme('dark'); await sleep(20);
  if (doc.documentElement.getAttribute('data-theme') !== 'dark') bad('ui', 'thème sombre non appliqué');
  window.setTheme('light'); await sleep(20);
  if (!$('#app').innerHTML.trim()) bad('ui', 'page vide après retour au thème clair');
}

/* ---------------- Rapport ---------------- */
console.log('='.repeat(62));
console.log('AUDIT FONCTIONNEL STUDY BOARD (jsdom)');
console.log('='.repeat(62));
console.log(`fiches ${stats.fiches} · défis joués ${stats.defis} · questions de quiz ${stats.quiz}`);
console.log(`\nErreurs JS bloquantes : ${jsErrors.length}`);
jsErrors.slice(0, 10).forEach((e) => console.log('  ✗ ' + e));
console.log(`\nProblèmes : ${problems.length}`);
[...new Set(problems)].forEach((p) => console.log('  ✗ ' + p));
if (warnings.length) {
  console.log(`\nAvertissements : ${[...new Set(warnings)].length}`);
  [...new Set(warnings)].forEach((w) => console.log('  ! ' + w));
}
console.log(problems.length || jsErrors.length ? '\n❌ Défauts à corriger.' : '\n✅ Aucun défaut détecté.');
process.exit(problems.length || jsErrors.length ? 1 : 0);
