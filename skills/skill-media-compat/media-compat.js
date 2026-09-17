// Code copié et adapté de streamproc/MediaStreamRecorder
export function pickSupportedAudioMime(MediaRecorderClass) {
  if (!MediaRecorderClass || typeof MediaRecorderClass.isTypeSupported !== 'function') {
    return '';
  }
  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/mp4',
    'audio/ogg;codecs=opus',
    'audio/wav',
    'audio/aac'
  ];
  for (const mime of candidates) {
    try {
      if (MediaRecorderClass.isTypeSupported(mime)) {
        return mime;
      }
    } catch (e) {}
  }
  return '';
}

export function createCompatibleRecorder(stream, MediaRecorderClass, mime) {
  let rec = null;
  const targetMime = mime || pickSupportedAudioMime(MediaRecorderClass);
  try {
    if (targetMime) {
      rec = new MediaRecorderClass(stream, { mimeType: targetMime, audioBitsPerSecond: 128000 });
    } else {
      rec = new MediaRecorderClass(stream);
    }
  } catch (e1) {
    try {
      if (targetMime) {
        rec = new MediaRecorderClass(stream, { mimeType: targetMime });
      } else {
        rec = new MediaRecorderClass(stream);
      }
    } catch (e2) {
      rec = new MediaRecorderClass(stream);
    }
  }
  return rec;
}
