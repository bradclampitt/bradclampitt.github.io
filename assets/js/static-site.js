/**
 * Helpers for GitHub Pages (static site): load CMS/skills/references from unified.sqlite via sql.js
 * when no API is available. Include after sql-wasm.js. Use in Alpine/vanilla loaders:
 * if (window.isStaticSite()) { const db = await window.getIndexDb(); ... }
 */
(function () {
    if (window.isStaticSite) return;
    window.isStaticSite = function () {
        var host = (typeof window !== 'undefined' && window.location && window.location.hostname) ? window.location.hostname : '';
        return host === 'bradclampitt.github.io' || (host && host.endsWith('.github.io'));
    };
    window.getIndexDb = function () {
        if (window.__indexDb) return Promise.resolve(window.__indexDb);
        return initSqlJs({ locateFile: function (file) { return '/assets/js/' + file; } }).then(function (SQL) {
            return fetch('/admin/database/unified.sqlite').then(function (r) {
                if (!r.ok) throw new Error('Failed to load database');
                return r.arrayBuffer();
            }).then(function (buf) {
                window.__indexDb = new SQL.Database(new Uint8Array(buf));
                return window.__indexDb;
            });
        });
    };
})();
