// Auto-dismiss alerts
var autoDismissAlerts = document.querySelectorAll(".auto-dismiss-alert");
autoDismissAlerts.forEach(function (alert) {
  setTimeout(function () {
    var bsAlert = new bootstrap.Alert(alert);
    bsAlert.close();
  }, 5000);
});

// Sidebar functionality
document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.getElementById("sidebar");
  const sidebarTrigger = document.getElementById("sidebarTrigger");
  const sidebarToggle = document.getElementById("sidebarToggle");

  // Variable para controlar si estamos manejando collapses automáticamente
  let isAutoManaging = false;

  // Función para manejar el hover del sidebar
  function handleSidebarHover() {
    if (window.innerWidth <= 1200 && window.innerWidth > 768) {
      // Hover sobre el área de trigger
      sidebarTrigger.addEventListener("mouseenter", function () {
        sidebar.classList.add("hover-active");
      });

      // Hover sobre el sidebar mismo
      sidebar.addEventListener("mouseenter", function () {
        sidebar.classList.add("hover-active");
      });

      // Mouse leave del sidebar
      sidebar.addEventListener("mouseleave", function () {
        sidebar.classList.remove("hover-active");
      });

      // Mouse leave del trigger
      sidebarTrigger.addEventListener("mouseleave", function () {
        setTimeout(() => {
          if (!sidebar.matches(":hover")) {
            sidebar.classList.remove("hover-active");
          }
        }, 100);
      });
    }
  }

  // Toggle sidebar en móviles
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", function () {
      sidebar.classList.toggle("hover-active");
    });
  }

  // Cerrar sidebar en móviles al hacer click fuera
  document.addEventListener("click", function (event) {
    if (window.innerWidth <= 768) {
      const isClickInsideSidebar = sidebar.contains(event.target);
      const isClickOnToggle =
        sidebarToggle && sidebarToggle.contains(event.target);

      if (
        !isClickInsideSidebar &&
        !isClickOnToggle &&
        sidebar.classList.contains("hover-active")
      ) {
        sidebar.classList.remove("hover-active");
      }
    }
  });

  // Función para determinar qué sección debe estar activa
  function getActiveSection() {
    const currentPath = window.location.pathname;
    const isHomePage = currentPath === "/" || currentPath === "/home";

    if (isHomePage) {
      return null; // No hay sección activa en home
    }

    // Mapeo de rutas a secciones del sidebar
    const routeSectionMap = {
      country: "geograficoSection",
      adm1: "geograficoSection",
      adm2: "geograficoSection",
      location: "geograficoSection",
      crop: "cultivosSection",
      simulation: "cultivosSection",
      parameter: "cultivosSection",
      weather: "climaSection",
      climate: "climaSection",
      user: "usuariosSection",
      role: "usuariosSection",
      source: "configuracionSection",
      data_source: "configuracionSection",
      indicator: "configurationSection",
    };

    for (const [route, section] of Object.entries(routeSectionMap)) {
      if (currentPath.includes(route)) {
        return section;
      }
    }

    return null;
  }

  // Función para manejar los collapses automáticamente
  function handleAutoCollapse() {
    const activeSection = getActiveSection();
    const allCollapses = document.querySelectorAll(".sidebar .collapse");

    isAutoManaging = true;

    allCollapses.forEach(function (collapse) {
      const shouldBeOpen = collapse.id === activeSection;
      const isCurrentlyOpen = collapse.classList.contains("show");

      // Solo manipular si realmente necesita cambiar
      if (shouldBeOpen && !isCurrentlyOpen) {
        collapse.classList.add("show");
        // Actualizar el ícono manualmente
        const header = document.querySelector(
          `[data-bs-target="#${collapse.id}"]`
        );
        const icon = header?.querySelector(".collapse-icon");
        if (icon) {
          icon.style.transform = "rotate(180deg)";
        }
      } else if (!shouldBeOpen && isCurrentlyOpen) {
        collapse.classList.remove("show");
        // Actualizar el ícono manualmente
        const header = document.querySelector(
          `[data-bs-target="#${collapse.id}"]`
        );
        const icon = header?.querySelector(".collapse-icon");
        if (icon) {
          icon.style.transform = "rotate(0deg)";
        }
      }
    });

    // Dar tiempo para que se apliquen los cambios antes de permitir interacción manual
    setTimeout(() => {
      isAutoManaging = false;
    }, 100);
  }

  // Highlight active nav link
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".sidebar .nav-link");

  navLinks.forEach(function (link) {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });

  // Manejar rotación de íconos de colapso solo para interacción manual
  const collapseElements = document.querySelectorAll(".collapse");
  collapseElements.forEach(function (collapseEl) {
    collapseEl.addEventListener("show.bs.collapse", function () {
      if (!isAutoManaging) {
        const header = document.querySelector(`[data-bs-target="#${this.id}"]`);
        const icon = header?.querySelector(".collapse-icon");
        if (icon) {
          icon.style.transform = "rotate(180deg)";
        }
      }
    });

    collapseEl.addEventListener("hide.bs.collapse", function () {
      if (!isAutoManaging) {
        const header = document.querySelector(`[data-bs-target="#${this.id}"]`);
        const icon = header?.querySelector(".collapse-icon");
        if (icon) {
          icon.style.transform = "rotate(0deg)";
        }
      }
    });
  });

  // Ejecutar auto-collapse al cargar la página
  handleAutoCollapse();

  // Inicializar hover functionality
  handleSidebarHover();

  // Re-inicializar en resize
  window.addEventListener("resize", function () {
    // Limpiar clases de hover al cambiar tamaño
    sidebar.classList.remove("hover-active");
    handleSidebarHover();
  });
});
