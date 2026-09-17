export const MAX_MS = 1800000; // 30 min
export const MAX_S = 1800;

export function hesRatio(txt) {
  const m = txt.match(/\b(euh|hum|ben|bah|alors|donc|du coup)\b/gi);
  const h = m ? m.length : 0;
  const w = txt.trim().split(/\s+/).filter(Boolean).length || 1;
  return h / w;
}

export function analyseOral(txt) {
  const words = txt.trim().split(/\s+/).filter(Boolean).length;
  const secs = Math.round(words / 130 * 60); // 130 mots/min oral
  const hR = hesRatio(txt);
  let palier = '', detail = '', tone = 'ok';

  if (words < 10) {
    palier = 'Trop court';
    detail = 'Ajoute au moins une phrase : dis ton plan en 1 min (≈130 mots).';
    tone = 'warn';
  } else if (words < 60) {
    palier = 'Un peu court';
    detail = 'Quelques phrases de plus et c\'est parfait pour un flash (1 min).';
    tone = 'warn';
  } else if (words < 600) {
    palier = 'Parfait 2-5 min';
    detail = 'Format idéal pour l\'oral 5 min : 3 parties d\'1 min 30 + intro/conclusion.';
    tone = 'ok';
  } else if (words < 1500) {
    palier = 'Long 5-12 min';
    detail = 'Exposé long : je découpe en 3 chapitres + plan chronométré.';
    tone = 'ok';
  } else {
    palier = 'XXL 15-30 min';
    detail = 'Cours complet 15-30 min : je segmente auto (words/3) + sommaire oral + 5 flashcards.';
    tone = 'bad';
  }

  if (hR > 0.025) {
    detail += ` · Hésitations un peu hautes (${(hR * 100).toFixed(1)}%) — ralentis et pose tes phrases.`;
  }

  let segmentation = null;
  if (words >= 600) {
    const segN = Math.min(4, Math.max(3, Math.ceil(words / 600)));
    const per = Math.floor(words / segN);
    const chapitres = [];
    for (let i = 0; i < segN; i++) {
      chapitres.push({
        num: i + 1,
        approxWords: per,
        approxMin: Math.round(per / 130)
      });
    }
    segmentation = {
      segN,
      wordsPerChapter: per,
      chapitres,
      flashcards: 5
    };
  }

  return { words, secs, hR, palier, detail, tone, segmentation };
}
