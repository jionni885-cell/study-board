#!/usr/bin/env node
// Audit complet Study Board — teste chaque erreur pour faciliter la correction
import fs from 'fs';
import { execSync } from 'child_process';

const RED='\x1b[31m', GREEN='\x1b[32m', YELLOW='\x1b[33m', RESET='\x1b[0m';
let errors=0, warns=0;
function ok(m){ console.log(`${GREEN}✅ ${m}${RESET}`); }
function warn(m){ console.log(`${YELLOW}⚠️ ${m}${RESET}`); warns++; }
function fail(m){ console.log(`${RED}❌ ${m}${RESET}`); errors++; }
function check(name, fn){
  try{ fn(); ok(name); }catch(e){ fail(`${name} — ${e.message}`); }
}

console.log('=== AUDIT COMPLET STUDY BOARD ===\n');

// 1. Fichiers requis (token.json n'est PLUS requis : il est local uniquement, gitignoré)
for(const f of ['index.html','vocal.html','server.py','token.json.example']){
  if(fs.existsSync(f)) ok(`Fichier ${f} présent`);
  else fail(`Fichier ${f} manquant`);
}

// 2. Vocal.html — 30 min, token.json, fallback, Permissions-Policy
const vocal = fs.existsSync('vocal.html') ? fs.readFileSync('vocal.html','utf8') : '';
check('vocal.html timer 30 min', ()=>{ if(!vocal.includes('MAX_MS = 1800000') && !vocal.includes('30:00')) throw new Error('MAX_MS 1800000 manquant'); });
check('vocal.html 30 min occurrences', ()=>{ const c=(vocal.match(/30 min/g)||[]).length; if(c<5) throw new Error(`seulement ${c} occurrences 30 min`); });
check('vocal.html SANS URL de token publique', ()=>{ if(vocal.includes('raw.githubusercontent.com') || vocal.includes('github.io/study-board/token.json')) throw new Error('URL de token publique détectée — interdit (sécurité)'); });
const deadSandbox = (txt)=> /https:\/\/[^'\"]*e2b\.(app|dev)/i.test(txt); // URL réelle en dur (pas les hostname endsWith())
check('vocal.html SANS sandbox mort en dur', ()=>{ if(deadSandbox(vocal)) throw new Error('URL e2b en dur détectée (sandbox éphémère mort)'); });
check('vocal.html 401 retry', ()=>{ if(!vocal.includes('401') || !vocal.includes('removeItem')) throw new Error('retry 401 manquant'); });
check('vocal.html SB_FALLBACKS', ()=>{ if(!vocal.includes('SB_FALLBACKS')) throw new Error('SB_FALLBACKS manquant'); });
check('vocal.html Permissions-Policy', ()=>{ if(!vocal.includes('Permissions-Policy')) throw new Error('Permissions-Policy manquant'); });
check('vocal.html pas de prompt() token', ()=>{ if(vocal.includes('prompt("Pour un envoi') || vocal.includes("prompt('Pour un envoi")) warn('encore un prompt() pour token — préférer modal'); else ok('vocal.html modal token OK'); });

// 3. Index.html — 30 min cohérent
const index = fs.existsSync('index.html') ? fs.readFileSync('index.html','utf8') : '';
check('index.html 30 min partout', ()=>{ if(index.includes('20 min') && index.includes('Timer 20')) throw new Error('encore des 20 min'); });
check('index.html SANS sandbox mort en dur', ()=>{ if(deadSandbox(index)) throw new Error('URL e2b en dur détectée (sandbox éphémère mort)'); });

// 4. Server.py — 4173, CORS, 30Mo, rebase
const server = fs.existsSync('server.py') ? fs.readFileSync('server.py','utf8') : '';
check('server.py port 4173', ()=>{ if(!server.includes('4173')) throw new Error('port 4173 manquant'); });
check('server.py CORS', ()=>{ if(!server.includes('Access-Control-Allow-Origin')) throw new Error('CORS manquant'); });
check('server.py 30Mo', ()=>{ if(!server.includes('30*1024*1024') && !server.includes('30 * 1024 * 1024')) throw new Error('30Mo manquant'); });
check('server.py rebase', ()=>{ if(!server.includes('non-fast-forward') || !server.includes('rebase')) throw new Error('logique rebase manquante'); });

// 5. Audit.py — 0 problème
try{
  execSync('python3 tools/audit.py', {stdio:'pipe'});
  ok('audit.py 0 problème');
}catch(e){ fail('audit.py a des problèmes'); }

// 6. Sécurité — token.json JAMAIS suivi par git (le token publié le 17/09/2026 est révélé)
try{
  const r = execSync('git ls-files token.json', {stdio:'pipe'});
  if(r.toString().trim()) throw new Error('token.json est SUIVI PAR GIT — retire-le (git rm --cached token.json)');
  ok('token.json non suivi par git (sécurité OK)');
}catch(e){
  if(e.status===0) throw e; // ne peut pas arriver, mais ne pas masquer les erreurs réelles
  fail(`sécurité token.json — ${e.message.split('\n')[0]}`);
}
// 6b. token.json local optionnel : s'il existe, il doit contenir un champ valide (vérification douce, pas bloquante)
if(fs.existsSync('token.json')){
  try{
    const j = JSON.parse(fs.readFileSync('token.json','utf8'));
    let tok = j.token || (j.t ? Buffer.from(j.t,'base64').toString() : '');
    if(!tok || tok === 'REMPLACE-MOI-EN-BASE64' || !tok.startsWith('ghp_')) warn('token.json local présent mais non renseigné (ou placeholder)');
    else ok(`token.json local présent (ghp_..., jamais commité)`);
  }catch(e){ warn(`token.json local illisible : ${e.message}`); }
}

// 7. Vocals — au moins 1
const vocals = fs.existsSync('vocals') ? fs.readdirSync('vocals').filter(f=>f.endsWith('.json')) : [];
if(vocals.length>0) ok(`vocals/ ${vocals.length} fichier(s)`);
else warn('vocals/ vide — pas encore de vocal utilisateur');

// 8. Headers — Permissions-Policy, CORS
check('index.html headers', ()=>{ if(!index.includes('Permissions-Policy') && !vocal.includes('Permissions-Policy')) warn('Permissions-Policy à vérifier'); });

// Résumé
console.log(`\n=== RÉSULTAT: ${errors} erreurs, ${warns} avertissements ===`);
if(errors===0) console.log(`${GREEN}✅ Tout est cohérent — prêt à corriger automatiquement${RESET}`);
else console.log(`${RED}❌ ${errors} erreurs à corriger — relance avec --fix${RESET}`);
process.exit(errors>0 ? 1 : 0);
