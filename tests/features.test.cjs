const test = require('node:test');
const assert = require('node:assert/strict');
const features = require('../app/static/features.js');

test('custom date validation accepts valid periods and leap dates', () => {
  assert.equal(features.validateRange('2026-11-01', '2026-11-11', '2026-11-11'), null);
  assert.equal(features.validateRange('2024-02-29', '2024-03-01', '2026-11-11'), null);
});
test('invalid, reversed, future and oversized date ranges are rejected', () => {
  for (const [start, end] of [['2026-02-30', '2026-03-01'], ['', '2026-01-01'], ['2026-11-11', '2026-11-01'], ['2026-11-01', '2026-12-01'], ['2024-01-01', '2026-01-01']]) {
    assert.ok(features.validateRange(start, end, '2026-11-11'));
  }
});
test('above and below targets include equality', () => {
  const response = {cache_status: 'fresh', rates: [{base: 'USD', quote: 'NGN', rate: '1500'}]};
  for (const direction of ['above', 'below']) assert.equal(features.alertState({base: 'USD', quote: 'NGN', target: 1500, direction}, response), 'met');
  assert.equal(features.alertState({base: 'USD', quote: 'NGN', target: 1600, direction: 'above'}, response), 'waiting');
  assert.equal(features.alertState({base: 'USD', quote: 'NGN', target: 1400, direction: 'below'}, response), 'waiting');
});
test('stale, missing and malformed rates never trigger targets', () => {
  const rule = {base: 'USD', quote: 'NGN', target: 1, direction: 'above'};
  assert.equal(features.alertState(rule, {cache_status: 'stale', rates: [{base: 'USD', quote: 'NGN', rate: 1500}]}), 'unavailable');
  assert.equal(features.alertState(rule, {rates: []}), 'unavailable');
  assert.equal(features.alertState(rule, null), 'unavailable');
  assert.equal(features.alertState(rule, {rates: [{base: 'USD', quote: 'NGN', rate: 'NaN'}]}), 'unavailable');
});
test('trend summary uses exact observation arithmetic', () => {
  assert.deepEqual(features.stats([{rate: '2'}, {rate: '4'}, {rate: '6'}]), {low: 2, high: 6, mean: 4, count: 3});
  assert.equal(features.stats([]), null);
  assert.equal(features.stats([{rate: 'NaN'}]), null);
});
test('CSV cells quote delimiters and neutralize spreadsheet formula prefixes', () => {
  assert.equal(features.csvCell('a,"b"'), '"a,""b"""');
  assert.equal(features.csvCell('=1+1'), '"\'=1+1"');
  assert.equal(features.csvCell('1500'), '"1500"');
});
