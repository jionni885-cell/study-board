# Skill: Audio Upload (addpipe/simple-recorderjs-demo)

Copie du pattern de `addpipe/simple-recorderjs-demo` :
Utilisation de `XMLHttpRequest` + `FormData` ou JSON au lieu de `fetch` pour une compatibilité maximale sur smartphones (iOS Safari 11+, Android WebView).

## Problème résolu
Sur téléphone, l'API `fetch()` avec de gros blobs audio (WebM / WAV) peut être interrompue ou bloquée par des politiques de connexion strictes sans feedback précis. `XMLHttpRequest` avec `onreadystatechange` / `onload` (readyState === 4) garantit la transmission complète et le rapport d'état exact.

## Implémentation
```javascript
function xhrJson(url, method, headers, body) {
  return new Promise((resolve, reject) => {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    if (headers) {
      for (var k in headers) {
        try { xhr.setRequestHeader(k, headers[k]); } catch(e) {}
      }
    }
    xhr.onload = function() {
      if (this.readyState === 4) {
        var txt = this.responseText || '';
        var j = null;
        try { j = txt ? JSON.parse(txt) : {}; } catch(e) { j = { raw: txt }; }
        resolve({ status: this.status, json: j, text: txt, ok: this.status >= 200 && this.status < 300 });
      }
    };
    xhr.onerror = function() { reject(new Error('xhr network ' + url)); };
    xhr.ontimeout = function() { reject(new Error('xhr timeout ' + url)); };
    xhr.timeout = 25000;
    xhr.send(body || null);
  });
}
```
