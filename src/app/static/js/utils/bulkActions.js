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

  // Actualizar estado de los botones
  function updateBulkButtons() {
    const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
    
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
  updateBulkButtons();

  // Evento para seleccionar/deseleccionar todos
  if (selectAll) {
    selectAll.addEventListener('change', () => {
      checkboxes.forEach(cb => cb.checked = selectAll.checked);
      updateBulkButtons();
    });
  }

  // Eventos para checkboxes individuales
  checkboxes.forEach(cb => {
    cb.addEventListener('change', () => {
      // Actualizar estado de "seleccionar todos"
      if (selectAll) {
        selectAll.checked = Array.from(checkboxes).every(cb => cb.checked);
      }
      updateBulkButtons();
    });
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