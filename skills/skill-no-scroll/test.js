import assert from 'node:assert';
import { safeFocusNoScroll } from './no-scroll.js';

let focused = false;
let focusedPreventScroll = false;

const mockEl = {
  tabIndex: -1,
  focus(opts) {
    focused = true;
    if (opts && opts.preventScroll) {
      focusedPreventScroll = true;
    }
  }
};

const ok = safeFocusNoScroll(mockEl);
assert.strictEqual(ok, true);
assert.strictEqual(focused, true);
assert.strictEqual(focusedPreventScroll, true);

console.log('✅ skill-no-scroll test passé avec succès');
