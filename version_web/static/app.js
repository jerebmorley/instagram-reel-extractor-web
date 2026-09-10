document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('extract-form');
  const submitButton = document.getElementById('submit-button');
  const alertBox = document.getElementById('alert-box');
  const progressCard = document.getElementById('progress-card');
  const progressStatus = document.getElementById('progress-status');
  const progressPercent = document.getElementById('progress-percent');
  const progressBar = document.getElementById('progress-bar');
  const progressMessage = document.getElementById('progress-message');
  const resultCard = document.getElementById('results-card');
  const downloadLink = document.getElementById('download-link');
  const resultFileName = document.getElementById('result-file-name');
  const resultTotal = document.getElementById('result-total');
  const historyList = document.getElementById('history-list');
  const stepItems = [...document.querySelectorAll('.step')];

  function setAlert(type, text) {
    alertBox.className = `alert ${type}`;
    alertBox.textContent = text;
    alertBox.classList.remove('hidden');
  }

  function clearAlert() {
    alertBox.textContent = '';
    alertBox.className = 'alert hidden';
  }

  function updateStepState(stepName, status) {
    stepItems.forEach((item) => {
      item.classList.remove('current', 'done', 'pending');
      if (item.dataset.step === stepName) {
        item.classList.add(status);
      } else if (status === 'done' || item.classList.contains('done')) {
        item.classList.add('done');
      } else {
        item.classList.add('pending');
      }
    });
  }

  function renderSteps(state) {
    const currentStep = state.step || 'login';
    const stepOrder = ['login', 'validation', 'extracting'];
    stepOrder.forEach((step, index) => {
      if (state.status === 'done' && index <= 2) {
        updateStepState(step, 'done');
        return;
      }
      if (step === currentStep) {
        updateStepState(step, 'current');
      } else if (stepOrder.indexOf(currentStep) > index) {
        updateStepState(step, 'done');
      } else {
        updateStepState(step, 'pending');
      }
    });

    if (state.status === 'error') {
      stepItems.forEach((item) => {
        item.classList.remove('current');
      });
    }
  }

  function updateProgress(data) {
    const { status = 'idle', percent = 0, message = 'Listo para iniciar.', step = 'login' } = data || {};

    progressCard.classList.remove('hidden');
    progressStatus.textContent = status === 'done' ? 'Completado' : status === 'error' ? 'Error' : 'Procesando';
    progressPercent.textContent = `${Math.round(percent)}%`;
    progressBar.style.width = `${percent}%`;
    progressMessage.textContent = message;

    renderSteps({ status, step });

    if (status === 'done') {
      progressStatus.textContent = 'Completado';
    }

    if (status === 'error') {
      progressStatus.textContent = 'Error';
      setAlert('error', message);
    }
  }

  function renderHistory(items) {
    if (!items || !items.length) {
      historyList.innerHTML = '<li class="empty-state">Todavía no realizaste ninguna extracción.</li>';
      return;
    }

    historyList.innerHTML = items.map((item) => `
      <li>
        <div>
          <strong>${item.shortcode}</strong>
          <small>${item.timestamp}</small>
        </div>
        <span>${item.total} comentarios</span>
      </li>
    `).join('');
  }

  async function fetchStatus() {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      updateProgress(data);
    } catch (error) {
      console.error('No se pudo cargar el estado:', error);
    }
  }

  async function fetchHistory() {
    try {
      const response = await fetch('/api/history');
      const items = await response.json();
      renderHistory(items);
    } catch (error) {
      console.error('No se pudo cargar el historial:', error);
    }
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearAlert();
    submitButton.disabled = true;
    submitButton.textContent = 'Extrayendo...';
    resultCard.classList.add('hidden');
    renderSteps({ status: 'running', step: 'login' });
    progressCard.classList.remove('hidden');
    progressBar.style.width = '5%';
    progressStatus.textContent = 'Procesando';
    progressMessage.textContent = 'Iniciando flujo de extracción...';

    const poller = setInterval(fetchStatus, 700);

    try {
      const response = await fetch('/api/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: document.getElementById('username').value,
          password: document.getElementById('password').value,
          reel_url: document.getElementById('reel_url').value,
        }),
      });

      const data = await response.json();
      clearInterval(poller);

      if (!response.ok) {
        updateProgress({ status: 'error', step: 'error', percent: 100, message: data.error || 'No se pudo completar la extracción.' });
        return;
      }

      resultCard.classList.remove('hidden');
      resultFileName.textContent = data.file_name;
      resultTotal.textContent = `${data.total} comentarios`;
      downloadLink.href = data.download_url;
      downloadLink.setAttribute('download', data.file_name);
      updateProgress({ status: 'done', step: 'done', percent: 100, message: `Listo. Se exportaron ${data.total} comentarios del reel ${data.shortcode}.` });
      setAlert('success', `La extracción fue exitosa. Se descargaron ${data.total} comentarios.`);
      await fetchHistory();
    } catch (error) {
      clearInterval(poller);
      updateProgress({ status: 'error', step: 'error', percent: 100, message: 'Se produjo un error inesperado al procesar la extracción.' });
      setAlert('error', 'Se produjo un error inesperado al procesar la extracción.');
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = 'Extraer comentarios';
    }
  });

  fetchStatus();
  fetchHistory();
});
