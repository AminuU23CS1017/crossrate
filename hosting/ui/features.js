/* Pure feature rules shared by the browser and dependency-free Node tests. */
(function (root) {
  'use strict';
  const validDate = text => /^\d{4}-\d{2}-\d{2}$/.test(text || '') && Number.isFinite(Date.parse(text)) && new Date(text).toISOString().slice(0, 10) === text;
  const api = {
    validateRange(start, end, today) {
      if (!validDate(start) || !validDate(end)) return 'Choose valid start and end dates.';
      if (start > end) return 'Start date must be on or before end date.';
      if (end > today) return 'End date cannot be in the future.';
      if ((Date.parse(end) - Date.parse(start)) / 86400000 > 366) return 'Choose a range of at most 366 days.';
      return null;
    },
    alertState(rule, response) {
      if (!response || response.cache_status === 'stale') return 'unavailable';
      const value = Number(response.rates?.find(r => r.base === rule.base && r.quote === rule.quote)?.rate);
      if (!Number.isFinite(value) || value <= 0) return 'unavailable';
      return (rule.direction === 'above' ? value >= rule.target : value <= rule.target) ? 'met' : 'waiting';
    },
    stats(rows) {
      const values = rows.map(r => Number(r.rate));
      if (!values.length || values.some(v => !Number.isFinite(v) || v <= 0)) return null;
      return {low: Math.min(...values), high: Math.max(...values), mean: values.reduce((a, b) => a + b, 0) / values.length, count: values.length};
    },
    csvCell(value) {
      let text = String(value ?? '');
      if (/^[=+@\-\t\r]/.test(text)) text = "'" + text;
      return '"' + text.replace(/"/g, '""') + '"';
    }
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.CrossrateFeatures = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
