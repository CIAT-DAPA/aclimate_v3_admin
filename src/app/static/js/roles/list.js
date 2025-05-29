document.addEventListener("DOMContentLoaded", function () {
  // Manejar envío del formulario del modal
  const addRoleForm = document.querySelector("#addRoleModal form");
  if (addRoleForm) {
    addRoleForm.addEventListener("submit", function (e) {
      const checkedModules = document.querySelectorAll(
        '#addRoleModal input[name="modules"]:checked'
      );
      if (checkedModules.length === 0) {
        e.preventDefault();
        alert("Debe seleccionar al menos un módulo para el rol");
        return false;
      }
    });
  }

  // Auto-cerrar alertas después de 5 segundos
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(function (alert) {
    if (
      alert.classList.contains("alert-success") ||
      alert.classList.contains("alert-warning")
    ) {
      setTimeout(function () {
        alert.style.transition = "opacity 0.5s";
        alert.style.opacity = "0";
        setTimeout(function () {
          alert.remove();
        }, 500);
      }, 5000);
    }
  });
});
