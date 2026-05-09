let _pendingDeleteId = null;

function confirmDeleteAlumno(id, nombre) {
  _pendingDeleteId = id;
  document.getElementById('confirm-delete-msg').textContent = `¿Seguro que deseas eliminar a "${nombre}"?`;
  openModal('modal-confirmar-eliminar');
}

function executeDeleteAlumno() {
  deleteAlumno(_pendingDeleteId);
}

async function deleteAlumno(id) {
  const res  = await fetch(`/alumnos/delete/${id}`, { method: 'POST' });
  const json = await res.json();
  if (json.ok) {
    showToast(json.message);
    setTimeout(() => location.reload(), 1200);
  } else {
    showToast(json.error, true);
  }
  closeModal('modal-confirmar-eliminar');
}

async function submitAlumno(e) {
  e.preventDefault();
  document.querySelectorAll('#form-alumno .form-error').forEach(el => el.style.display = 'none');

  const res  = await fetch('/alumnos/new', { method: 'POST', body: new FormData(e.target) });
  const json = await res.json();

  if (json.ok) {
    closeModal('modal-nuevo-alumno');
    showToast(json.message);
    e.target.reset();
    setTimeout(() => location.reload(), 1200);
  } else {
    const errEl = document.getElementById('a-' + (json.field || 'nombre') + '-err');
    if (errEl) { errEl.textContent = json.error; errEl.style.display = 'block'; }
    else        { showToast(json.error, true); }
  }
}

// Recargar saldo — lista
function openRecharge(id, nombre, saldoActual) {
  document.getElementById('r-alumno-id').value      = id;
  document.getElementById('r-alumno-nombre').textContent = nombre;
  document.getElementById('r-saldo-actual').textContent  = `Saldo actual: ${saldoActual} €`;
  document.getElementById('r-cantidad').value = '';
  const err = document.getElementById('r-cantidad-err');
  if (err) { err.style.display = 'none'; }
  openModal('modal-recharge');
}

async function submitRecharge(e) {
  e.preventDefault();
  const err = document.getElementById('r-cantidad-err');
  if (err) err.style.display = 'none';

  const res  = await fetch('/alumnos/recharge', { method: 'POST', body: new FormData(e.target) });
  const json = await res.json();

  if (json.ok) {
    closeModal('modal-recharge');
    showToast(json.message);
    setTimeout(() => location.reload(), 1200);
  } else {
    if (err) { err.textContent = json.error; err.style.display = 'block'; }
    else     { showToast(json.error, true); }
  }
}

// Recargar saldo — detail page
function openRechargeDetail(id, nombre, saldoActual) {
  openModal('modal-recharge');
}

async function submitRechargeDetail(e) {
  e.preventDefault();
  const err = document.getElementById('r-cantidad-err');
  if (err) err.style.display = 'none';

  const res  = await fetch('/alumnos/recharge', { method: 'POST', body: new FormData(e.target) });
  const json = await res.json();

  if (json.ok) {
    closeModal('modal-recharge');
    showToast(json.message);
    // Update saldo displayed on detail page
    if (json.saldo !== null && json.saldo !== undefined) {
      const el = document.getElementById('detail-saldo');
      if (el) {
        el.textContent = json.saldo.toFixed(2) + ' €';
        el.style.color = json.saldo >= 100 ? '#1a7a4a' : '#b91c1c';
      }
      const sa = document.getElementById('r-saldo-actual');
      if (sa) sa.textContent = json.saldo.toFixed(2) + ' €';
    }
  } else {
    if (err) { err.textContent = json.error; err.style.display = 'block'; }
    else     { showToast(json.error, true); }
  }
}
