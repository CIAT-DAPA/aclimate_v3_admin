#!/bin/bash
# =============================================================================
# Script para actualizar traducciones en Linux (Producción)
# Uso: ./update_translations.sh
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
    python validate_translations.py > validation_report.txt 2>&1 || true
    
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
# 5. PREGUNTAR SI CONTINUAR
# =============================================================================
if [ $TOTAL_FUZZY -gt 0 ]; then
    echo "⚠️  ¿Deseas continuar con la compilación?"
    echo "   - Hay $TOTAL_FUZZY marcadores fuzzy que NO se compilarán"
    echo "   - Revisa los archivos .po antes de continuar"
    echo ""
    read -p "Continuar? (s/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        echo "❌ Compilación cancelada"
        echo ""
        echo "Acciones sugeridas:"
        echo "  1. Revisar marcadores fuzzy: grep -r '#, fuzzy' app/translations/"
        echo "  2. Ejecutar script de corrección: python fix_fuzzy_translations.py"
        echo "  3. Editar manualmente los archivos .po"
        echo "  4. Volver a ejecutar este script"
        exit 1
    fi
fi

# =============================================================================
# 6. COMPILAR TRADUCCIONES
# =============================================================================
echo "🔨 Paso 5/7: Compilando traducciones..."
pybabel compile -d app/translations
echo "   ✅ Archivos .mo compilados"
echo ""

# =============================================================================
# 7. VERIFICAR ARCHIVOS .mo
# =============================================================================
echo "🔍 Paso 6/7: Verificando archivos compilados..."
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
    echo "   ❌ Error: Algunos archivos .mo no se generaron"
    exit 1
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
echo "   - Marcadores fuzzy: $TOTAL_FUZZY"
echo "   - Compilación: ✅"
echo ""
echo "🔄 Próximos pasos:"
echo "   1. Reiniciar el servidor de aplicación"
echo "      • systemctl restart tu-servicio"
echo "      • supervisorctl restart tu-app"
echo "      • O el comando correspondiente"
echo ""
echo "   2. Limpiar caché del navegador (Ctrl + Shift + R)"
echo ""
echo "   3. Probar las traducciones en la aplicación"
echo ""

if [ $TOTAL_FUZZY -gt 0 ]; then
    echo "⚠️  Advertencia:"
    echo "   - Hay $TOTAL_FUZZY traducciones fuzzy que NO se compilaron"
    echo "   - Revisa validation_report.txt para más detalles"
    echo "   - Ejecuta fix_fuzzy_translations.py para corregirlas"
    echo ""
fi

echo "================================================================================"
