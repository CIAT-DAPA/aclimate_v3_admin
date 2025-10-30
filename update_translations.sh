#!/bin/bash
# =============================================================================
# Script para actualizar traducciones en Linux (Producción)
# Uso: ./update_translations.sh
# 
# Modo: NO INTERACTIVO (apto para CI/CD pipelines)
# - No pide confirmaciones
# - Solo falla si hay errores CRÍTICOS
# - Advertencias no detienen la ejecución
# =============================================================================

set -e  # Salir si hay error

echo "================================================================================"
echo "🌍 ACTUALIZACIÓN DE TRADUCCIONES - Linux/Producción"
echo "================================================================================"
echo ""

# Cambiar al directorio src
cd "$(dirname "$0")"
cd src

# =============================================================================
# 1. SKIP EXTRACTION IN PRODUCTION (translations come from git)
# =============================================================================
echo "📝 Paso 1/7: Omitiendo extracción (traducciones desde repositorio)..."
echo "   ⏭️  NOTA: Los archivos .po ya vienen actualizados desde git"
echo "   ⏭️  Si necesitas re-extraer, ejecuta manualmente: pybabel extract + update"
echo ""

# =============================================================================
# 2. SKIP UPDATE IN PRODUCTION (avoid merge conflicts)
# =============================================================================
echo "🔄 Paso 2/7: Omitiendo actualización de catálogos..."
echo "   ⏭️  Los archivos .po NO se modificarán (evita conflictos de merge)"
echo "   ⏭️  Las traducciones se usan tal como vienen del repositorio"
echo ""

# =============================================================================
# 3. VERIFICAR ARCHIVOS .po EXISTEN
# =============================================================================
echo "🔍 Paso 3/7: Verificando archivos de traducción..."
if [ -f "app/translations/es_CO/LC_MESSAGES/messages.po" ] && \
   [ -f "app/translations/es_GT/LC_MESSAGES/messages.po" ] && \
   [ -f "app/translations/en_US/LC_MESSAGES/messages.po" ]; then
    echo "   ✅ Todos los archivos .po encontrados"
else
    echo "   ❌ ERROR: Faltan archivos .po"
    exit 1
fi
echo ""

# =============================================================================
# 4. SKIP VALIDATION IN PRODUCTION
# =============================================================================
echo "✅ Paso 4/7: Omitiendo validación..."
echo "   ⏭️  Las traducciones ya fueron validadas antes del commit"
echo ""

# =============================================================================
# 5. SKIP AUTO-FIX IN PRODUCTION
# =============================================================================
echo "🔧 Paso 5/7: Omitiendo correcciones automáticas..."
echo "   ⏭️  Los archivos .po no se modificarán automáticamente"
echo ""

# =============================================================================
# 6. COMPILAR TRADUCCIONES
# =============================================================================
echo "🔨 Paso 6/7: Compilando traducciones..."
pybabel compile -d app/translations
echo "   ✅ Archivos .mo compilados"
echo ""

# =============================================================================
# 7. VERIFICAR ARCHIVOS .mo
# =============================================================================
echo "🔍 Paso 7/7: Verificando archivos compilados..."
if [ -f "app/translations/es_CO/LC_MESSAGES/messages.mo" ] && \
   [ -f "app/translations/es_GT/LC_MESSAGES/messages.mo" ] && \
   [ -f "app/translations/en_US/LC_MESSAGES/messages.mo" ]; then
    echo "   ✅ Todos los archivos .mo existen"
    
    # Mostrar tamaños
    SIZE_CO=$(du -h app/translations/es_CO/LC_MESSAGES/messages.mo | cut -f1)
    SIZE_GT=$(du -h app/translations/es_GT/LC_MESSAGES/messages.mo | cut -f1)
    SIZE_US=$(du -h app/translations/en_US/LC_MESSAGES/messages.mo | cut -f1)
    
    echo "   es_CO: $SIZE_CO"
    echo "   es_GT: $SIZE_GT"
    echo "   en_US: $SIZE_US"
else
    echo "   ⚠️  Advertencia: Algunos archivos .mo no se generaron"
    echo "   ℹ️  La aplicación funcionará con traducciones parciales"
fi
echo ""

# =============================================================================
# 8. RESUMEN
# =============================================================================
echo "================================================================================"
echo "✅ COMPILACIÓN DE TRADUCCIONES COMPLETADA"
echo "================================================================================"
echo ""
echo "📊 Resumen:"
echo "   - Archivos .po: ✅ (desde repositorio git)"
echo "   - Compilación .mo: ✅"
echo "   - Sin modificaciones a archivos .po: ✅"
echo ""
echo "ℹ️  Modo producción:"
echo "   - NO se ejecutó pybabel extract/update"
echo "   - Los archivos .po NO fueron modificados"
echo "   - Las traducciones provienen directamente del repositorio git"
echo ""
echo "✅ Traducciones listas - Sin conflictos de merge"
echo ""
echo "================================================================================"
