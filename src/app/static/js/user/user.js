/**
 * User Management JavaScript
 * Handles user search, filtering, modal interactions and bulk operations
 */

document.addEventListener("DOMContentLoaded", function () {
  // Elements
  const searchInput = document.getElementById("searchInput");
  const searchIcon = document.getElementById("searchIcon");
  const usersTableBody = document.getElementById("usersTableBody");
  const usersTableContainer = document.getElementById("usersTableContainer");
  const noSearchResults = document.getElementById("noSearchResults");
  const searchResults = document.getElementById("searchResults");
  const searchTerm = document.getElementById("searchTerm");
  const deleteModal = document.getElementById("deleteUserModal");
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

  // Get all user rows and checkboxes
  const userRows = document.querySelectorAll(".user-row");
  const userCheckboxes = document.querySelectorAll(".user-checkbox");
  const totalUsers = userRows.length;

  // Active filters and selections
  let activeRoleFilters = new Set();
  let selectedUsers = new Set();
  let isDeleting = false;

  /**
   * Update bulk selection UI
   */
  function updateBulkSelectionUI() {
    const selectedCount = selectedUsers.size;

    if (selectedCount > 0) {
      bulkDeleteBtn.style.display = "flex";
      document.getElementById("selectedCount").textContent = selectedCount;
      bulkDeleteBtn.title = `${
        window.translations?.deleting || "Eliminar"
      } ${selectedCount} ${
        selectedCount === 1
          ? window.translations?.user || "usuario"
          : window.translations?.users || "usuarios"
      } ${
        selectedCount === 1
          ? window.translations?.selected || "seleccionado"
          : window.translations?.selectedPlural || "seleccionados"
      }`;
    } else {
      bulkDeleteBtn.style.display = "none";
    }

    // Update select all checkbox state
    const visibleCheckboxes = Array.from(userCheckboxes).filter(
      (cb) =>
        !cb.closest(".user-row").style.display ||
        cb.closest(".user-row").style.display !== "none"
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
  function handleUserCheckboxChange(event) {
    const checkbox = event.target;
    const userId = checkbox.value;
    const userRow = checkbox.closest(".user-row");

    if (checkbox.checked) {
      selectedUsers.add(userId);
      userRow.classList.add("selected");
    } else {
      selectedUsers.delete(userId);
      userRow.classList.remove("selected");
    }

    updateBulkSelectionUI();
  }

  /**
   * Handle select all checkbox change
   */
  function handleSelectAllChange(event) {
    const isChecked = event.target.checked;

    // Get only visible and enabled user checkboxes
    const visibleCheckboxes = Array.from(userCheckboxes).filter((cb) => {
      const row = cb.closest(".user-row");
      return (
        (!row.style.display || row.style.display !== "none") && !cb.disabled
      );
    });

    visibleCheckboxes.forEach((checkbox) => {
      const userId = checkbox.value;
      const userRow = checkbox.closest(".user-row");

      checkbox.checked = isChecked;

      if (isChecked) {
        selectedUsers.add(userId);
        userRow.classList.add("selected");
      } else {
        selectedUsers.delete(userId);
        userRow.classList.remove("selected");
      }
    });

    updateBulkSelectionUI();
  }

  /**
   * Prepare bulk delete modal
   */
  function prepareBulkDeleteModal() {
    const selectedUsersList = document.getElementById("selectedUsersList");
    const bulkDeleteCount = document.getElementById("bulkDeleteCount");

    bulkDeleteCount.textContent = selectedUsers.size;

    // Generate list of selected users
    let userListHTML = "";
    selectedUsers.forEach((userId) => {
      const checkbox = document.querySelector(
        `.user-checkbox[value="${userId}"]`
      );
      if (checkbox) {
        const username = checkbox.dataset.username;
        const userRow = checkbox.closest(".user-row");
        const fullNameElement = userRow.querySelector(".searchable-fullname");
        const fullName = fullNameElement
          ? fullNameElement.textContent.trim()
          : window.translations?.noName || "Sin nombre";

        userListHTML += `
          <div class="selected-user-item">
            <div class="selected-user-avatar">
              <i class="fas fa-user"></i>
            </div>
            <div>
              <strong>${username}</strong>
              <br>
              <small class="text-muted">${fullName}</small>
            </div>
          </div>
        `;
      }
    });

    selectedUsersList.innerHTML = userListHTML;
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

    const userIds = Array.from(selectedUsers);
    const totalToDelete = userIds.length;
    let deletedCount = 0;
    let errorCount = 0;

    statusText.textContent = window.translations?.preparing || "Preparando...";

    // Delete users one by one
    for (let i = 0; i < userIds.length; i++) {
      const userId = userIds[i];
      const checkbox = document.querySelector(
        `.user-checkbox[value="${userId}"]`
      );
      const username = checkbox ? checkbox.dataset.username : "Unknown";

      try {
        statusText.textContent = `${
          window.translations?.deleting || "Eliminando"
        } ${username}... (${i + 1}/${totalToDelete})`;

        // Make delete request
        const response = await fetch(`/user/delete/${userId}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });

        if (response.ok) {
          deletedCount++;
          statusText.textContent = `${
            window.translations?.deleted || "Eliminado"
          }: ${username}`;

          // Remove user row from table
          const userRow = checkbox.closest(".user-row");
          if (userRow) {
            userRow.style.transition = "opacity 0.3s ease-out";
            userRow.style.opacity = "0";
            setTimeout(() => {
              userRow.remove();
            }, 300);
          }

          // Remove from selected users
          selectedUsers.delete(userId);
        } else {
          errorCount++;
          console.error(
            `Error deleting user ${username}:`,
            response.statusText
          );
        }
      } catch (error) {
        errorCount++;
        console.error(`Error deleting user ${username}:`, error);
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
      window.translations?.usersDeleted || "usuarios eliminados exitosamente"
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
        // You can trigger a flash message here or show a toast
        console.log(`Successfully deleted ${deletedCount} users`);
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
   * Get unique roles from current users
   */
  function getUniqueRoles() {
    const roles = new Map();

    userRows.forEach((row) => {
      const roleElement = row.querySelector(".badge");
      if (roleElement) {
        const roleText = roleElement.textContent.trim();
        const roleIcon = roleElement.querySelector("i");
        const iconClass = roleIcon ? roleIcon.className : "fas fa-user-tag";

        const cleanRoleName = roleText.replace(/^\s*\w+\s+/, "").trim();

        if (cleanRoleName && !roles.has(cleanRoleName)) {
          roles.set(cleanRoleName, iconClass);
        }
      }
    });

    return roles;
  }

  /**
   * Generate filters dropdown content
   */
  function generateFiltersMenu() {
    if (!filtersMenu) return;

    const uniqueRoles = getUniqueRoles();

    let menuHTML = `<li><h6 class="dropdown-header">Filtrar por Rol</h6></li>`;

    uniqueRoles.forEach((iconClass, roleName) => {
      const filterId = `filter-${roleName.toLowerCase().replace(/\s+/g, "-")}`;
      menuHTML += `
        <li>
          <div class="dropdown-item-text">
            <div class="form-check">
              <input class="form-check-input role-filter" type="checkbox" id="${filterId}" value="${roleName}">
              <label class="form-check-label" for="${filterId}">
                <i class="${iconClass} me-2"></i>${roleName}
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
    const roleFilterCheckboxes = document.querySelectorAll(".role-filter");
    roleFilterCheckboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", handleRoleFilterChange);
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
   * Handle role filter change
   */
  function handleRoleFilterChange(event) {
    const roleName = event.target.value;

    if (event.target.checked) {
      activeRoleFilters.add(roleName);
    } else {
      activeRoleFilters.delete(roleName);
    }

    updateFiltersDisplay();
    applyFilters();
  }

  /**
   * Update filters button display
   */
  function updateFiltersDisplay() {
    if (!filtersDropdown) return;

    const filterCount = activeRoleFilters.size;

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
    activeRoleFilters.clear();

    const roleFilterCheckboxes = document.querySelectorAll(".role-filter");
    roleFilterCheckboxes.forEach((checkbox) => {
      checkbox.checked = false;
    });

    updateFiltersDisplay();
    applyFilters();
  }

  /**
   * Check if a row matches the role filters
   */
  function matchesRoleFilters(row) {
    if (activeRoleFilters.size === 0) {
      return true;
    }

    const roleElement = row.querySelector(".badge");
    if (!roleElement) return false;

    const roleText = roleElement.textContent.trim();
    const cleanRoleName = roleText.replace(/^\s*\w+\s+/, "").trim();

    return activeRoleFilters.has(cleanRoleName);
  }

  /**
   * Update search icon based on input content
   */
  function updateSearchIcon() {
    if (searchInput && searchIcon) {
      if (searchInput.value.trim()) {
        searchIcon.className = "fas fa-times search-icon clear-icon";
        searchIcon.title = window.translations?.clear || "Limpiar búsqueda";
      } else {
        searchIcon.className = "fas fa-search search-icon";
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
   * Apply both search and role filters
   */
  function applyFilters() {
    const searchText = searchInput
      ? searchInput.value.toLowerCase().trim()
      : "";
    let visibleCount = 0;

    updateSearchIcon();

    userRows.forEach((row) => {
      const searchableElements = row.querySelectorAll(
        ".searchable-username, .searchable-fullname, .searchable-email"
      );
      searchableElements.forEach((element) => clearHighlight(element));
    });

    userRows.forEach((row) => {
      const searchData = row.getAttribute("data-search");
      const matchesSearch = !searchText || searchData.includes(searchText);
      const matchesRole = matchesRoleFilters(row);

      if (matchesSearch && matchesRole) {
        row.style.display = "";
        visibleCount++;

        if (searchText) {
          const username = row.querySelector(".searchable-username");
          const fullname = row.querySelector(".searchable-fullname");
          const email = row.querySelector(".searchable-email");

          if (username) highlightText(username, searchText);
          if (fullname) highlightText(fullname, searchText);
          if (email && email.textContent !== "Sin email")
            highlightText(email, searchText);
        }
      } else {
        row.style.display = "none";

        // Uncheck hidden rows and remove from selection
        const checkbox = row.querySelector(".user-checkbox");
        if (checkbox && checkbox.checked) {
          checkbox.checked = false;
          selectedUsers.delete(checkbox.value);
          row.classList.remove("selected");
        }
      }
    });

    updateSearchResults(searchText, visibleCount);
    updateBulkSelectionUI();
  }

  /**
   * Perform live search on user table
   */
  function performSearch() {
    applyFilters();
  }

  /**
   * Update search results counter and messages
   */
  function updateSearchResults(searchText, visibleCount) {
    const hasActiveFilters = activeRoleFilters.size > 0;

    if (searchText || hasActiveFilters) {
      if (visibleCount === 0) {
        usersTableContainer.style.display = "none";
        noSearchResults.style.display = "block";

        if (searchText) {
          searchTerm.textContent = searchText;
        } else {
          const noResultsText = document.getElementById("noResultsText");
          if (noResultsText) {
            noResultsText.textContent =
              "No se encontraron usuarios que coincidan con los filtros aplicados";
          }
          searchTerm.textContent = "";
        }

        searchResults.textContent = "";
      } else {
        usersTableContainer.style.display = "block";
        noSearchResults.style.display = "none";

        const resultText =
          visibleCount === 1
            ? `${window.translations?.showing || "Mostrando"} ${visibleCount} ${
                window.translations?.user || "usuario"
              }`
            : `${window.translations?.showing || "Mostrando"} ${visibleCount} ${
                window.translations?.users || "usuarios"
              }`;

        let filterInfo = "";
        if (hasActiveFilters && !searchText) {
          filterInfo = ` (filtrados)`;
        } else if (hasActiveFilters && searchText) {
          filterInfo = ` (búsqueda + filtros)`;
        }

        searchResults.textContent = `${resultText}${filterInfo} ${
          window.translations?.of || "de"
        } ${totalUsers}`;
      }
    } else {
      usersTableContainer.style.display = "block";
      noSearchResults.style.display = "none";
      searchResults.textContent = `${
        window.translations?.total || "Total"
      }: ${totalUsers} ${window.translations?.users || "usuarios"}`;
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

      updateSearchResults("", totalUsers);
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
      updateFiltersDisplay();
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

    // Individual user checkboxes
    userCheckboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", handleUserCheckboxChange);
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
      applyFilters();
      searchInput.focus();
    }
  }

  /**
   * Initialize delete user modal
   */
  function initializeDeleteModal() {
    if (deleteModal) {
      deleteModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;

        const userId = button.getAttribute("data-user-id");
        const username = button.getAttribute("data-username");
        const userName = button.getAttribute("data-user-name");

        const modalUserName = deleteModal.querySelector("#deleteUserName");
        const modalUsername = deleteModal.querySelector("#deleteUsername");
        const modalFullName = deleteModal.querySelector("#deleteFullName");
        const deleteForm = deleteModal.querySelector("#deleteUserForm");

        if (modalUserName) modalUserName.textContent = username;
        if (modalUsername) modalUsername.textContent = username;
        if (modalFullName)
          modalFullName.textContent =
            userName || window.translations?.noName || "Sin nombre";

        if (deleteForm) deleteForm.action = `/user/delete/${userId}`;
      });
    }
  }

  /**
   * Initialize all user management functionality
   */
  function init() {
    initializeSearch();
    initializeFilters();
    initializeBulkSelection();
    initializeDeleteModal();

    // Make functions available globally
    window.clearSearch = clearSearch;
    window.clearAllFilters = clearAllFilters;

    console.log("User management initialized");
    console.log(
      `Found ${totalUsers} users with ${getUniqueRoles().size} unique roles`
    );
  }

  // Initialize everything
  init();
});
