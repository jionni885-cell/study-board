import assert from 'node:assert';
import { MAX_MS, MAX_S, analyseOral, hesRatio } from './vocal-long.js';

assert.strictEqual(MAX_MS, 1800000);
assert.strictEqual(MAX_S, 1800);

// Test <10 mots
const r1 = analyseOral('Bonjour à tous.');
assert.strictEqual(r1.palier, 'Trop court');

// Test <60 mots
const r2 = analyseOral(Array(30).fill('mot').join(' '));
assert.strictEqual(r2.palier, 'Un peu court');

// Test <600 mots
const r3 = analyseOral(Array(200).fill('mot').join(' '));
assert.strictEqual(r3.palier, 'Parfait 2-5 min');

// Test <1500 mots
const r4 = analyseOral(Array(800).fill('mot').join(' '));
assert.strictEqual(r4.palier, 'Long 5-12 min');
assert.ok(r4.segmentation);
assert.strictEqual(r4.segmentation.flashcards, 5);

// Test >=1500 mots
const r5 = analyseOral(Array(1600).fill('mot').join(' '));
assert.strictEqual(r5.palier, 'XXL 15-30 min');
assert.ok(r5.segmentation);
assert.strictEqual(r5.segmentation.flashcards, 5);

// Test hesitations
const r6 = analyseOral('Euh donc voilà euh je pense que du coup c est bien');
assert.ok(r6.hR > 0.025);
assert.ok(r6.detail.includes('Hésitations'));

console.log('✅ skill-vocal-long test passé avec succès');
