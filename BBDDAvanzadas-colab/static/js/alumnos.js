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

// Viajar a aula (GIS)
function openViajar(alumnoId, alumnoNombre) {
  document.getElementById('v-alumno-id').value = alumnoId;
  const res = document.getElementById('v-resultado');
  if (res) res.style.display = 'none';
  const err = document.getElementById('v-curso-err');
  if (err) err.style.display = 'none';
  openModal('modal-viajar');
}

async function submitViajar(e) {
  e.preventDefault();
  const err = document.getElementById('v-curso-err');
  const res = document.getElementById('v-resultado');
  if (err) err.style.display = 'none';
  if (res) res.style.display = 'none';

  const fd     = new FormData(e.target);
  const resp   = await fetch('/alumnos/viajar', { method: 'POST', body: fd });
  const json   = await resp.json();

  if (json.ok) {
    // Actualizar coordenadas en pantalla si los elementos existen
    const lonEl = document.getElementById('alumno-lon');
    const latEl = document.getElementById('alumno-lat');
    const wktEl = document.getElementById('alumno-wkt');
    if (lonEl) lonEl.textContent = json.lon.toFixed(6);
    if (latEl) latEl.textContent = json.lat.toFixed(6);
    if (wktEl) wktEl.textContent = json.wkt;

    // Mostrar resultado del viaje
    if (res) {
      let distTxt = json.distancia_m !== null && json.distancia_m !== undefined
        ? `Distancia recorrida: <strong>${json.distancia_m.toFixed(0)} m</strong><br>`
        : '';
      res.innerHTML = `✅ <strong>¡Viaje completado!</strong><br>
        ${distTxt}
        Nueva posición: (${json.lon.toFixed(6)}, ${json.lat.toFixed(6)})<br>
        <span style="font-size:10px;color:#666;">${json.wkt}</span>`;
      res.style.display = 'block';
    }
    showToast(json.message);
    setTimeout(() => { closeModal('modal-viajar'); location.reload(); }, 2000);
  } else {
    if (err) { err.textContent = json.error; err.style.display = 'block'; }
    else     { showToast(json.error, true); }
  }
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
