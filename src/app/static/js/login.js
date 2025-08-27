document.addEventListener("DOMContentLoaded", function () {
  const emailField = document.getElementById("email");
  const passwordField = document.getElementById("password");

  // Función para validar email
  function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Función para remover clases de error y mensajes
  function removeError(field) {
    field.classList.remove("is-invalid");
    const errorDiv = field.parentNode.querySelector(".invalid-feedback");
    if (errorDiv) {
      errorDiv.style.display = "none";
    }
  }

  // Función para agregar clases de error y mensajes
  function addError(field, message) {
    field.classList.add("is-invalid");
    let errorDiv = field.parentNode.querySelector(".invalid-feedback");
    if (!errorDiv) {
      errorDiv = document.createElement("div");
      errorDiv.className = "invalid-feedback";
      field.parentNode.appendChild(errorDiv);
    }
    errorDiv.innerHTML = "<small>" + message + "</small>";
    errorDiv.style.display = "block";
  }

  // Validación en tiempo real para email
  emailField.addEventListener("input", function () {
    const email = this.value.trim();

    if (email === "") {
      removeError(this);
    } else if (!validateEmail(email)) {
      addError(this, "Ingresa un email válido");
    } else {
      removeError(this);
    }
  });

  // Validación en tiempo real para password
  passwordField.addEventListener("input", function () {
    const password = this.value;

    if (password === "") {
      removeError(this);
    } else {
      removeError(this);
    }
  });

  // Validación al perder el foco
  emailField.addEventListener("blur", function () {
    const email = this.value.trim();

    if (email === "") {
      addError(this, "El email es requerido");
    } else if (!validateEmail(email)) {
      addError(this, "Ingresa un email válido");
    }
  });

  passwordField.addEventListener("blur", function () {
    const password = this.value;

    if (password === "") {
      addError(this, "La contraseña es requerida");
    }
  });

  // Prevenir envío del formulario si hay errores
  const form = document.querySelector("form");
  form.addEventListener("submit", function (e) {
    let hasErrors = false;

    // Validar email
    const email = emailField.value.trim();
    if (email === "") {
      addError(emailField, "El email es requerido");
      hasErrors = true;
    } else if (!validateEmail(email)) {
      addError(emailField, "Ingresa un email válido");
      hasErrors = true;
    }

    // Validar password
    const password = passwordField.value;
    if (password === "") {
      addError(passwordField, "La contraseña es requerida");
      hasErrors = true;
    }

    if (hasErrors) {
      e.preventDefault();
    }
  });
});
