// static/js/bulkActions.js
export function setupBulkActions(config = {}) {
  // Configuración predeterminada
  const defaultConfig = {
    selectAllId: 'select-all',
    rowCheckboxClass: 'select-row',
    disableBtnId: 'bulk-disable',
    recoverBtnId: 'bulk-recover',
    formId: 'bulk-action-form',
    actionInputId: 'bulk-action-hidden',
    visibleClass: 'visible-action' // Clase para manejar visibilidad
  };

  // Combinar configuraciones
  const { 
    selectAllId, 
    rowCheckboxClass, 
    disableBtnId, 
    recoverBtnId,
    formId,
    actionInputId,
    visibleClass
  } = { ...defaultConfig, ...config };

  // Obtener elementos
  const selectAll = document.getElementById(selectAllId);
  const checkboxes = document.querySelectorAll(`.${rowCheckboxClass}`);
  const bulkDisable = document.getElementById(disableBtnId);
  const bulkRecover = document.getElementById(recoverBtnId);
  const form = document.getElementById(formId);
  const actionInput = document.getElementById(actionInputId);

  // Salir si faltan elementos esenciales
  if (!selectAll || !checkboxes.length || !bulkDisable || !bulkRecover || !form || !actionInput) {
    console.warn('Elementos de bulk actions no encontrados');
    return;
  }

  function getVisibleCheckboxes() {
    return Array.from(checkboxes).filter(cb => {
      const row = cb.closest('tr');
      if (!row) {
        return false;
      }
      return getComputedStyle(row).display !== 'none';
    });
  }

  // Actualizar estado de los botones y seleccionar todo
  function updateSelectionState() {
    const visibleCheckboxes = getVisibleCheckboxes();
    const anyChecked = visibleCheckboxes.some(cb => cb.checked);
    const allChecked = visibleCheckboxes.length > 0 && visibleCheckboxes.every(cb => cb.checked);

    if (selectAll) {
      selectAll.checked = allChecked;
      selectAll.indeterminate = anyChecked && !allChecked;
      selectAll.disabled = visibleCheckboxes.length === 0;
    }

    // Usamos clases para manejar visibilidad
    if (anyChecked) {
      bulkDisable.classList.add(visibleClass);
      bulkRecover.classList.add(visibleClass);
    } else {
      bulkDisable.classList.remove(visibleClass);
      bulkRecover.classList.remove(visibleClass);
    }

    bulkDisable.disabled = !anyChecked;
    bulkRecover.disabled = !anyChecked;
  }

  // Inicializar
  updateSelectionState();

  // Evento para seleccionar/deseleccionar todos
  if (selectAll) {
    selectAll.addEventListener('change', () => {
      getVisibleCheckboxes().forEach(cb => cb.checked = selectAll.checked);
      updateSelectionState();
    });
  }

  // Eventos para checkboxes individuales
  checkboxes.forEach(cb => {
    cb.addEventListener('change', () => {
      updateSelectionState();
    });
  });

  document.addEventListener('bulk-selection-refresh', () => {
    updateSelectionState();
  });

  // Deshabilitar botones al enviar
  form.addEventListener('submit', () => {
    bulkDisable.disabled = true;
    bulkRecover.disabled = true;
  });

  // Configurar acciones
  bulkDisable.addEventListener('click', () => {
    actionInput.value = 'disable';
    form.submit();
  });

  bulkRecover.addEventListener('click', () => {
    actionInput.value = 'recover';
    form.submit();
  });
}