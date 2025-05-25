const uploadBtn    = document.getElementById('uploadBtn');
const setPromptBtn = document.getElementById('setPromptBtn');
const chatBtn      = document.getElementById('chatBtn');

let uploadId = null;

// 1. Upload file and list columns
uploadBtn.addEventListener('click', async () => {
  const fileInput = document.getElementById('fileInput');
  if (!fileInput.files.length) return alert('Select a file first.');
  const form = new FormData();
  form.append('file', fileInput.files[0]);

  const res = await fetch('/upload-file', { method: 'POST', body: form });
  if (!res.ok) return alert('Upload failed.');
  const { upload_id, columns } = await res.json();
  uploadId = upload_id;
  document.getElementById('columnsList').textContent =
    'Columns: ' + columns.join(', ');
  setPromptBtn.disabled = false;
});

// 2. Set system prompt
setPromptBtn.addEventListener('click', async () => {
  const prompt = document.getElementById('promptInput').value.trim();
  if (!prompt) return alert('Enter a prompt.');
  const res = await fetch('/set-prompt', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ upload_id: uploadId, system_prompt: prompt })
  });
  if (!res.ok) return alert('Failed to set prompt.');
  document.getElementById('promptStatus').textContent = 'Prompt set ✓';
  chatBtn.disabled = false;
});

// 3. Chat/query
chatBtn.addEventListener('click', async () => {
  const query = document.getElementById('queryInput').value.trim();
  if (!query) return alert('Enter your question.');
  const res = await fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ upload_id: uploadId, query })
  });
  if (!res.ok) {
    const err = await res.json();
    return alert('Error: ' + err.detail);
  }
  const { response } = await res.json();
  document.getElementById('responseArea').textContent = response;
});
