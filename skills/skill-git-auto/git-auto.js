// Code copié et adapté du pattern paul.kinlan / freecodecamp
export function utf8ToBase64(str) {
  try {
    const bytes = new TextEncoder().encode(str);
    let bin = '';
    for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    return btoa(bin);
  } catch (e) {
    return Buffer.from(str, 'utf-8').toString('base64');
  }
}

export async function pushDirectGitFiles({ owner, repo, branch, token, files, message, xhrFn }) {
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: 'application/vnd.github.v3+json',
    'Content-Type': 'application/json'
  };

  // 1. Ref
  const refRes = await xhrFn(`https://api.github.com/repos/${owner}/${repo}/git/refs/heads/${branch}`, 'GET', headers, null);
  if (!refRes.ok) throw new Error(`Ref fail: ${refRes.status}`);
  const commitSha = refRes.json.object.sha;

  // 2. Commit tree
  const commitRes = await xhrFn(`https://api.github.com/repos/${owner}/${repo}/git/commits/${commitSha}`, 'GET', headers, null);
  if (!commitRes.ok) throw new Error(`Commit get fail: ${commitRes.status}`);
  const baseTreeSha = commitRes.json.tree.sha;

  // 3. Blobs
  const treeEntries = [];
  for (const f of files) {
    const blobRes = await xhrFn(`https://api.github.com/repos/${owner}/${repo}/git/blobs`, 'POST', headers, JSON.stringify({
      content: f.base64Content,
      encoding: 'base64'
    }));
    if (!blobRes.ok) throw new Error(`Blob fail for ${f.path}: ${blobRes.status}`);
    treeEntries.push({
      path: f.path,
      sha: blobRes.json.sha,
      mode: '100644',
      type: 'blob'
    });
  }

  // 4. Tree
  const treeRes = await xhrFn(`https://api.github.com/repos/${owner}/${repo}/git/trees`, 'POST', headers, JSON.stringify({
    base_tree: baseTreeSha,
    tree: treeEntries
  }));
  if (!treeRes.ok) throw new Error(`Tree create fail: ${treeRes.status}`);

  // 5. Commit
  const newCommitRes = await xhrFn(`https://api.github.com/repos/${owner}/${repo}/git/commits`, 'POST', headers, JSON.stringify({
    message,
    tree: treeRes.json.sha,
    parents: [commitSha]
  }));
  if (!newCommitRes.ok) throw new Error(`Commit create fail: ${newCommitRes.status}`);

  // 6. Update head
  const updRes = await xhrFn(`https://api.github.com/repos/${owner}/${repo}/git/refs/heads/${branch}`, 'PATCH', headers, JSON.stringify({
    sha: newCommitRes.json.sha
  }));
  if (!updRes.ok) throw new Error(`Update head fail: ${updRes.status}`);

  return newCommitRes.json.sha;
}
