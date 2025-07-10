// static/js/tableSearch.js

/**
 * Inicializa el sistema de búsqueda y filtros para una tabla
 * @param {Object} config - Configuración específica de la tabla
 */
export function initTableSearch(config) {
    const {
        searchInputId,
        filtersButtonId,
        tableContainerId,
        noResultsId,
        resultsCountId,
        tableBodyId,
        searchColumns,
        filterConfigs
    } = config;

    // Elementos DOM
    const searchInput = document.getElementById(searchInputId);
    const filtersButton = document.getElementById(filtersButtonId);
    const tableContainer = document.getElementById(tableContainerId);
    const noResults = document.getElementById(noResultsId);
    const resultsCount = document.getElementById(resultsCountId);
    const tableBody = document.getElementById(tableBodyId);
    const rows = tableBody.querySelectorAll('tr');
    const filtersMenu = document.querySelector(`#${filtersButtonId} + .dropdown-menu`);

    // Estado
    let activeFilters = {};

    // Función para resaltar texto
    function highlightText(element, searchText) {
        if (!element || !searchText) return;
        const originalText = element.textContent;
        const regex = new RegExp(`(${searchText})`, "gi");
        element.innerHTML = originalText.replace(regex, '<mark>$1</mark>');
    }
    
    // Función para quitar resaltado
    function clearHighlight(element) {
        if (!element) return;
        element.innerHTML = element.textContent;
    }

    /**
     * Actualiza la interfaz basada en los filtros activos
     */
    function updateFiltersDisplay() {
        const filterCount = Object.keys(activeFilters).filter(key => 
            activeFilters[key].size > 0
        ).length;

        if (filterCount > 0) {
            filtersButton.classList.remove("btn-outline-secondary");
            filtersButton.classList.add("btn-primary");
            filtersButton.innerHTML = `<i class="fas fa-filter me-2"></i> ${filtersButton.dataset.filterText} (${filterCount})`;
        } else {
            filtersButton.classList.remove("btn-primary");
            filtersButton.classList.add("btn-outline-secondary");
            filtersButton.innerHTML = `<i class="fas fa-filter"></i> ${filtersButton.dataset.filterText}`;
        }
    }

    /**
     * Aplica todos los filtros activos
     */
    function applyFilters() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    let visibleCount = 0;

    // Limpiar resaltados previos
    rows.forEach(row => {
        searchColumns.forEach(column => {
            const cells = row.querySelectorAll(column.selector);
            cells.forEach(cell => clearHighlight(cell));
        });
    });

    rows.forEach(row => {
        let matchesSearch = !searchTerm; // Si no hay término, coincide por defecto
        let matchesFilters = true;

        // Aplicar búsqueda en TODAS las columnas
        if (searchTerm) {
            matchesSearch = false;
            
            // Verificar todas las columnas buscables
            searchColumns.forEach(column => {
                const cells = row.querySelectorAll(column.selector);
                cells.forEach(cell => {
                    const cellText = cell.textContent.toLowerCase();
                    if (cellText.includes(searchTerm)) {
                        matchesSearch = true;
                        highlightText(cell, searchTerm);
                    }
                });
            });
        }

        // Aplicar filtros
        for (const [filterName, filterSet] of Object.entries(activeFilters)) {
            if (filterSet.size > 0) {
                const filterConfig = filterConfigs.find(f => f.name === filterName);
                if (filterConfig) {
                    const filterValue = filterConfig.getValue(row);
                    matchesFilters = matchesFilters && filterSet.has(filterValue);
                }
            }
        }

        // Mostrar/ocultar fila
        if (matchesSearch && matchesFilters) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });

    // Actualizar UI de resultados
    updateResultsUI(searchTerm, visibleCount);
}

    /**
     * Actualiza la interfaz de resultados
     */
    function updateResultsUI(searchTerm, visibleCount) {
        // Siempre actualiza el número de resultados
        resultsCount.textContent = visibleCount;

        if (visibleCount === 0) {
            tableContainer.style.display = 'none';
            noResults.style.display = 'block';
            noResults.querySelector('.search-term').textContent = searchTerm || '';
        } else {
            tableContainer.style.display = 'block';
            noResults.style.display = 'none';
        }
    }

    /**
     * Genera los controles de filtro
     */
    function generateFilterControls() {
        if (!filtersMenu) return;
        
        let menuHTML = '';
        
        filterConfigs.forEach(filterConfig => {
            // Cabecera del filtro
            menuHTML += `<li><h6 class="dropdown-header">${filterConfig.label}</h6></li>`;
            
            // Obtener valores únicos para este filtro
            const uniqueValues = new Map();
            
            rows.forEach(row => {
                const value = filterConfig.getValue(row);
                if (value && !uniqueValues.has(value)) {
                    uniqueValues.set(value, filterConfig.getDisplayValue ? 
                        filterConfig.getDisplayValue(row) : value);
                }
            });
            
            // Convertir a array y ordenar alfabéticamente
            const sortedValues = Array.from(uniqueValues).sort((a, b) => 
                a[1].localeCompare(b[1])
            );
            
            // Crear opciones
            sortedValues.forEach(([value, displayValue]) => {
                const filterId = `filter-${filterConfig.name}-${value.toString().replace(/\s+/g, '-')}`;
                menuHTML += `
                    <li>
                        <div class="dropdown-item-text">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" 
                                    id="${filterId}" 
                                    data-filter="${filterConfig.name}" 
                                    value="${value}">
                                <label class="form-check-label" for="${filterId}">
                                    ${displayValue}
                                </label>
                            </div>
                        </div>
                    </li>
                `;
            });
        });
        
        // Botón para limpiar filtros
        menuHTML += `
            <li><hr class="dropdown-divider"></li>
            <li>
                <a class="dropdown-item text-primary" href="#" id="clearFilters">
                    <i class="fas fa-times me-2"></i>${filtersButton.dataset.clearText}
                </a>
            </li>
        `;
        
        filtersMenu.innerHTML = menuHTML;
        
        // Event listeners para los filtros
        filtersMenu.querySelectorAll('.form-check-input').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const filterName = this.dataset.filter;
                
                if (!activeFilters[filterName]) {
                    activeFilters[filterName] = new Set();
                }
                
                if (this.checked) {
                    activeFilters[filterName].add(this.value);
                } else {
                    activeFilters[filterName].delete(this.value);
                }
                
                updateFiltersDisplay();
                applyFilters();
            });
        });
        
        // Event listener para limpiar filtros
        document.getElementById('clearFilters').addEventListener('click', function(e) {
            e.preventDefault();
            activeFilters = {};
            filtersMenu.querySelectorAll('.form-check-input').forEach(cb => cb.checked = false);
            updateFiltersDisplay();
            applyFilters();
        });
    }

    // Inicialización
    if (searchInput && filtersButton && tableContainer) {
        // Configurar elementos
        filtersButton.dataset.filterText = filtersButton.textContent;
        resultsCount.dataset.resultsText = resultsCount.textContent;
        
        // Generar controles de filtro
        generateFilterControls();
        
        // Event listeners
        searchInput.addEventListener('input', applyFilters);
        
        // Aplicar filtros iniciales
        applyFilters();
    } else {
        console.error('Required elements not found:', {
            searchInput, 
            filtersButton,
            tableContainer
        });
    }
}