document.addEventListener("DOMContentLoaded", function () {
  // Elementos del DOM
  const searchInput = document.getElementById("searchInput");
  const searchIcon = document.getElementById("searchIcon");
  const usersTableContainer = document.getElementById("usersTableContainer");
  const noSearchResults = document.getElementById("noSearchResults");
  const searchResults = document.getElementById("searchResults");
  const searchTerm = document.getElementById("searchTerm");
  const userRows = document.querySelectorAll(".user-row");
  const filtersDropdown = document.getElementById("filtersDropdown");
  const filtersMenu = document.querySelector(
    "#filtersDropdown + .dropdown-menu"
  );

  // Variables de estado
  let activeRoleFilters = new Set();

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
   * Obtiene roles únicos de los usuarios
   */
  function getUniqueRoles() {
    const roles = new Map();

    userRows.forEach((row) => {
      const roleElement = row.querySelector(".badge");
      if (roleElement) {
        const roleText = roleElement.textContent.trim();
        const cleanRoleName = roleText.replace(/^\s*\w+\s+/, "").trim();

        if (cleanRoleName && !roles.has(cleanRoleName)) {
          roles.set(cleanRoleName, roleElement.innerHTML);
        }
      }
    });

    return roles;
  }

  /**
   * Genera el menú de filtros
   */
  function generateFiltersMenu() {
    const uniqueRoles = getUniqueRoles();
    let menuHTML = `<li><h6 class="dropdown-header">Filtrar por Rol</h6></li>`;

    uniqueRoles.forEach((roleHTML, roleName) => {
      const filterId = `filter-${roleName.toLowerCase().replace(/\s+/g, "-")}`;
      menuHTML += `
        <li>
          <div class="dropdown-item-text">
            <div class="form-check">
              <input class="form-check-input role-filter" type="checkbox" id="${filterId}" value="${roleName}">
              <label class="form-check-label" for="${filterId}">
                ${roleHTML}
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
    document.querySelectorAll(".role-filter").forEach((checkbox) => {
      checkbox.addEventListener("change", function () {
        if (this.checked) {
          activeRoleFilters.add(this.value);
        } else {
          activeRoleFilters.delete(this.value);
        }
        updateFiltersDisplay();
        applyFilters();
      });
    });

    document
      .getElementById("clearFilters")
      .addEventListener("click", function (e) {
        e.preventDefault();
        activeRoleFilters.clear();
        document
          .querySelectorAll(".role-filter")
          .forEach((cb) => (cb.checked = false));
        updateFiltersDisplay();
        applyFilters();
      });
  }

  /**
   * Actualiza la visualización de los filtros
   */
  function updateFiltersDisplay() {
    const filterCount = activeRoleFilters.size;

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
   * Verifica si una fila coincide con los filtros de rol
   */
  function matchesRoleFilters(row) {
    if (activeRoleFilters.size === 0) return true;

    const roleElement = row.querySelector(".badge");
    if (!roleElement) return false;

    const roleText = roleElement.textContent.trim();
    const cleanRoleName = roleText.replace(/^\s*\w+\s+/, "").trim();

    return activeRoleFilters.has(cleanRoleName);
  }

  /**
   * Aplica búsqueda y filtros
   */
  function applyFilters() {
    const searchText = searchInput.value.toLowerCase().trim();
    let visibleCount = 0;

    // Limpiar resaltados previos
    userRows.forEach((row) => {
      row
        .querySelectorAll(
          ".searchable-username, .searchable-fullname, .searchable-email"
        )
        .forEach((el) => clearHighlight(el));
    });

    // Aplicar búsqueda + filtros
    userRows.forEach((row) => {
      const searchData = row.getAttribute("data-search").toLowerCase();
      const isSearchMatch = !searchText || searchData.includes(searchText);
      const isRoleMatch = matchesRoleFilters(row);

      if (isSearchMatch && isRoleMatch) {
        row.style.display = "";
        visibleCount++;

        // Resaltar texto de búsqueda
        if (searchText) {
          row
            .querySelectorAll(
              ".searchable-username, .searchable-fullname, .searchable-email"
            )
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
    const hasActiveFilters = activeRoleFilters.size > 0;

    if (visibleCount === 0) {
      usersTableContainer.style.display = "none";
      noSearchResults.style.display = "block";

      if (hasActiveSearch) {
        searchTerm.textContent = searchText;
      } else {
        searchTerm.textContent = "";
        document.getElementById("noResultsText").textContent =
          "No se encontraron usuarios con los filtros aplicados";
      }
    } else {
      usersTableContainer.style.display = "block";
      noSearchResults.style.display = "none";

      let resultText = "";
      if (hasActiveSearch && hasActiveFilters) {
        resultText = `Mostrando ${visibleCount} resultados (búsqueda + filtros)`;
      } else if (hasActiveSearch) {
        resultText = `Mostrando ${visibleCount} resultados de búsqueda`;
      } else if (hasActiveFilters) {
        resultText = `Mostrando ${visibleCount} usuarios filtrados`;
      } else {
        resultText = `Total: ${userRows.length} usuarios`;
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
   * Configura el modal de eliminación individual con la información del usuario
   */
  function setupDeleteModal() {
    const deleteModal = document.getElementById("deleteUserModal");
    const deleteForm = document.getElementById("deleteUserForm");
    const deleteUsernames = document.querySelectorAll(".deleteUsername");
    const deleteFullName = document.getElementById("deleteFullName");

    if (!deleteModal) return;

    // Escuchar cuando se abre el modal
    deleteModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget; // Botón que activó el modal

      if (!button) return;

      // Obtener datos del botón
      const userId = button.getAttribute("data-user-id");
      const username = button.getAttribute("data-username");
      const userFullName = button.getAttribute("data-user-name");

      // Actualizar el contenido del modal
      deleteUsernames.forEach((deleteUsername) => {
        deleteUsername.textContent = username || "Usuario";
      });

      if (deleteFullName) {
        // Limpiar nombres vacíos y mostrar mensaje apropiado
        const cleanFullName = userFullName
          ? userFullName.trim().replace(/\s+/g, " ")
          : "";
        deleteFullName.textContent = cleanFullName || "Sin nombre asignado";
      }

      // Actualizar la acción del formulario
      if (deleteForm && userId) {
        deleteForm.action = `/user/delete/${userId}`;
      }
    });

    // Limpiar el modal cuando se cierra
    deleteModal.addEventListener("hidden.bs.modal", function () {
      deleteUsernames.forEach((deleteUsername) => {
        deleteUsername.textContent = "";
      });
      if (deleteFullName) deleteFullName.textContent = "";
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
