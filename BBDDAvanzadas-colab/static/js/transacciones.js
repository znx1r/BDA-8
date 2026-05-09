const TYPE_CLASS = {
  info:  'log-info',
  ok:    'log-ok',
  error: 'log-error',
  warn:  'log-warn',
};

async function runDemo(demoId, btn) {
  const logEl = document.getElementById(`log-${demoId}`);

  btn.disabled   = true;
  btn.textContent = '⏳ Ejecutando…';
  logEl.innerHTML = '';
  logEl.style.display = 'block';

  try {
    const res  = await fetch(`/transacciones/run/${demoId}`, { method: 'POST' });
    const json = await res.json();

    if (!json.ok) {
      appendLine(logEl, 'error', `ERROR: ${json.error}`);
      return;
    }

    await animateSteps(logEl, json.steps);

  } catch (e) {
    appendLine(logEl, 'error', `Error de red: ${e.message}`);
  } finally {
    btn.disabled    = false;
    btn.textContent = '▶ Ejecutar de nuevo';
  }
}

async function animateSteps(container, steps) {
  const delay = ms => new Promise(r => setTimeout(r, ms));
  const BASE_DELAY = 340;

  for (const step of steps) {
    await delay(BASE_DELAY);
    appendLine(container, step.type, step.text);
    container.scrollTop = container.scrollHeight;
  }
}

function appendLine(container, type, text) {
  const span = document.createElement('span');
  span.className = TYPE_CLASS[type] || 'log-info';
  span.textContent = text + '\n';
  container.appendChild(span);
}
