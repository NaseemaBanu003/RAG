const chatForm = document.getElementById('chatForm');
const questionInput = document.getElementById('questionInput');
const chatOutput = document.getElementById('chatOutput');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const reindexBtn = document.getElementById('reindexBtn');
const docCounter = document.getElementById('docCounter');

function appendMessage(role, content) {
  const message = document.createElement('div');
  message.className = `message ${role}`;
  message.textContent = content;
  chatOutput.appendChild(message);
  chatOutput.scrollTop = chatOutput.scrollHeight;
}

async function updateStatus() {
  const response = await fetch('/api/status');
  const data = await response.json();
  docCounter.textContent = `${data.indexed_documents || 0} chunks indexed`;
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    return;
  }

  appendMessage('user', question);
  questionInput.value = '';

  try {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, top_k: 4 }),
    });

    const data = await response.json();

    if (!response.ok) {
      appendMessage('bot', data.detail || 'Something went wrong.');
      return;
    }

    let answer = data.answer || 'No answer available.';
    if (data.sources && data.sources.length) {
      answer += '\n\nSources:\n' + data.sources.map((source) => `• ${source.source}`).join('\n');
    }

    appendMessage('bot', answer);
    updateStatus();
  } catch (error) {
    appendMessage('bot', 'The app could not reach the backend. Please ensure the server is running.');
  }
});

uploadBtn.addEventListener('click', async () => {
  const file = fileInput.files[0];
  if (!file) {
    uploadStatus.textContent = 'Please choose a file before uploading.';
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      uploadStatus.textContent = data.detail || 'Upload failed.';
      return;
    }

    uploadStatus.textContent = `${data.filename} was uploaded and indexed (${data.chunks_added} chunks).`;
    uploadStatus.classList.add('success');
    updateStatus();
  } catch (error) {
    uploadStatus.textContent = 'Upload failed. Check that the backend is running.';
  }
});

reindexBtn.addEventListener('click', async () => {
  try {
    const response = await fetch('/api/index', { method: 'POST' });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Re-index failed');
    }

    uploadStatus.textContent = `Workshop materials indexed successfully (${data.chunks_added} chunks).`;
    uploadStatus.classList.add('success');
    updateStatus();
  } catch (error) {
    uploadStatus.textContent = 'Could not re-index the workshop documents.';
  }
});

updateStatus();
