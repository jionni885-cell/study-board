import assert from 'node:assert';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { runFullAudit } from './audit-runner.js';

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');

try {
  const res = runFullAudit(rootDir);
  assert.strictEqual(res.ok, true);
  console.log('✅ skill-audit test passé avec succès (0 erreurs, 0 avertissements)');
} catch (e) {
  console.error('❌ skill-audit test échoué:', e);
  process.exit(1);
}
