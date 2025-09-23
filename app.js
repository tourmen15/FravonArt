document.getElementById('applyBrand').onclick = () => {
  const primary = document.getElementById('brandPrimary').value;
  const accent = document.getElementById('brandAccent').value;
  const text = document.getElementById('brandText').value;
  document.body.style.setProperty('--brand-primary', primary);
  document.body.style.setProperty('--brand-accent', accent);
  document.body.style.setProperty('--brand-text', text);
  updatePreview();
}

document.getElementById('generateBtn').onclick = () => {
  alert('Preview generated! (Canvas placeholder)');
}

document.getElementById('generateAllBtn').onclick = () => {
  const zip = new JSZip();
  zip.file("preview.png", ""); // placeholder
  zip.generateAsync({type:"blob"}).then(function(content) {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(content);
      a.download = "fravonart-previews.zip";
      a.click();
  });
}

document.getElementById('sendCanvaBtn').onclick = () => {
  alert('This would send the design to Canva (stub)');
}

document.getElementById('genCaption').onclick = () => {
  document.getElementById('caption').value = "Generated caption: Your awesome social post!";
}

document.getElementById('copyCaption').onclick = () => {
  document.getElementById('caption').select();
  document.execCommand('copy');
  alert('Caption copied!');
}
