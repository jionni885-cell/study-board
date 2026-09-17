// Test unitaire de validation du skill audio-upload
import assert from 'node:assert';

class MockXHR {
  constructor() {
    this.headers = {};
    this.readyState = 0;
    this.status = 0;
  }
  open(method, url, async) {
    this.method = method;
    this.url = url;
    this.async = async;
  }
  setRequestHeader(k, v) {
    this.headers[k] = v;
  }
  send(body) {
    this.body = body;
    this.readyState = 4;
    this.status = 200;
    this.responseText = JSON.stringify({ ok: true, id: 'test_123' });
    if (this.onload) this.onload({ target: this });
  }
}

globalThis.XMLHttpRequest = MockXHR;

class MockFormData {
  constructor() { this.entries = {}; }
  append(k, v, filename) { this.entries[k] = { value: v, filename }; }
}

globalThis.FormData = MockFormData;

import { createUploadXhr } from './upload.js';

async function run() {
  const res = await createUploadXhr('/api/vocal', 'fake_blob', 'audio.wav', { 'X-Test': '1' });
  assert.strictEqual(res.ok, true);
  assert.strictEqual(res.status, 200);
  assert.strictEqual(res.json.ok, true);
  console.log('✅ skill-audio-upload test passé avec succès');
}

run().catch(e => {
  console.error('❌ skill-audio-upload test échoué:', e);
  process.exit(1);
});
