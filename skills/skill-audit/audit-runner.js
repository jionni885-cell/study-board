import { execSync } from 'node:child_process';
import path from 'node:path';

export function runFullAudit(rootDir) {
  const auditPy = execSync(`python3 "${path.join(rootDir, 'tools/audit.py')}" --fix-zip`, {
    cwd: rootDir,
    encoding: 'utf-8'
  });
  if (auditPy.includes('Problèmes : 0') === false) {
    throw new Error('audit.py reported issues:\n' + auditPy);
  }

  const auditMjs = execSync(`node "${path.join(rootDir, 'tools/audit-complet.mjs')}"`, {
    cwd: rootDir,
    encoding: 'utf-8'
  });
  if (auditMjs.includes('0 erreurs, 0 avertissements') === false) {
    throw new Error('audit-complet.mjs reported issues:\n' + auditMjs);
  }

  return { ok: true, py: auditPy, mjs: auditMjs };
}
