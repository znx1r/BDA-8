// ── Autocomplete helpers ───────────────────────────────────────────────────
function renderList(items, listId, hiddenId, queryId, labelFn, valueFn) {
  const list = document.getElementById(listId);
  list.innerHTML = '';
  if (!items.length) { list.style.display = 'none'; return; }
  items.slice(0, 8).forEach(item => {
    const div = document.createElement('div');
    div.className = 'autocomplete-item';
    div.innerHTML = labelFn(item);
    div.onclick = () => {
      document.getElementById(hiddenId).value = valueFn(item);
      document.getElementById(queryId).value  = item[1];
      list.style.display = 'none';
    };
    list.appendChild(div);
  });
  list.style.display = 'block';
}

// ── Matrícula simple ──────────────────────────────────────────────────────
function filterAlumnos(q) {
  const ql = q.toLowerCase();
  document.getElementById('m-alumno-id').value = '';
  const matches = ALUMNOS_DATA.filter(a => a[1].toLowerCase().includes(ql) || a[2].toLowerCase().includes(ql));
  renderList(
    matches, 'm-alumno-list', 'm-alumno-id', 'm-alumno-q',
    a => `${a[1]} <span>#${a[0].slice(0,8)}…</span>`,
    a => a[0]
  );
}

function filterCursos(q) {
  const ql = q.toLowerCase();
  document.getElementById('m-curso-id').value = '';
  const matches = CURSOS_DATA.filter(c => c[1].toLowerCase().includes(ql));
  renderList(
    matches, 'm-curso-list', 'm-curso-id', 'm-curso-q',
    c => c[1],
    c => c[0]
  );
}

document.addEventListener('click', e => {
  if (!e.target.closest('#m-alumno-q') && !e.target.closest('#m-alumno-list'))
    document.getElementById('m-alumno-list').style.display = 'none';
  if (!e.target.closest('#m-curso-q') && !e.target.closest('#m-curso-list'))
    document.getElementById('m-curso-list').style.display = 'none';
  if (!e.target.closest('#et-alumno-q') && !e.target.closest('#et-alumno-list'))
    document.getElementById('et-alumno-list').style.display = 'none';
  if (!e.target.closest('#et-curso-q') && !e.target.closest('#et-curso-list'))
    document.getElementById('et-curso-list').style.display = 'none';
});

async function deleteMatricula(alumnoId, cursoId) {
  const fd = new FormData();
  fd.append('alumno_id', alumnoId);
  fd.append('curso_id',  cursoId);
  const res  = await fetch('/matriculas/delete', { method: 'POST', body: fd });
  const json = await res.json();
  if (json.ok) {
    showToast(json.message);
    setTimeout(() => location.reload(), 1200);
  } else {
    showToast(json.error, true);
  }
  closeModal('modal-confirmar-eliminar');
}

let _pendingDeleteAlumnoId = null;
let _pendingDeleteCursoId  = null;

function confirmDeleteMatricula(alumnoId, cursoId, alumnoNombre, cursoNombre) {
  _pendingDeleteAlumnoId = alumnoId;
  _pendingDeleteCursoId  = cursoId;
  document.getElementById('confirm-delete-msg').textContent =
    `¿Eliminar la matrícula de "${alumnoNombre}" en "${cursoNombre}"?`;
  openModal('modal-confirmar-eliminar');
}

function executeDeleteMatricula() {
  deleteMatricula(_pendingDeleteAlumnoId, _pendingDeleteCursoId);
}

async function submitMatricula(e) {
  e.preventDefault();
  document.querySelectorAll('#form-matricula .form-error').forEach(el => el.style.display = 'none');

  const res  = await fetch('/matriculas/new', { method: 'POST', body: new FormData(e.target) });
  const json = await res.json();

  if (json.ok) {
    closeModal('modal-nueva-matricula');
    showToast(json.message);
    e.target.reset();
    document.getElementById('m-alumno-q').value = '';
    document.getElementById('m-curso-q').value  = '';
    setTimeout(() => location.reload(), 1200);
  } else {
    const errEl = document.getElementById('m-' + (json.field || 'alumno_id') + '-err');
    if (errEl) { errEl.textContent = json.error; errEl.style.display = 'block'; }
    else        { showToast(json.error, true); }
  }
}

// ── Matriculación transaccional ───────────────────────────────────────────
// ALUMNOS_DATA[i] = [id, nombre, email, saldo]
// CURSOS_DATA[i]  = [id, nombre, profesor, precio, max_alumnos]

let _etSelectedAlumno = null;
let _etSelectedCurso  = null;

function etFilterAlumnos(q) {
  _etSelectedAlumno = null;
  document.getElementById('et-alumno-id').value = '';
  const ql = q.toLowerCase();
  const matches = ALUMNOS_DATA.filter(a => a[1].toLowerCase().includes(ql) || a[2].toLowerCase().includes(ql));
  renderList(
    matches, 'et-alumno-list', 'et-alumno-id', 'et-alumno-q',
    a => `${a[1]} <span>${parseFloat(a[3]).toFixed(2)} €</span>`,
    a => a[0]
  );
  const list = document.getElementById('et-alumno-list');
  list.querySelectorAll('.autocomplete-item').forEach((div, i) => {
    div.onclick = () => {
      _etSelectedAlumno = matches[i];
      document.getElementById('et-alumno-id').value = matches[i][0];
      document.getElementById('et-alumno-q').value  = matches[i][1];
      list.style.display = 'none';
      etUpdatePreview();
    };
  });
}

function etFilterCursos(q) {
  _etSelectedCurso = null;
  document.getElementById('et-curso-id').value = '';
  const ql = q.toLowerCase();
  const matches = CURSOS_DATA.filter(c => c[1].toLowerCase().includes(ql));
  renderList(
    matches, 'et-curso-list', 'et-curso-id', 'et-curso-q',
    c => `${c[1]} <span>${parseFloat(c[3]).toFixed(2)} €</span>`,
    c => c[0]
  );
  const list = document.getElementById('et-curso-list');
  list.querySelectorAll('.autocomplete-item').forEach((div, i) => {
    div.onclick = () => {
      _etSelectedCurso = matches[i];
      document.getElementById('et-curso-id').value = matches[i][0];
      document.getElementById('et-curso-q').value  = matches[i][1];
      list.style.display = 'none';
      etUpdatePreview();
    };
  });
}

function etUpdatePreview() {
  const preview = document.getElementById('enroll-preview');
  const warn    = document.getElementById('prev-warning');
  if (!_etSelectedAlumno || !_etSelectedCurso) { preview.style.display = 'none'; return; }

  const saldo  = parseFloat(_etSelectedAlumno[3]);
  const precio = parseFloat(_etSelectedCurso[3]);
  const maxA   = parseInt(_etSelectedCurso[4]);

  document.getElementById('prev-saldo').textContent  = saldo.toFixed(2) + ' €';
  document.getElementById('prev-precio').textContent = precio.toFixed(2) + ' €';
  document.getElementById('prev-plazas').textContent = '—/' + maxA;
  document.getElementById('prev-saldo').style.color  = saldo >= precio ? '#1a7a4a' : '#b91c1c';

  const warnings = [];
  if (saldo < precio) warnings.push(`Saldo insuficiente: ${saldo.toFixed(2)} € < ${precio.toFixed(2)} €`);

  warn.style.display = warnings.length ? 'block' : 'none';
  warn.textContent   = warnings.join(' · ');
  preview.style.display = 'block';
}

async function runEnrollTransaction() {
  const alumnoId = document.getElementById('et-alumno-id').value;
  const cursoId  = document.getElementById('et-curso-id').value;

  ['et-alumno-err', 'et-curso-err'].forEach(id => {
    const el = document.getElementById(id); if (el) el.style.display = 'none';
  });

  if (!alumnoId) {
    const el = document.getElementById('et-alumno-err');
    el.textContent = 'Selecciona un alumno.'; el.style.display = 'block'; return;
  }
  if (!cursoId) {
    const el = document.getElementById('et-curso-err');
    el.textContent = 'Selecciona una asignatura.'; el.style.display = 'block'; return;
  }

  document.getElementById('enroll-form-section').style.display = 'none';
  document.getElementById('enroll-log-section').style.display  = 'block';
  const logEl = document.getElementById('enroll-tx-log');
  logEl.innerHTML = '<div class="tx-log-line info">Conectando con PostgreSQL…</div>';

  const fd = new FormData();
  fd.append('alumno_id', alumnoId);
  fd.append('curso_id',  cursoId);

  const res  = await fetch('/matriculas/enroll', { method: 'POST', body: fd });
  const json = await res.json();

  logEl.innerHTML = '';
  const steps = json.steps || [];
  steps.forEach((s, i) => {
    setTimeout(() => {
      const div = document.createElement('div');
      div.className = `tx-log-line ${s.type}`;
      div.textContent = s.text;
      logEl.appendChild(div);
      logEl.scrollTop = logEl.scrollHeight;
    }, i * 130);
  });

  setTimeout(() => {
    const card = document.getElementById('enroll-result-card');
    card.style.display = 'block';
    if (json.ok) {
      card.style.cssText = 'display:block;padding:16px;border-radius:8px;background:#e6f9f0;border:1px solid #a3d9be;color:#1a7a4a;';
      card.innerHTML = `
        <strong style="font-family:var(--font-secondary);font-size:13px;">✓ COMMIT — Matrícula registrada correctamente</strong>
        <div style="font-family:var(--font-secondary);font-size:12px;margin-top:10px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">
          <div><div style="opacity:.7;margin-bottom:2px;">Alumno</div><strong>${json.alumno}</strong></div>
          <div><div style="opacity:.7;margin-bottom:2px;">Asignatura</div><strong>${json.curso}</strong></div>
          <div><div style="opacity:.7;margin-bottom:2px;">Saldo anterior → nuevo</div><strong>${json.saldo_anterior.toFixed(2)} € → ${json.saldo_nuevo.toFixed(2)} €</strong></div>
        </div>`;
    } else {
      card.style.cssText = 'display:block;padding:16px;border-radius:8px;background:#fdecea;border:1px solid #f5b4b4;color:#b91c1c;';
      card.innerHTML = `<strong style="font-family:var(--font-secondary);font-size:13px;">✗ ROLLBACK — Ningún dato fue modificado</strong>`;
    }
    document.getElementById('btn-enroll-again').style.display = 'inline-flex';
    if (json.ok) setTimeout(() => location.reload(), 4500);
  }, steps.length * 130 + 350);
}

function resetEnrollModal() {
  closeModal('modal-enroll-tx');
  setTimeout(resetEnrollForm, 300);
}

function resetEnrollForm() {
  document.getElementById('enroll-form-section').style.display = 'block';
  document.getElementById('enroll-log-section').style.display  = 'none';
  document.getElementById('enroll-tx-log').innerHTML = '';
  const card = document.getElementById('enroll-result-card');
  if (card) { card.style.display = 'none'; card.innerHTML = ''; }
  const again = document.getElementById('btn-enroll-again');
  if (again) again.style.display = 'none';
  document.getElementById('et-alumno-q').value  = '';
  document.getElementById('et-alumno-id').value = '';
  document.getElementById('et-curso-q').value   = '';
  document.getElementById('et-curso-id').value  = '';
  document.getElementById('enroll-preview').style.display = 'none';
  _etSelectedAlumno = null;
  _etSelectedCurso  = null;
  openModal('modal-enroll-tx');
}
