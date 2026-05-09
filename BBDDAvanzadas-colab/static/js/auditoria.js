let _deleteId = null;

function confirmDeleteAuditoria(id) {
    _deleteId = id;
    openModal('modal-confirmar-eliminar');
}

function executeDelete() {
    if (!_deleteId) return;
    fetch(`/auditoria/delete/${_deleteId}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            closeModal('modal-confirmar-eliminar');
            if (data.ok) {
                showToast(data.message, false);
                setTimeout(() => location.reload(), 900);
            } else {
                showToast(data.error, true);
            }
        });
}

function confirmLimpiarTodo() {
    openModal('modal-limpiar-todo');
}

function executeLimpiar() {
    fetch('/auditoria/delete-all', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            closeModal('modal-limpiar-todo');
            if (data.ok) {
                showToast(data.message, false);
                setTimeout(() => location.reload(), 900);
            } else {
                showToast(data.error, true);
            }
        });
}
