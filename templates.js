const templates = [
  {
    id: 1,
    name: 'Instagram Post',
    img: 'assets/template-1.png',
    pro: false
  },
  {
    id: 2,
    name: 'TikTok Story',
    img: 'assets/template-2.png',
    pro: false
  },
  {
    id: 3,
    name: 'Facebook Ad',
    img: 'assets/template-3.png',
    pro: true
  }
];

const templatesContainer = document.getElementById('templates');
templates.forEach(t => {
  const div = document.createElement('div');
  div.className = 'template';
  div.textContent = t.name + (t.pro ? ' (Pro)' : '');
  div.onclick = () => selectTemplate(t.id);
  templatesContainer.appendChild(div);
});

let selectedTemplate = null;
function selectTemplate(id){
  selectedTemplate = templates.find(t=>t.id===id);
  document.querySelectorAll('.template').forEach(el=>el.classList.remove('selected'));
  const el = Array.from(document.querySelectorAll('.template')).find(e=>e.textContent.includes(selectedTemplate.name));
  if(el) el.classList.add('selected');
  updatePreview();
}

function updatePreview() {
  const canvas = document.getElementById('preview');
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#eee';
  ctx.fillRect(0,0,canvas.width,canvas.height);
  if(selectedTemplate){
    ctx.fillStyle = '#0ea5a4';
    ctx.font = '24px sans-serif';
    ctx.fillText(selectedTemplate.name, 20, 50);
  }
}
