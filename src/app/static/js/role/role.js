/**
 * Role Management JavaScript
 * Handles role search, filtering, modal interactions and bulk operations
 */

document.addEventListener("DOMContentLoaded", function () {
  // Elements
  const searchInput = document.getElementById("searchInput");
  const searchIcon = document.getElementById("searchIcon");
  const rolesTableBody = document.getElementById("rolesTableBody");
  const rolesTableContainer = document.getElementById("rolesTableContainer");
  const noSearchResults = document.getElementById("noSearchResults");
  const searchResults = document.getElementById("searchResults");
  const searchTerm = document.getElementById("searchTerm");
  const deleteModal = document.getElementById("deleteRoleModal");
  const filtersDropdown = document.getElementById("filtersDropdown");
  const filtersMenu = document.querySelector(
    "#filtersDropdown + .dropdown-menu"
  );

  // Bulk selection elements
  const selectAllCheckbox = document.getElementById("selectAllCheckbox");
  const bulkDeleteBtn = document.getElementById("bulkDeleteBtn");
  const selectedCount = document.getElementById("selectedCount");
  const bulkDeleteModal = document.getElementById("bulkDeleteModal");
  const bulkDeleteConfirmBtn = document.getElementById("bulkDeleteConfirmBtn");
  const bulkDeleteCancelBtn = document.getElementById("bulkDeleteCancelBtn");

  // Get all role rows and checkboxes
  const roleRows = document.querySelectorAll(".role-row");
  const roleCheckboxes = document.querySelectorAll(".role-checkbox");
  const totalRoles = roleRows.length;

  // Active filters and selections
  let activeTypeFilters = new Set();
  let selectedRoles = new Set();
  let isDeleting = false;

  /**
   * Update bulk selection UI
   */
  function updateBulkSelectionUI() {
    const selectedCount = selectedRoles.size;

    if (selectedCount > 0) {
      bulkDeleteBtn.style.display = "flex";
      document.getElementById("selectedCount").textContent = selectedCount;
      bulkDeleteBtn.title = `${
        window.translations?.deleting || "Eliminar"
      } ${selectedCount} ${
        selectedCount === 1
          ? window.translations?.role || "rol"
          : window.translations?.roles || "roles"
      } ${
        selectedCount === 1
          ? window.translations?.selected || "seleccionado"
          : window.translations?.selectedPlural || "seleccionados"
      }`;
    } else {
      bulkDeleteBtn.style.display = "none";
    }

    // Update select all checkbox state
    const visibleCheckboxes = Array.from(roleCheckboxes).filter(
      (cb) =>
        !cb.closest(".role-row").style.display ||
        cb.closest(".role-row").style.display !== "none"
    );
    const checkedVisibleCheckboxes = visibleCheckboxes.filter(
      (cb) => cb.checked
    );

    if (checkedVisibleCheckboxes.length === 0) {
      selectAllCheckbox.checked = false;
      selectAllCheckbox.indeterminate = false;
    } else if (checkedVisibleCheckboxes.length === visibleCheckboxes.length) {
      selectAllCheckbox.checked = true;
      selectAllCheckbox.indeterminate = false;
    } else {
      selectAllCheckbox.checked = false;
      selectAllCheckbox.indeterminate = true;
    }
  }

  /**
   * Handle individual checkbox change
   */
  function handleRoleCheckboxChange(event) {
    const checkbox = event.target;
    const roleId = checkbox.value;
    const roleRow = checkbox.closest(".role-row");

    if (checkbox.checked) {
      selectedRoles.add(roleId);
      roleRow.classList.add("selected");
    } else {
      selectedRoles.delete(roleId);
      roleRow.classList.remove("selected");
    }

    updateBulkSelectionUI();
  }

  /**
   * Handle select all checkbox change
   */
  function handleSelectAllChange(event) {
    const isChecked = event.target.checked;

    // Get only visible and enabled role checkboxes
    const visibleCheckboxes = Array.from(roleCheckboxes).filter((cb) => {
      const row = cb.closest(".role-row");
      return (
        (!row.style.display || row.style.display !== "none") && !cb.disabled
      );
    });

    visibleCheckboxes.forEach((checkbox) => {
      const roleId = checkbox.value;
      const roleRow = checkbox.closest(".role-row");

      checkbox.checked = isChecked;

      if (isChecked) {
        selectedRoles.add(roleId);
        roleRow.classList.add("selected");
      } else {
        selectedRoles.delete(roleId);
        roleRow.classList.remove("selected");
      }
    });

    updateBulkSelectionUI();
  }

  /**
   * Prepare bulk delete modal
   */
  function prepareBulkDeleteModal() {
    const selectedRolesList = document.getElementById("selectedRolesList");
    const bulkDeleteCount = document.getElementById("bulkDeleteCount");

    bulkDeleteCount.textContent = selectedRoles.size;

    // Generate list of selected roles
    let roleListHTML = "";
    selectedRoles.forEach((roleId) => {
      const checkbox = document.querySelector(
        `.role-checkbox[value="${roleId}"]`
      );
      if (checkbox) {
        const roleName = checkbox.dataset.rolename || "Unknown";
        const roleRow = checkbox.closest(".role-row");
        const roleDescription =
          roleRow.querySelector(".searchable-description")?.textContent ||
          "Sin descripción";

        roleListHTML += `
          <div class="selected-role-item">
            <div class="selected-role-icon">
              <i class="fas fa-user-tag"></i>
            </div>
            <div>
              <strong>${roleName}</strong>
              <br>
              <small class="text-muted">${roleDescription}</small>
            </div>
          </div>
        `;
      }
    });

    selectedRolesList.innerHTML = roleListHTML;
  }

  /**
   * Perform bulk delete operation
   */
  async function performBulkDelete() {
    if (isDeleting) return;

    isDeleting = true;
    const progressContainer = document.getElementById("bulkDeleteProgress");
    const progressBar = document.getElementById("bulkDeleteProgressBar");
    const statusText = document.getElementById("bulkDeleteStatus");

    // Show progress UI
    progressContainer.style.display = "block";
    bulkDeleteConfirmBtn.style.display = "none";
    bulkDeleteCancelBtn.disabled = true;

    const roleIds = Array.from(selectedRoles);
    const totalToDelete = roleIds.length;
    let deletedCount = 0;
    let errorCount = 0;

    statusText.textContent = window.translations?.preparing || "Preparando...";

    // Delete roles one by one
    for (let i = 0; i < roleIds.length; i++) {
      const roleId = roleIds[i];
      const checkbox = document.querySelector(
        `.role-checkbox[value="${roleId}"]`
      );
      const roleName = checkbox ? checkbox.dataset.rolename : "Unknown";

      try {
        statusText.textContent = `${
          window.translations?.deleting || "Eliminando"
        } ${roleName}...`;

        const response = await fetch(`/role/delete/${roleId}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (response.ok) {
          // Remove role row from table
          const roleRow = checkbox.closest(".role-row");
          if (roleRow) {
            roleRow.remove();
          }

          selectedRoles.delete(roleId);
          deletedCount++;

          statusText.textContent = `${
            window.translations?.deleted || "Eliminado"
          }: ${roleName}`;
        } else {
          console.error(`Error deleting role ${roleId}:`, response.statusText);
          errorCount++;
        }
      } catch (error) {
        console.error(`Error deleting role ${roleId}:`, error);
        errorCount++;
      }

      // Update progress bar
      const progress = ((i + 1) / totalToDelete) * 100;
      progressBar.style.width = `${progress}%`;

      // Small delay to show progress
      await new Promise((resolve) => setTimeout(resolve, 200));
    }

    // Show completion message
    progressBar.classList.remove("progress-bar-animated");
    statusText.textContent = `${
      window.translations?.deletionComplete || "Eliminación completada"
    }: ${deletedCount} ${
      window.translations?.rolesDeleted || "roles eliminados exitosamente"
    }${
      errorCount > 0
        ? `. ${errorCount} ${window.translations?.someErrors || "errores"}`
        : ""
    }`;

    // Update UI
    updateBulkSelectionUI();
    applyFilters(); // Refresh the view

    // Auto close modal after 2 seconds
    setTimeout(() => {
      const modal = bootstrap.Modal.getInstance(bulkDeleteModal);
      if (modal) {
        modal.hide();
      }

      // Show success message
      if (deletedCount > 0) {
        // You can add a toast notification here
      }

      // Reset modal state
      setTimeout(() => {
        progressContainer.style.display = "none";
        bulkDeleteConfirmBtn.style.display = "inline-block";
        bulkDeleteCancelBtn.disabled = false;
        progressBar.style.width = "0%";
        progressBar.classList.add("progress-bar-animated");
        isDeleting = false;
      }, 500);
    }, 2000);
  }

  /**
   * Get unique role types from current roles
   */
  function getUniqueTypes() {
    const types = new Map();

    roleRows.forEach((row) => {
      // Check if role is composite or simple
      const compositeElement = row.querySelector(".badge");
      if (compositeElement) {
        const badgeText = compositeElement.textContent.trim();
        if (badgeText.includes("Compuesto")) {
          types.set("Compuesto", "fas fa-layer-group");
        } else if (badgeText.includes("Simple")) {
          types.set("Simple", "fas fa-user-tag");
        }
      }
    });

    return types;
  }

  /**
   * Generate filters dropdown content
   */
  function generateFiltersMenu() {
    if (!filtersMenu) return;

    const uniqueTypes = getUniqueTypes();

    let menuHTML = `<li><h6 class="dropdown-header">Filtrar por Tipo</h6></li>`;

    uniqueTypes.forEach((iconClass, typeName) => {
      const filterId = `filter-${typeName.toLowerCase().replace(/\s+/g, "-")}`;
      menuHTML += `
        <li>
          <div class="dropdown-item-text">
            <div class="form-check">
              <input class="form-check-input type-filter" type="checkbox" id="${filterId}" value="${typeName}">
              <label class="form-check-label" for="${filterId}">
                <i class="${iconClass} me-2"></i>${typeName}
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
    initializeFilterEventListeners();
  }

  /**
   * Initialize filter event listeners
   */
  function initializeFilterEventListeners() {
    const typeFilterCheckboxes = document.querySelectorAll(".type-filter");
    typeFilterCheckboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", handleTypeFilterChange);
    });

    const clearFiltersBtn = document.getElementById("clearFilters");
    if (clearFiltersBtn) {
      clearFiltersBtn.addEventListener("click", function (e) {
        e.preventDefault();
        clearAllFilters();
      });
    }
  }

  /**
   * Handle type filter change
   */
  function handleTypeFilterChange(event) {
    const typeName = event.target.value;

    if (event.target.checked) {
      activeTypeFilters.add(typeName);
    } else {
      activeTypeFilters.delete(typeName);
    }

    updateFiltersDisplay();
    applyFilters();
  }

  /**
   * Update filters button display
   */
  function updateFiltersDisplay() {
    if (!filtersDropdown) return;

    const filterCount = activeTypeFilters.size;

    if (filterCount > 0) {
      filtersDropdown.classList.remove("btn-outline-secondary");
      filtersDropdown.classList.add("btn-primary");

      const buttonContent = `<i class="fas fa-filter me-2"></i>Filtros (${filterCount})`;
      if (filtersDropdown.innerHTML !== buttonContent) {
        filtersDropdown.innerHTML = buttonContent;
      }
    } else {
      filtersDropdown.classList.remove("btn-primary");
      filtersDropdown.classList.add("btn-outline-secondary");
      filtersDropdown.innerHTML = '<i class="fas fa-filter"></i> Filtros';
    }
  }

  /**
   * Clear all active filters
   */
  function clearAllFilters() {
    activeTypeFilters.clear();

    const typeFilterCheckboxes = document.querySelectorAll(".type-filter");
    typeFilterCheckboxes.forEach((checkbox) => {
      checkbox.checked = false;
    });

    updateFiltersDisplay();
    applyFilters();
  }

  /**
   * Check if a row matches the type filters
   */
  function matchesTypeFilters(row) {
    if (activeTypeFilters.size === 0) {
      return true;
    }

    const badgeElement = row.querySelector(".badge");
    if (!badgeElement) return false;

    const badgeText = badgeElement.textContent.trim();

    for (const filterType of activeTypeFilters) {
      if (badgeText.includes(filterType)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Update search icon based on input content
   */
  function updateSearchIcon() {
    if (searchInput && searchIcon) {
      if (searchInput.value.trim()) {
        searchIcon.classList.remove("fa-search");
        searchIcon.classList.add("fa-times", "clear-icon");
        searchIcon.title = window.translations?.clear || "Limpiar búsqueda";
      } else {
        searchIcon.classList.remove("fa-times", "clear-icon");
        searchIcon.classList.add("fa-search");
        searchIcon.title = window.translations?.search || "Buscar";
      }
    }
  }

  /**
   * Handle search icon click
   */
  function handleSearchIconClick() {
    if (searchInput && searchIcon) {
      if (searchInput.value.trim()) {
        clearSearch();
      } else {
        searchInput.focus();
      }
    }
  }

  /**
   * Highlight matching text in search results
   */
  function highlightText(element, searchText) {
    if (!searchText) return;

    const originalText = element.textContent;
    const regex = new RegExp(`(${searchText})`, "gi");
    const highlightedText = originalText.replace(
      regex,
      '<mark class="bg-warning">$1</mark>'
    );

    if (highlightedText !== originalText) {
      element.innerHTML = highlightedText;
    }
  }

  /**
   * Clear highlighting from elements
   */
  function clearHighlight(element) {
    const marks = element.querySelectorAll("mark");
    marks.forEach((mark) => {
      mark.outerHTML = mark.innerHTML;
    });
  }

  /**
   * Apply both search and type filters
   */
  function applyFilters() {
    const searchText = searchInput
      ? searchInput.value.toLowerCase().trim()
      : "";
    let visibleCount = 0;

    updateSearchIcon();

    roleRows.forEach((row) => {
      const searchableElements = row.querySelectorAll(
        ".searchable-rolename, .searchable-description"
      );
      searchableElements.forEach((element) => clearHighlight(element));
    });

    roleRows.forEach((row) => {
      const searchData = row.getAttribute("data-search");
      const matchesSearch = !searchText || searchData.includes(searchText);
      const matchesType = matchesTypeFilters(row);

      if (matchesSearch && matchesType) {
        row.style.display = "";
        visibleCount++;

        // Highlight search terms
        if (searchText) {
          const searchableElements = row.querySelectorAll(
            ".searchable-rolename, .searchable-description"
          );
          searchableElements.forEach((element) =>
            highlightText(element, searchText)
          );
        }
      } else {
        row.style.display = "none";
      }
    });

    updateSearchResults(searchText, visibleCount);
    updateBulkSelectionUI();
  }

  /**
   * Perform live search on role table
   */
  function performSearch() {
    applyFilters();
  }

  /**
   * Update search results counter and messages
   */
  function updateSearchResults(searchText, visibleCount) {
    const hasActiveFilters = activeTypeFilters.size > 0;

    if (searchText || hasActiveFilters) {
      if (visibleCount === 0) {
        rolesTableContainer.style.display = "none";
        noSearchResults.style.display = "block";
        searchTerm.textContent = searchText;
        searchResults.textContent = "";
      } else {
        rolesTableContainer.style.display = "block";
        noSearchResults.style.display = "none";
        searchResults.textContent = `${
          window.translations?.showing || "Mostrando"
        } ${visibleCount} ${
          visibleCount === 1
            ? window.translations?.role || "rol"
            : window.translations?.roles || "roles"
        } ${window.translations?.of || "de"} ${totalRoles}`;
      }
    } else {
      rolesTableContainer.style.display = "block";
      noSearchResults.style.display = "none";
      searchResults.textContent = `${
        window.translations?.total || "Total"
      }: ${totalRoles} ${window.translations?.roles || "roles"}`;
    }
  }

  /**
   * Initialize search functionality
   */
  function initializeSearch() {
    if (searchInput) {
      searchInput.addEventListener("input", performSearch);

      if (searchIcon) {
        searchIcon.addEventListener("click", handleSearchIconClick);
      }

      updateSearchResults("", totalRoles);
      updateSearchIcon();

      searchInput.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
          clearSearch();
        }
      });

      searchInput.addEventListener("input", updateSearchIcon);
    }
  }

  /**
   * Initialize filters functionality
   */
  function initializeFilters() {
    if (filtersDropdown) {
      filtersDropdown.disabled = false;
      generateFiltersMenu();
    }
  }

  /**
   * Initialize bulk selection functionality
   */
  function initializeBulkSelection() {
    // Select all checkbox
    if (selectAllCheckbox) {
      selectAllCheckbox.addEventListener("change", handleSelectAllChange);
    }

    // Individual role checkboxes
    roleCheckboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", handleRoleCheckboxChange);
    });

    // Bulk delete modal events
    if (bulkDeleteModal) {
      bulkDeleteModal.addEventListener("show.bs.modal", prepareBulkDeleteModal);
    }

    if (bulkDeleteConfirmBtn) {
      bulkDeleteConfirmBtn.addEventListener("click", performBulkDelete);
    }

    // Initialize UI
    updateBulkSelectionUI();
  }

  /**
   * Clear search input and reset results
   */
  function clearSearch() {
    if (searchInput) {
      searchInput.value = "";
      updateSearchIcon();
      applyFilters();
      searchInput.focus();
    }
  }

  /**
   * Initialize delete role modal
   */
  function initializeDeleteModal() {
    if (deleteModal) {
      deleteModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const roleId = button.getAttribute("data-role-id");
        const roleName = button.getAttribute("data-rolename");
        const roleDescription = button.getAttribute("data-role-description");

        // Update modal content
        const deleteRoleName = document.getElementById("deleteRoleName");
        const deleteRoleNameDetail = document.getElementById(
          "deleteRoleNameDetail"
        );
        const deleteRoleDescription = document.getElementById(
          "deleteRoleDescription"
        );
        const deleteRoleForm = document.getElementById("deleteRoleForm");

        if (deleteRoleName) deleteRoleName.textContent = roleName;
        if (deleteRoleNameDetail) deleteRoleNameDetail.textContent = roleName;
        if (deleteRoleDescription)
          deleteRoleDescription.textContent = roleDescription;
        if (deleteRoleForm) {
          deleteRoleForm.action = `/role/delete/${roleId}`;
        }
      });
    }
  }

  /**
   * Initialize all role management functionality
   */
  function init() {
    initializeSearch();
    initializeFilters();
    initializeBulkSelection();
    initializeDeleteModal();

    // Make functions available globally
    window.clearSearch = clearSearch;
    window.clearAllFilters = clearAllFilters;

    console.log("Role management initialized");
    console.log(
      `Found ${totalRoles} roles with ${getUniqueTypes().size} unique types`
    );
  }

  // Initialize everything
  init();
});
