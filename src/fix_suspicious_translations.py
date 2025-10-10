"""
Script para corregir traducciones SOSPECHOSAS detectadas por el validador.
Ejecutar desde: src/
"""

import re
import os

def fix_po_file(file_path, corrections):
    """
    Corrige traducciones en un archivo .po
    
    Args:
        file_path: Ruta al archivo .po
        corrections: Lista de tuplas (msgid_pattern, old_msgstr, new_msgstr)
    """
    print(f"\n{'='*80}")
    print(f"Corrigiendo: {file_path}")
    print(f"{'='*80}\n")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    corrections_made = 0
    
    for msgid_pattern, old_msgstr, new_msgstr, description in corrections:
        # Buscar el patrón en el archivo
        pattern = rf'(msgid "{re.escape(msgid_pattern)}"\nmsgstr ")({re.escape(old_msgstr)})(")'
        
        if re.search(pattern, content):
            content = re.sub(pattern, rf'\g<1>{new_msgstr}\g<3>', content)
            corrections_made += 1
            print(f"✓ Corregido: {description}")
            print(f"  msgid:  \"{msgid_pattern}\"")
            print(f"  Antes:  \"{old_msgstr}\"")
            print(f"  Ahora:  \"{new_msgstr}\"\n")
    
    if corrections_made > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {corrections_made} traducciones corregidas en {os.path.basename(file_path)}\n")
    else:
        print(f"ℹ️  No se encontraron problemas en {os.path.basename(file_path)}\n")
    
    return corrections_made


def main():
    """Corrige traducciones sospechosas en todos los idiomas"""
    
    print("\n" + "="*80)
    print("🔧 CORRECCIÓN DE TRADUCCIONES SOSPECHOSAS")
    print("="*80)
    
    total_corrections = 0
    
    # =========================================================================
    # ESPAÑOL COLOMBIA (es_CO)
    # =========================================================================
    
    es_co_corrections = [
        # CRÍTICO: "No tienes permisos..." traducido como "No hay... registradas"
        (
            "No tienes permisos para crear divisiones administrativas.",
            "No hay divisiones administrativas registradas.",
            "No tienes permisos para crear divisiones administrativas.",
            "Permisos ADM - No confundir permisos con lista vacía"
        ),
        
        # CRÍTICO: "No hay relaciones país-indicador" traducido como "No hay ubicaciones"
        (
            "No hay relaciones país-indicador registradas.",
            "No hay ubicaciones registradas.",
            "No hay relaciones país-indicador registradas.",
            "Country Indicator - Texto lista vacía incorrecto"
        ),
        
        # MEDIO: Traducciones cortas sospechosas
        (
            "Divisiones administrativas - Nivel 1",
            "Departamentos",
            "Divisiones Administrativas - Nivel 1 (Departamentos)",
            "ADM1 - Título completo más descriptivo"
        ),
        
        (
            "Divisiones administrativas - Nivel 2",
            "Municipios",
            "Divisiones Administrativas - Nivel 2 (Municipios)",
            "ADM2 - Título completo más descriptivo"
        ),
    ]
    
    corrections = fix_po_file(
        'app/translations/es_CO/LC_MESSAGES/messages.po',
        es_co_corrections
    )
    total_corrections += corrections
    
    # =========================================================================
    # ESPAÑOL GUATEMALA (es_GT)
    # =========================================================================
    
    es_gt_corrections = [
        # CRÍTICO: "No tienes permisos..." traducido como "No hay... registradas"
        (
            "No tienes permisos para crear divisiones administrativas.",
            "No hay divisiones administrativas registradas.",
            "No tienes permisos para crear divisiones administrativas.",
            "Permisos ADM - No confundir permisos con lista vacía"
        ),
        
        # CRÍTICO: "No hay relaciones país-indicador" traducido como "No hay ubicaciones"
        (
            "No hay relaciones país-indicador registradas.",
            "No hay ubicaciones registradas.",
            "No hay relaciones país-indicador registradas.",
            "Country Indicator - Texto lista vacía incorrecto"
        ),
        
        # CRÍTICO: "No hay categorías" traducido como "No hay temporadas"
        (
            "No hay categorías registradas.",
            "No hay temporadas registradas.",
            "No hay categorías registradas.",
            "Indicator Category - Texto lista vacía incorrecto"
        ),
        
        # MEDIO: Traducciones cortas sospechosas
        (
            "Divisiones administrativas - Nivel 1",
            "Provincias",
            "Divisiones Administrativas - Nivel 1 (Provincias)",
            "ADM1 - Título completo más descriptivo"
        ),
        
        (
            "Divisiones administrativas - Nivel 2",
            "Municipios",
            "Divisiones Administrativas - Nivel 2 (Municipios)",
            "ADM2 - Título completo más descriptivo"
        ),
    ]
    
    corrections = fix_po_file(
        'app/translations/es_GT/LC_MESSAGES/messages.po',
        es_gt_corrections
    )
    total_corrections += corrections
    
    # =========================================================================
    # INGLÉS (en_US)
    # =========================================================================
    
    en_us_corrections = [
        # CRÍTICO: "Error al crear la temporada" traducido como "Add season"
        (
            "Error al crear la temporada: {}",
            "Add season",
            "Error creating season: {}",
            "Season Error - Mensaje de error traducido como acción"
        ),
        
        # CRÍTICO: "Editar división administrativa" traducido como "Edit countie" (sin s)
        (
            "Editar división administrativa - Nivel 2",
            "Edit countie",
            "Edit Administrative Division - Level 2",
            "ADM2 Edit - Typo 'countie' corregido"
        ),
        
        # MEDIO: "Divisiones administrativas - Nivel 2" traducido como "Countie" (sin s)
        (
            "Divisiones administrativas - Nivel 2",
            "Countie",
            "Administrative Divisions - Level 2 (Counties)",
            "ADM2 List - Typo 'countie' corregido y título completo"
        ),
        
        # MEDIO: Traducciones cortas
        (
            "Divisiones administrativas - Nivel 1",
            "States",
            "Administrative Divisions - Level 1 (States)",
            "ADM1 - Título completo más descriptivo"
        ),
        
        (
            "Nivel administrativo 2",
            "Counties",
            "Administrative Level 2 (Counties)",
            "ADM2 Form - Título completo más descriptivo"
        ),
    ]
    
    corrections = fix_po_file(
        'app/translations/en_US/LC_MESSAGES/messages.po',
        en_us_corrections
    )
    total_corrections += corrections
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    
    print("\n" + "="*80)
    print("📊 RESUMEN DE CORRECCIONES")
    print("="*80)
    print(f"\n   Total de traducciones corregidas: {total_corrections}")
    
    if total_corrections > 0:
        print("\n   ✅ Correcciones aplicadas exitosamente")
        print("\n   🔄 Próximos pasos:")
        print("      1. Revisar los cambios")
        print("      2. Recompilar traducciones:")
        print("         pybabel compile -d app/translations")
        print("      3. Reiniciar el servidor Flask")
        print("      4. Limpiar caché del navegador (Ctrl + Shift + R)")
    else:
        print("\n   ℹ️  No se encontraron problemas que corregir")
    
    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    main()
