#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir ERRORES CRÍTICOS en traducciones
- Elimina marcadores fuzzy
- Rellena traducciones vacías con el texto original (temporal)
- Corrige placeholders incorrectos

Uso: python3 fix_critical_errors.py
"""

import re
import sys
from pathlib import Path

# Configuración
LOCALES = ['es_CO', 'es_GT', 'en_US']
TRANSLATIONS_DIR = Path('app/translations')

def remove_fuzzy_markers(po_file):
    """Elimina todos los marcadores #, fuzzy de un archivo .po"""
    lines = po_file.read_text(encoding='utf-8').split('\n')
    new_lines = []
    skip_next_entry = False
    
    for i, line in enumerate(lines):
        if line.strip() == '#, fuzzy':
            # Marcar para eliminar la traducción fuzzy (msgstr siguiente)
            skip_next_entry = True
            print(f"   ⚠️  Eliminando marcador fuzzy en línea {i+1}")
            continue  # No incluir la línea #, fuzzy
        
        if skip_next_entry and line.startswith('msgstr'):
            # Si el msgstr está vacío o es fuzzy, usar el msgid como fallback
            next_msgid = None
            for j in range(i-1, -1, -1):
                if lines[j].startswith('msgid'):
                    next_msgid = lines[j]
                    break
            
            if next_msgid and 'msgid ""' not in next_msgid:
                # Extraer el texto del msgid
                msgid_text = re.search(r'msgid\s+"(.+)"', next_msgid)
                if msgid_text:
                    original_text = msgid_text.group(1)
                    new_lines.append(f'msgstr "{original_text}"  # AUTO-FIXED: was fuzzy')
                    print(f"   🔧 Corregido msgstr vacío con: {original_text}")
                    skip_next_entry = False
                    continue
            
            skip_next_entry = False
        
        new_lines.append(line)
    
    po_file.write_text('\n'.join(new_lines), encoding='utf-8')

def fill_empty_translations(po_file):
    """Rellena traducciones vacías (msgstr "") con el texto original del msgid"""
    content = po_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    corrections = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Buscar msgid seguido de msgstr vacío
        if line.startswith('msgid "') and 'msgid ""' not in line:
            msgid_text = re.search(r'msgid\s+"(.+)"', line)
            
            # Verificar si el siguiente msgstr está vacío
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip() == 'msgstr ""' or next_line.strip() == 'msgstr':
                    if msgid_text:
                        original_text = msgid_text.group(1)
                        new_lines.append(line)
                        new_lines.append(f'msgstr "{original_text}"  # AUTO-FIXED: was empty')
                        corrections += 1
                        print(f"   🔧 Línea {i+2}: Rellenado msgstr vacío con '{original_text}'")
                        i += 2  # Saltar el msgstr original vacío
                        continue
        
        new_lines.append(line)
        i += 1
    
    if corrections > 0:
        po_file.write_text('\n'.join(new_lines), encoding='utf-8')
        print(f"   ✅ {corrections} traducciones vacías corregidas")
    
    return corrections

def fix_placeholder_consistency(po_file):
    """Corrige placeholders inconsistentes entre msgid y msgstr"""
    content = po_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    corrections = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Buscar msgid con placeholders
        if line.startswith('msgid "') and '%(' in line:
            msgid_placeholders = re.findall(r'%\([^)]+\)[sd]', line)
            
            # Verificar el msgstr correspondiente
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.startswith('msgstr "'):
                    msgstr_placeholders = re.findall(r'%\([^)]+\)[sd]', next_line)
                    
                    # Si los placeholders no coinciden, copiarlos del msgid
                    if set(msgid_placeholders) != set(msgstr_placeholders):
                        print(f"   ⚠️  Línea {i+2}: Placeholders inconsistentes")
                        print(f"      msgid:  {msgid_placeholders}")
                        print(f"      msgstr: {msgstr_placeholders}")
                        
                        # Reconstruir msgstr manteniendo el texto pero con placeholders correctos
                        # (Esto es complejo, por ahora solo advertir)
                        corrections += 1
        
        new_lines.append(line)
        i += 1
    
    if corrections > 0:
        print(f"   ⚠️  {corrections} placeholders inconsistentes detectados (requieren revisión manual)")
    
    return corrections

def main():
    print("="*80)
    print("🔧 CORRECCIÓN DE ERRORES CRÍTICOS EN TRADUCCIONES")
    print("="*80)
    print()
    
    total_fixes = 0
    
    for locale in LOCALES:
        po_file = TRANSLATIONS_DIR / locale / 'LC_MESSAGES' / 'messages.po'
        
        if not po_file.exists():
            print(f"❌ Archivo no encontrado: {po_file}")
            continue
        
        print(f"📝 Procesando: {locale}")
        print(f"   Archivo: {po_file}")
        print()
        
        # 1. Eliminar marcadores fuzzy
        print("   🔍 Eliminando marcadores fuzzy...")
        remove_fuzzy_markers(po_file)
        
        # 2. Rellenar traducciones vacías
        print("   🔍 Rellenando traducciones vacías...")
        empty_fixes = fill_empty_translations(po_file)
        total_fixes += empty_fixes
        
        # 3. Verificar placeholders
        print("   🔍 Verificando placeholders...")
        placeholder_issues = fix_placeholder_consistency(po_file)
        
        print()
    
    print("="*80)
    if total_fixes > 0:
        print(f"✅ CORRECCIONES APLICADAS: {total_fixes}")
        print()
        print("⚠️  IMPORTANTE:")
        print("   - Las traducciones vacías se rellenaron con el texto original")
        print("   - Esto es una solución TEMPORAL para evitar errores de compilación")
        print("   - Debes revisar y corregir manualmente estas traducciones después del deploy")
        print()
        print("   Buscar traducciones auto-corregidas:")
        print("   grep 'AUTO-FIXED' app/translations/*/LC_MESSAGES/messages.po")
    else:
        print("✅ No se encontraron errores críticos que corregir")
    print("="*80)
    
    return 0 if total_fixes == 0 else 1  # Exit 1 si hubo correcciones (para informar)

if __name__ == '__main__':
    sys.exit(main())
