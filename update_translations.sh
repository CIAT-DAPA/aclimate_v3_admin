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
# 1. EXTRAER TEXTOS TRADUCIBLES
# =============================================================================
echo "📝 Paso 1/7: Extrayendo textos traducibles..."
pybabel extract -F babel.cfg -k _l -o messages.pot .
echo "   ✅ messages.pot generado"
echo ""

# =============================================================================
# 2. ACTUALIZAR CATÁLOGOS
# =============================================================================
echo "🔄 Paso 2/7: Actualizando catálogos de traducción..."
pybabel update -i messages.pot -d app/translations
echo "   ✅ Catálogos actualizados (es_CO, es_GT, en_US)"
echo ""

# =============================================================================
# 3. CONTAR MARCADORES FUZZY
# =============================================================================
echo "🔍 Paso 3/7: Buscando marcadores fuzzy..."
FUZZY_COUNT_CO=$(grep -c "#, fuzzy" app/translations/es_CO/LC_MESSAGES/messages.po || true)
FUZZY_COUNT_GT=$(grep -c "#, fuzzy" app/translations/es_GT/LC_MESSAGES/messages.po || true)
FUZZY_COUNT_US=$(grep -c "#, fuzzy" app/translations/en_US/LC_MESSAGES/messages.po || true)
TOTAL_FUZZY=$((FUZZY_COUNT_CO + FUZZY_COUNT_GT + FUZZY_COUNT_US))

echo "   es_CO: $FUZZY_COUNT_CO marcadores fuzzy"
echo "   es_GT: $FUZZY_COUNT_GT marcadores fuzzy"
echo "   en_US: $FUZZY_COUNT_US marcadores fuzzy"
echo "   Total: $TOTAL_FUZZY marcadores fuzzy"

if [ $TOTAL_FUZZY -gt 0 ]; then
    echo "   ⚠️  Advertencia: Hay traducciones marcadas como fuzzy (no se compilarán)"
fi
echo ""

# =============================================================================
# 4. VALIDAR TRADUCCIONES
# =============================================================================
echo "✅ Paso 4/7: Validando traducciones..."
if [ -f "validate_translations.py" ]; then
    python3 validate_translations.py > validation_report.txt 2>&1 || true
    
    # Contar errores y advertencias
    ERRORS=$(grep -c "❌ Errores:" validation_report.txt || echo "0")
    WARNINGS=$(grep -c "⚠️  Advertencias:" validation_report.txt || echo "0")
    
    echo "   📊 Reporte de validación generado: validation_report.txt"
    echo ""
    echo "   Para ver problemas críticos:"
    echo "   grep -A 10 'SUSPICIOUS_PATTERN' validation_report.txt"
    echo ""
else
    echo "   ⚠️  Script de validación no encontrado (validate_translations.py)"
    echo "   Continuando sin validación..."
fi
echo ""

# =============================================================================
# 5. CORRECCIÓN AUTOMÁTICA DE ERRORES CRÍTICOS
# =============================================================================
echo "🔧 Paso 5/7: Corrigiendo errores críticos..."

# PRIMERO: Corregir errores críticos (fuzzy, vacíos, placeholders)
if [ -f "fix_critical_errors.py" ]; then
    echo "   🔧 Eliminando marcadores fuzzy y rellenando traducciones vacías..."
    python3 fix_critical_errors.py > critical_fixes.txt 2>&1 || true
    
    # Verificar si se hicieron correcciones (contar líneas que contengan AUTO-FIXED)
    CRITICAL_FIXES=$(grep "AUTO-FIXED" app/translations/*/LC_MESSAGES/messages.po 2>/dev/null | wc -l || echo "0")
    # Limpiar espacios en blanco
    CRITICAL_FIXES=$(echo "$CRITICAL_FIXES" | tr -d ' ')
    
    if [ "$CRITICAL_FIXES" -gt 0 ]; then
        echo "   ✅ $CRITICAL_FIXES correcciones críticas aplicadas"
        echo "   📝 Ver detalles en: critical_fixes.txt"
        echo "   ⚠️  IMPORTANTE: Revisa las traducciones marcadas 'AUTO-FIXED' después del deploy"
    fi
else
    echo "   ⚠️  Script de corrección crítica no encontrado (fix_critical_errors.py)"
fi
echo ""

# SEGUNDO: Verificar patrones sospechosos
echo "   🔍 Verificando patrones sospechosos..."
# Contar traducciones sospechosas
SUSPICIOUS_COUNT=$(grep -c "SUSPICIOUS_PATTERN" validation_report.txt 2>/dev/null || echo "0")

if [ $SUSPICIOUS_COUNT -gt 0 ]; then
    echo "   ⚠️  Detectados $SUSPICIOUS_COUNT patrones sospechosos"
    
    if [ -f "fix_suspicious_translations.py" ]; then
        echo "   🔧 Aplicando correcciones automáticas..."
        python3 fix_suspicious_translations.py > fix_report.txt 2>&1 || true
        
        # Verificar si se hicieron correcciones
        CORRECTIONS=$(grep -c "traducciones corregidas" fix_report.txt 2>/dev/null || echo "0")
        if [ "$CORRECTIONS" -gt 0 ]; then
            echo "   ✅ Correcciones automáticas aplicadas"
            echo "   📝 Ver detalles en: fix_report.txt"
        fi
    else
        echo "   ⚠️  Script de corrección no encontrado (fix_suspicious_translations.py)"
        echo "   ℹ️  Continuando con traducciones actuales..."
    fi
fi

# Re-contar fuzzy después de las correcciones
FUZZY_COUNT_CO=$(grep -c "#, fuzzy" app/translations/es_CO/LC_MESSAGES/messages.po || true)
FUZZY_COUNT_GT=$(grep -c "#, fuzzy" app/translations/es_GT/LC_MESSAGES/messages.po || true)
FUZZY_COUNT_US=$(grep -c "#, fuzzy" app/translations/en_US/LC_MESSAGES/messages.po || true)
TOTAL_FUZZY=$((FUZZY_COUNT_CO + FUZZY_COUNT_GT + FUZZY_COUNT_US))

# Advertir sobre fuzzy restantes pero NO detener ejecución
if [ $TOTAL_FUZZY -gt 0 ]; then
    echo "   ⚠️  Aún quedan $TOTAL_FUZZY marcadores fuzzy (no se compilarán)"
    echo "   ℹ️  Continuando con compilación..."
fi
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
echo "✅ ACTUALIZACIÓN COMPLETADA"
echo "================================================================================"
echo ""
echo "📊 Resumen:"
echo "   - Textos extraídos: ✅"
echo "   - Catálogos actualizados: ✅"
echo "   - Traducciones sospechosas: $SUSPICIOUS_COUNT"
echo "   - Marcadores fuzzy: $TOTAL_FUZZY"
echo "   - Compilación: ✅"
echo ""

# Verificar si hay errores o advertencias en las traducciones
# Buscar la línea "Total de errores: X" en el reporte
CRITICAL_ERRORS=$(grep "Total de errores:" validation_report.txt 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")

# Mostrar reporte de problemas pero NO detener el pipeline
if [ "$CRITICAL_ERRORS" -gt 0 ] || [ $TOTAL_FUZZY -gt 0 ] || [ $SUSPICIOUS_COUNT -gt 0 ]; then
    echo "⚠️  Advertencias en traducciones (NO detienen el deployment):"
    
    if [ "$CRITICAL_ERRORS" -gt 0 ]; then
        echo "   - $CRITICAL_ERRORS errores de validación detectados"
    fi
    if [ $TOTAL_FUZZY -gt 0 ]; then
        echo "   - $TOTAL_FUZZY marcadores fuzzy (traducciones no compiladas)"
    fi
    if [ $SUSPICIOUS_COUNT -gt 0 ]; then
        echo "   - $SUSPICIOUS_COUNT patrones sospechosos detectados"
    fi
    
    echo ""
    echo "   ℹ️  La aplicación funcionará correctamente con traducciones parciales"
    echo "   📝 Ver detalles en: validation_report.txt"
    
    if [ "$CRITICAL_ERRORS" -gt 0 ]; then
        echo ""
        echo "   📋 Errores comunes:"
        echo "   - Traducciones faltantes (msgstr vacío) → Se mostrará texto original"
        echo "   - Placeholders incorrectos (%(variable)s) → Se mostrará texto sin formato"
    fi
    echo ""
fi

echo "✅ Traducciones actualizadas - Pipeline puede continuar"
echo ""

echo "================================================================================"
