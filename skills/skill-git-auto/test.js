import assert from 'node:assert';
import { utf8ToBase64, pushDirectGitFiles } from './git-auto.js';

const mockStore = {
  refSha: 'ref_111',
  baseTree: 'tree_222',
  blobs: {},
  newTree: 'tree_333',
  newCommit: 'commit_444'
};

async function mockXhr(url, method, headers, body) {
  assert.strictEqual(headers.Authorization.startsWith('Bearer ghp_'), true);

  if (url.includes('/git/refs/heads/main')) {
    if (method === 'GET') {
      return { ok: true, status: 200, json: { object: { sha: mockStore.refSha } } };
    }
    if (method === 'PATCH') {
      const b = JSON.parse(body);
      assert.strictEqual(b.sha, mockStore.newCommit);
      return { ok: true, status: 200, json: { object: { sha: b.sha } } };
    }
  }
  if (url.includes('/git/commits/ref_111') && method === 'GET') {
    return { ok: true, status: 200, json: { tree: { sha: mockStore.baseTree } } };
  }
  if (url.includes('/git/blobs') && method === 'POST') {
    const b = JSON.parse(body);
    const sha = 'blob_' + Math.random().toString(36).slice(2, 7);
    mockStore.blobs[sha] = b.content;
    return { ok: true, status: 201, json: { sha } };
  }
  if (url.includes('/git/trees') && method === 'POST') {
    return { ok: true, status: 201, json: { sha: mockStore.newTree } };
  }
  if (url.includes('/git/commits') && method === 'POST') {
    return { ok: true, status: 201, json: { sha: mockStore.newCommit } };
  }
  return { ok: false, status: 404, json: {} };
}

async function test() {
  const b64 = utf8ToBase64('Hello World');
  assert.strictEqual(Buffer.from(b64, 'base64').toString('utf8'), 'Hello World');

  const sha = await pushDirectGitFiles({
    owner: 'jionni885-cell',
    repo: 'study-board',
    branch: 'main',
    token: 'ghp_MockTokenValid12345',
    files: [
      { path: 'vocals/v1.json', base64Content: b64 }
    ],
    message: 'test commit',
    xhrFn: mockXhr
  });

  assert.strictEqual(sha, 'commit_444');
  console.log('✅ skill-git-auto test passé avec succès');
}

test().catch(e => {
  console.error('❌ skill-git-auto test échoué:', e);
  process.exit(1);
});
