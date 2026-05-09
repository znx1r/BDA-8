let _pendingDeleteId = null;

function confirmDeleteCurso(id, nombre) {
  _pendingDeleteId = id;
  document.getElementById('confirm-delete-msg').textContent = `¿Seguro que deseas eliminar "${nombre}"?`;
  openModal('modal-confirmar-eliminar');
}

function executeDeleteCurso() {
  deleteCurso(_pendingDeleteId);
}

async function deleteCurso(id) {
  const res  = await fetch(`/asignaturas/delete/${id}`, { method: 'POST' });
  const json = await res.json();
  if (json.ok) {
    showToast(json.message);
    setTimeout(() => location.reload(), 1200);
  } else {
    showToast(json.error, true);
  }
  closeModal('modal-confirmar-eliminar');
}

async function submitCurso(e) {
  e.preventDefault();
  document.querySelectorAll('#form-curso .form-error').forEach(el => el.style.display = 'none');

  const res  = await fetch('/asignaturas/new', { method: 'POST', body: new FormData(e.target) });
  const json = await res.json();

  if (json.ok) {
    closeModal('modal-nuevo-curso');
    showToast(json.message);
    e.target.reset();
    setTimeout(() => location.reload(), 1200);
  } else {
    const errEl = document.getElementById('c-' + (json.field || 'nombre') + '-err');
    if (errEl) { errEl.textContent = json.error; errEl.style.display = 'block'; }
    else        { showToast(json.error, true); }
  }
}

function openEditCurso(id, nombre, precio, maxAlumnos, nombreEn) {
  const idEl      = document.getElementById('ec-id');
  const nombreEnEl = document.getElementById('ec-nombre-en');
  const precioEl  = document.getElementById('ec-precio');
  const maxEl     = document.getElementById('ec-max');
  if (idEl)       idEl.value       = id;
  if (nombreEnEl) nombreEnEl.value = nombreEn || '';
  if (precioEl)   precioEl.value   = precio;
  if (maxEl)      maxEl.value      = maxAlumnos;
  openModal('modal-edit-curso');
}

async function submitEditCurso(e) {
  e.preventDefault();
  document.querySelectorAll('#form-edit-curso .form-error').forEach(el => el.style.display = 'none');

  const id  = document.getElementById('ec-id').value;
  const fd  = new FormData(e.target);
  const res = await fetch(`/asignaturas/update/${id}`, { method: 'POST', body: fd });
  const json = await res.json();

  if (json.ok) {
    closeModal('modal-edit-curso');
    showToast(json.message);
    setTimeout(() => location.reload(), 1200);
  } else {
    showToast(json.error, true);
  }
}
