document.addEventListener("DOMContentLoaded", function () {
  // Elementos del DOM
  const searchInput = document.getElementById("searchInput");
  const searchIcon = document.getElementById("searchIcon");
  const rolesTableContainer = document.getElementById("rolesTableContainer");
  const noSearchResults = document.getElementById("noSearchResults");
  const searchResults = document.getElementById("searchResults");
  const searchTerm = document.getElementById("searchTerm");
  const roleRows = document.querySelectorAll(".role-row");
  const filtersDropdown = document.getElementById("filtersDropdown");
  const filtersMenu = document.querySelector(
    "#filtersDropdown + .dropdown-menu"
  );

  // Variables de estado
  let activeModuleFilters = new Set();

  /**
   * Actualiza el ícono de búsqueda según el contenido del input
   */
  function updateSearchIcon() {
    if (searchInput.value.trim()) {
      searchIcon.className = "fas fa-times search-icon clear-icon";
      searchIcon.title = "Limpiar búsqueda";
    } else {
      searchIcon.className = "fas fa-search search-icon";
      searchIcon.title = "Buscar";
    }
  }

  /**
   * Maneja el clic en el ícono de búsqueda
   */
  function handleSearchIconClick() {
    if (searchInput.value.trim()) {
      clearSearch();
    } else {
      searchInput.focus();
    }
  }

  /**
   * Resalta texto coincidente en los resultados
   */
  function highlightText(element, searchText) {
    const regex = new RegExp(`(${searchText})`, "gi");
    element.innerHTML = element.textContent.replace(
      regex,
      '<mark class="bg-warning">$1</mark>'
    );
  }

  /**
   * Elimina el resaltado previo
   */
  function clearHighlight(element) {
    element.innerHTML = element.textContent;
  }

  /**
   * Obtiene los módulos únicos y su información
   */
  function getUniqueModules() {
    const modules = new Map();
    
    // Definir módulos con sus iconos y nombres
    const moduleInfo = {
      'geographic': {
        name: 'Módulo Geográfico',
        icon: '<i class="fas fa-globe me-2"></i>',
        description: 'Gestión geográfica'
      },
      'climate_data': {
        name: 'Datos Climáticos', 
        icon: '<i class="fas fa-cloud-sun me-2"></i>',
        description: 'Datos climáticos'
      },
      'crop_data': {
        name: 'Datos de Cultivos',
        icon: '<i class="fas fa-seedling me-2"></i>', 
        description: 'Datos de cultivos'
      },
      'user_management': {
        name: 'Gestión de Usuarios',
        icon: '<i class="fas fa-users me-2"></i>',
        description: 'Administración de usuarios'
      }
    };

    // Agregar todos los módulos disponibles
    Object.keys(moduleInfo).forEach(moduleKey => {
      modules.set(moduleKey, moduleInfo[moduleKey]);
    });

    return modules;
  }

  /**
   * Verifica si un rol tiene acceso a un módulo específico
   */
  function roleHasModuleAccess(row, moduleKey) {
    // Mapear módulos a sus columnas correspondientes
    const moduleColumnMap = {
      'geographic': 3,      // Columna 4 (0-indexed = 3)
      'climate_data': 4,    // Columna 5 (0-indexed = 4) 
      'crop_data': 5,       // Columna 6 (0-indexed = 5)
      'user_management': 6  // Columna 7 (0-indexed = 6)
    };

    const columnIndex = moduleColumnMap[moduleKey];
    if (columnIndex === undefined) return false;

    const cells = row.querySelectorAll('td');
    if (cells.length <= columnIndex) return false;

    const moduleCell = cells[columnIndex];
    const accessIndicator = moduleCell.querySelector('.access-indicator');
    
    return accessIndicator && accessIndicator.classList.contains('access-granted');
  }

  /**
   * Genera el menú de filtros por módulos
   */
  function generateFiltersMenu() {
    const uniqueModules = getUniqueModules();
    let menuHTML = `<li><h6 class="dropdown-header">Filtrar por Acceso a Módulos</h6></li>`;

    uniqueModules.forEach((moduleInfo, moduleKey) => {
      const filterId = `filter-${moduleKey}`;
      menuHTML += `
        <li>
          <div class="dropdown-item-text">
            <div class="form-check">
              <input class="form-check-input module-filter" type="checkbox" id="${filterId}" value="${moduleKey}">
              <label class="form-check-label" for="${filterId}">
                ${moduleInfo.icon}${moduleInfo.name}
              </label>
            </div>
          </div>
        </li>
      `;
    });

    menuHTML += `
      <li><hr class="dropdown-divider"></li>
      <li>
        <a class="dropdown-item text-primary" href="#" id="clearFilters">
          <i class="fas fa-times me-2"></i>Limpiar filtros
        </a>
      </li>
    `;

    filtersMenu.innerHTML = menuHTML;

    // Inicializar eventos de los filtros
    document.querySelectorAll(".module-filter").forEach((checkbox) => {
      checkbox.addEventListener("change", function () {
        if (this.checked) {
          activeModuleFilters.add(this.value);
        } else {
          activeModuleFilters.delete(this.value);
        }
        updateFiltersDisplay();
        applyFilters();
      });
    });

    document
      .getElementById("clearFilters")
      .addEventListener("click", function (e) {
        e.preventDefault();
        activeModuleFilters.clear();
        document
          .querySelectorAll(".module-filter")
          .forEach((cb) => (cb.checked = false));
        updateFiltersDisplay();
        applyFilters();
      });
  }

  /**
   * Actualiza la visualización de los filtros
   */
  function updateFiltersDisplay() {
    const filterCount = activeModuleFilters.size;

    if (filterCount > 0) {
      filtersDropdown.classList.add("btn-primary");
      filtersDropdown.style.setProperty("color", "#fff", "important");
      filtersDropdown.innerHTML = `<i class="fas fa-filter me-2"></i>Filtros (${filterCount})`;
    } else {
      filtersDropdown.classList.remove("btn-primary");
      filtersDropdown.style.removeProperty("color");
      filtersDropdown.innerHTML = '<i class="fas fa-filter"></i> Filtros';
    }
  }

  /**
   * Verifica si una fila coincide con los filtros de módulos
   */
  function matchesModuleFilters(row) {
    if (activeModuleFilters.size === 0) return true;

    // El rol debe tener acceso a TODOS los módulos seleccionados (AND logic)
    // Si quieres OR logic, cambia 'every' por 'some'
    return Array.from(activeModuleFilters).every(moduleKey => 
      roleHasModuleAccess(row, moduleKey)
    );
  }

  /**
   * Aplica búsqueda y filtros
   */
  function applyFilters() {
    const searchText = searchInput.value.toLowerCase().trim();
    let visibleCount = 0;

    // Limpiar resaltados previos
    roleRows.forEach((row) => {
      row
        .querySelectorAll(".searchable-rolename, .searchable-description")
        .forEach((el) => clearHighlight(el));
    });

    // Aplicar búsqueda + filtros
    roleRows.forEach((row) => {
      const searchData = row.getAttribute("data-search").toLowerCase();
      const isSearchMatch = !searchText || searchData.includes(searchText);
      const isModuleMatch = matchesModuleFilters(row);

      if (isSearchMatch && isModuleMatch) {
        row.style.display = "";
        visibleCount++;

        // Resaltar texto de búsqueda
        if (searchText) {
          row
            .querySelectorAll(".searchable-rolename, .searchable-description")
            .forEach((el) => highlightText(el, searchText));
        }
      } else {
        row.style.display = "none";
      }
    });

    updateSearchResults(searchText, visibleCount);
  }

  /**
   * Actualiza los resultados de búsqueda
   */
  function updateSearchResults(searchText, visibleCount) {
    const hasActiveSearch = searchText.length > 0;
    const hasActiveFilters = activeModuleFilters.size > 0;

    if (visibleCount === 0) {
      rolesTableContainer.style.display = "none";
      noSearchResults.style.display = "block";

      if (hasActiveSearch) {
        searchTerm.textContent = searchText;
        document.getElementById("noResultsText").textContent = 
          "No se encontraron roles que coincidan con la búsqueda";
      } else if (hasActiveFilters) {
        searchTerm.textContent = "";
        document.getElementById("noResultsText").textContent =
          "No se encontraron roles con acceso a los módulos seleccionados";
      } else {
        searchTerm.textContent = "";
        document.getElementById("noResultsText").textContent =
          "No se encontraron roles";
      }
    } else {
      rolesTableContainer.style.display = "block";
      noSearchResults.style.display = "none";

      let resultText = "";
      if (hasActiveSearch && hasActiveFilters) {
        resultText = `Mostrando ${visibleCount} resultados (búsqueda + filtros)`;
      } else if (hasActiveSearch) {
        resultText = `Mostrando ${visibleCount} resultados de búsqueda`;
      } else if (hasActiveFilters) {
        resultText = `Mostrando ${visibleCount} roles con acceso a módulos seleccionados`;
      } else {
        resultText = `Total: ${roleRows.length} roles`;
      }

      searchResults.textContent = resultText;
    }
  }

  /**
   * Limpia la búsqueda
   */
  function clearSearch() {
    searchInput.value = "";
    applyFilters();
    searchInput.focus();
  }

  /**
   * Configura el modal de eliminación individual con la información del rol
   */
  function setupDeleteModal() {
    const deleteModal = document.getElementById("deleteRolModal");
    const deleteForm = document.getElementById("deleteRoleForm");
    const deleteRoleNames = document.querySelectorAll(".deleteRolName");
    const deleteRoleDescription = document.getElementById(
      "deleteRolDescription"
    );

    if (!deleteModal) return;

    // Escuchar cuando se abre el modal
    deleteModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget; // Botón que activó el modal

      if (!button) return;

      // Obtener datos del botón
      const roleId = button.getAttribute("data-role-id");
      const roleName = button.getAttribute("data-rolename");
      const roleDescription = button.getAttribute("data-role-description");

      // Actualizar el contenido del modal
      deleteRoleNames.forEach((deleteRoleName) => {
        deleteRoleName.textContent = roleName || "Rol";
      });

      if (deleteRoleDescription) {
        // Limpiar nombres vacíos y mostrar mensaje apropiado
        const cleanRoleDescription = roleDescription
          ? roleDescription.trim().replace(/\s+/g, " ")
          : "";
        deleteRoleDescription.textContent =
          cleanRoleDescription || "Sin descripción asignada";
      }

      // Actualizar la acción del formulario
      if (deleteForm && roleId) {
        deleteForm.action = `/role/delete/${roleId}`;
      }
    });

    // Limpiar el modal cuando se cierra
    deleteModal.addEventListener("hidden.bs.modal", function () {
      deleteRoleNames.forEach((deleteRoleName) => {
        deleteRoleName.textContent = "";
      });
      if (deleteRoleDescription) deleteRoleDescription.textContent = "";
      if (deleteForm) deleteForm.action = "";
    });
  }

  /**
   * Inicializa el sistema
   */
  function init() {
    // Búsqueda
    searchInput.addEventListener("input", applyFilters);
    searchIcon.addEventListener("click", handleSearchIconClick);
    searchInput.addEventListener(
      "keydown",
      (e) => e.key === "Escape" && clearSearch()
    );
    searchInput.addEventListener("input", updateSearchIcon);
    updateSearchIcon();

    // Filtros
    generateFiltersMenu();
    updateFiltersDisplay();

    // Modales de eliminación
    setupDeleteModal();

    // Estado inicial
    applyFilters();
  }

  init();
});