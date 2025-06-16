/**
 * User Management JavaScript
 * Handles user search, filtering, and modal interactions
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

  // Get all user rows
  const userRows = document.querySelectorAll(".user-row");
  const totalUsers = userRows.length;

  // Active filters
  let activeRoleFilters = new Set();

  /**
   * Get unique roles from current users
   */
  function getUniqueRoles() {
    const roles = new Map(); // Using Map to store role info

    userRows.forEach((row) => {
      const roleElement = row.querySelector(".badge");
      if (roleElement) {
        const roleText = roleElement.textContent.trim();
        const roleIcon = roleElement.querySelector("i");
        const iconClass = roleIcon ? roleIcon.className : "fas fa-user-tag";

        // Extract clean role name (remove icon text)
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

    let menuHTML = `
      <li><h6 class="dropdown-header">Filtrar por Rol</h6></li>
    `;

    // Add role filters
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

    // Add divider and clear filters
    menuHTML += `
      <li><hr class="dropdown-divider"></li>
      <li>
        <a class="dropdown-item text-primary" href="#" id="clearFilters">
          <i class="fas fa-times me-2"></i>Limpiar filtros
        </a>
      </li>
    `;

    filtersMenu.innerHTML = menuHTML;

    // Add event listeners to the new checkboxes
    initializeFilterEventListeners();
  }

  /**
   * Initialize filter event listeners
   */
  function initializeFilterEventListeners() {
    // Role filter checkboxes
    const roleFilterCheckboxes = document.querySelectorAll(".role-filter");
    roleFilterCheckboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", handleRoleFilterChange);
    });

    // Clear filters button
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
    const filterText =
      filtersDropdown.querySelector(".filter-text") || filtersDropdown;

    if (filterCount > 0) {
      filtersDropdown.classList.remove("btn-outline-secondary");
      filtersDropdown.classList.add("btn-primary");

      // Update button text to show active filters count
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

    // Uncheck all filter checkboxes
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
    // If no role filters are active, show all
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
        // Has content - show clear icon
        searchIcon.className = "fas fa-times search-icon clear-icon";
        searchIcon.title = window.translations?.clear || "Limpiar búsqueda";
      } else {
        // Empty - show search icon
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
        // Has content - clear it
        clearSearch();
      } else {
        // Empty - focus input
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

    // Update search icon
    updateSearchIcon();

    // Clear previous highlights
    userRows.forEach((row) => {
      const searchableElements = row.querySelectorAll(
        ".searchable-username, .searchable-fullname, .searchable-email"
      );
      searchableElements.forEach((element) => clearHighlight(element));
    });

    // Filter rows based on both search and role filters
    userRows.forEach((row) => {
      const searchData = row.getAttribute("data-search");
      const matchesSearch = !searchText || searchData.includes(searchText);
      const matchesRole = matchesRoleFilters(row);

      if (matchesSearch && matchesRole) {
        row.style.display = "";
        visibleCount++;

        // Highlight matching text if there's a search
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
      }
    });

    // Update search results display
    updateSearchResults(searchText, visibleCount);
  }

  /**
   * Perform live search on user table
   */
  function performSearch() {
    applyFilters(); // Use the combined filter function
  }

  /**
   * Update search results counter and messages
   */
  function updateSearchResults(searchText, visibleCount) {
    const hasActiveFilters = activeRoleFilters.size > 0;

    if (searchText || hasActiveFilters) {
      if (visibleCount === 0) {
        // No results found
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
        // Results found
        usersTableContainer.style.display = "block";
        noSearchResults.style.display = "none";

        // Get localized text
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
      // No search or filters, show all
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
      // Real-time search event listener
      searchInput.addEventListener("input", performSearch);

      // Search icon click event
      if (searchIcon) {
        searchIcon.addEventListener("click", handleSearchIconClick);
      }

      // Initialize counter and icon
      updateSearchResults("", totalUsers);
      updateSearchIcon();

      // Add keyboard shortcuts
      searchInput.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
          clearSearch();
        }
      });

      // Update icon when input changes
      searchInput.addEventListener("input", updateSearchIcon);
    }
  }

  /**
   * Initialize filters functionality
   */
  function initializeFilters() {
    if (filtersDropdown) {
      // Enable the filters dropdown
      filtersDropdown.disabled = false;

      // Generate dynamic filters menu
      generateFiltersMenu();

      // Initialize display
      updateFiltersDisplay();
    }
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
        // Button that triggered the modal
        const button = event.relatedTarget;

        // Extract info from data-* attributes
        const userId = button.getAttribute("data-user-id");
        const username = button.getAttribute("data-username");
        const userName = button.getAttribute("data-user-name");

        // Update modal content
        const modalUserName = deleteModal.querySelector("#deleteUserName");
        const modalUsername = deleteModal.querySelector("#deleteUsername");
        const modalFullName = deleteModal.querySelector("#deleteFullName");
        const deleteForm = deleteModal.querySelector("#deleteUserForm");

        // Set values
        if (modalUserName) modalUserName.textContent = username;
        if (modalUsername) modalUsername.textContent = username;
        if (modalFullName)
          modalFullName.textContent =
            userName || window.translations?.noName || "Sin nombre";

        // Configure form action
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
