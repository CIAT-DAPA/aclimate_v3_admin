// static/js/dataSourceTemplates.js

// Definir plantillas JSON
const templates = {
    sst_iridl: JSON.stringify({
        "sst_download": {
            "base_url": "http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/",
            "dataset_paths": {
            "historical": ".EMC/.CFSv2/.ENSEMBLE/.OCNF/.surface/.TMP/",
            "realtime": ".EMC/.CFSv2/.REALTIME_ENSEMBLE/.OCNF/.surface/.TMP/"
            },
            "request_template": {
            "time_range": "appendstream/S/%280000%201%20{current_month_abb}%201982-{current_year}%29/VALUES/",
            "forecast_range": "L/{start_offset}.5/{end_offset}.5/RANGE/%5BL%5D//keepgrids/average/",
            "area_filter": "X/{x_min}/{x_max}/flagrange/Y/{y_min}/{y_max}/flagrange/add/1/flaggt/",
            "output_format": "0/maskle/mul/-999/setmissing_value/%5BX/Y%5D%5BS/L/add/%5Dcptv10.tsv.gz"
            },
            "multi_area_template": "X/{x_min1}/{x_max1}/flagrange/Y/{y_min1}/{y_max1}/flagrange/add/1/flaggt/X/{x_min2}/{x_max2}/flagrange/Y/{y_min2}/{y_max2}/flagrange/add/1/flaggt/add/",
            "file_naming": "{current_month_abb}_{target_season}_sst.tsv.gz",
            "example_request": {
            "department": "Antioquia",
            "target_season": "Aug-Sep-Oct",
            "areas": [
                {
                "x_min": -180.0,
                "x_max": -80.0,
                "y_min": -10.0,
                "y_max": 10.0
                },
                {
                "x_min": 120.0,
                "x_max": 180.0,
                "y_min": -15.0,
                "y_max": 5.0
                }
            ],
            "output_directory": "/data/descargas/Antioquia/Aug-Sep-Oct",
            "temporal_params": {
                "calculation_date": "2025-07-25",
                "forecast_offsets": {
                "start": 1.5,
                "end": 3.5
                }
            }
            }
        }

    }, null, 4),
    copernicus: JSON.stringify({
        "api": "copernicus",
        "version": "v1",
        "parameters": {
            "product_type": "reanalysis",
            "variable": ["2m_temperature", "total_precipitation"],
            "year": "2023",
            "month": "01",
            "day": "01",
            "time": "12:00",
            "format": "netcdf"
        }
    }, null, 4),
    
    chirps: JSON.stringify({
        "api": "chirps",
        "version": "2.0",
        "parameters": {
            "base_url": "http://data.chc.ucsb.edu/products/CHIRP/daily",
            "file_pattern": "chirp.{date}.tif.gz",
            "date_format": "YYYY.MM.DD",
            "variables": ["precipitation"],
            "processing": {
                "decompress": true,
                "remove_compressed": true
            }
        }
    }, null, 4),
    
    era5_single: JSON.stringify({
        "api": "era5",
        "dataset": "sis-agrometeorological-indicators",
        "version": "1_1",
        "parameters": {
            "variable": "2m_temperature",
            "statistic": "24_hour_maximum",
            "transform": {
                "operation": "subtract",
                "value": 273.15
            },
            "format": "zip",
            "output_format": "geotiff"
        }
    }, null, 4),
    
    era5_full: JSON.stringify({
        "api": "era5",
        "dataset": "sis-agrometeorological-indicators",
        "version": "1_1",
        "parameters": {
            "variables": [
                {
                    "name": "2m_temperature",
                    "statistic": "24_hour_maximum",
                    "output_name": "t_max",
                    "transform": {
                        "operation": "subtract",
                        "value": 273.15
                    }
                },
                {
                    "name": "2m_temperature",
                    "statistic": "24_hour_minimum",
                    "output_name": "t_min",
                    "transform": {
                        "operation": "subtract",
                        "value": 273.15
                    }
                },
                {
                    "name": "solar_radiation_flux",
                    "output_name": "sol_rad",
                    "transform": {
                        "operation": "divide",
                        "value": 1000000
                    }
                }
            ],
            "format": "zip",
            "output_format": "geotiff"
        }
    }, null, 4),
    
    climatology: JSON.stringify({
        "process": "climatology",
        "parameters": {
            "source": "historical",
            "aggregation": {
                "t_max": "mean",
                "t_min": "mean",
                "prec": "median",
                "sol_rad": "mean"
            },
            "group_by": ["day", "month"]
        }
    }, null, 4),
    
    full_workflow: JSON.stringify({
        "workflow": {
            "prepare_env": {
                "country": "{country}",
                "base_path": "/path/to/data",
                "cores": 4
            },
            "download": [
                {
                    "source": "chirps",
                    "parameters": {}
                },
                {
                    "source": "era5",
                    "parameters": {
                        "variables": ["t_max", "t_min", "sol_rad"]
                    }
                }
            ],
            "extract": {},
            "process": [
                {
                    "name": "climatology",
                    "parameters": {}
                }
            ],
            "output": {
                "path": "/path/to/output",
                "format": "csv"
            }
        }
    }, null, 4),
    
    custom: "{}"
};

// Función para cargar plantilla en el campo JSON
function loadTemplate(selectElement) {
    const templateKey = selectElement.value;
    const jsonContent = document.getElementById('json-content');
    
    if (templateKey && templates[templateKey]) {
        jsonContent.value = templates[templateKey];
    } else {
        jsonContent.value = '';
    }
    
    // Resaltar sintaxis JSON si Prism está disponible
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(jsonContent);
    }
}

// Función para inicializar el editor en la página de edición
function initTemplateEditor() {
    const jsonContent = document.getElementById('json-content');
    const templateSelect = document.querySelector('select[name="template"]');
    
    if (jsonContent && templateSelect) {
        // Intentar emparejar el contenido actual con una plantilla
        try {
            const currentContent = jsonContent.value;
            for (const [key, template] of Object.entries(templates)) {
                if (JSON.stringify(JSON.parse(currentContent)) === JSON.stringify(JSON.parse(template))) {
                    templateSelect.value = key;
                    break;
                }
            }
        } catch (e) {
            // Ignorar errores de parseo
        }
        
        // Resaltar sintaxis inicial
        if (typeof Prism !== 'undefined') {
            Prism.highlightElement(jsonContent);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initTemplateEditor);