import assert from 'node:assert';
import { pickSupportedAudioMime, createCompatibleRecorder } from './media-compat.js';

class MockMediaRecorderSafari {
  static isTypeSupported(type) {
    return type === 'audio/mp4' || type === 'audio/aac';
  }
  constructor(stream, opts) {
    this.stream = stream;
    this.opts = opts;
  }
}

class MockMediaRecorderChrome {
  static isTypeSupported(type) {
    return type.startsWith('audio/webm');
  }
  constructor(stream, opts) {
    this.stream = stream;
    this.opts = opts;
  }
}

// Test Safari
const safariMime = pickSupportedAudioMime(MockMediaRecorderSafari);
assert.strictEqual(safariMime, 'audio/mp4');
const safariRec = createCompatibleRecorder({}, MockMediaRecorderSafari, safariMime);
assert.strictEqual(safariRec.opts.mimeType, 'audio/mp4');

// Test Chrome
const chromeMime = pickSupportedAudioMime(MockMediaRecorderChrome);
assert.strictEqual(chromeMime, 'audio/webm;codecs=opus');
const chromeRec = createCompatibleRecorder({}, MockMediaRecorderChrome, chromeMime);
assert.strictEqual(chromeRec.opts.mimeType, 'audio/webm;codecs=opus');

console.log('✅ skill-media-compat test passé avec succès');
