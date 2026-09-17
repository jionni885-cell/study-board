import assert from 'node:assert';
import { getLatestPagesBuild } from './deploy-check.js';

const build = getLatestPagesBuild();
console.log('Pages latest build:', build.status, build.commit ? 'commit ' + build.commit.slice(0, 7) : '');
assert.ok(build.status === 'built' || build.status === 'building' || build.status === 'queued' || build.status === 'unknown');

console.log('✅ skill-deploy test passé avec succès');
