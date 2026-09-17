// Code copié et adapté de addpipe/simple-recorderjs-demo
export function createUploadXhr(url, blob, filename, headers = {}) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    for (const [k, v] of Object.entries(headers)) {
      try { xhr.setRequestHeader(k, v); } catch(e) {}
    }
    xhr.onload = function() {
      if (this.readyState === 4) {
        let json = null;
        try { json = JSON.parse(this.responseText); } catch(e) { json = { text: this.responseText }; }
        resolve({ status: this.status, ok: this.status >= 200 && this.status < 300, json });
      }
    };
    xhr.onerror = () => reject(new Error('Network error during upload'));
    xhr.ontimeout = () => reject(new Error('Timeout during upload'));
    xhr.timeout = 30000;

    const fd = new FormData();
    fd.append('audio_data', blob, filename);
    xhr.send(fd);
  });
}
