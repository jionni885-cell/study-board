import { execSync } from 'node:child_process';

export function getLatestPagesBuild() {
  try {
    const raw = execSync('gh api repos/jionni885-cell/study-board/pages/builds --jq .[0]', {
      encoding: 'utf-8',
      timeout: 10000
    });
    return JSON.parse(raw.trim());
  } catch (e) {
    return { status: 'unknown', error: e.message };
  }
}
