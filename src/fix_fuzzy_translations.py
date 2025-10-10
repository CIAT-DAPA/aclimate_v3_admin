#!/usr/bin/env python3
"""
Script para limpiar marcadores fuzzy y completar traducciones de indicadores
"""

file_paths = [
    r"app\translations\es_CO\LC_MESSAGES\messages.po",
    r"app\translations\es_GT\LC_MESSAGES\messages.po",
    r"app\translations\en_US\LC_MESSAGES\messages.po",
]

# Traducciones específicas para indicadores
es_translations = {
    "Indicators": "Indicadores",
    "Indicators management": "Gestión de indicadores",
    "Indicators category management": "Gestión de categorías de indicadores",
    "Country indicator": "Indicador por país",
}

en_translations = {
    "Indicators": "Indicators",
    "Indicators management": "Indicators management",
    "Indicators category management": "Indicators category management",
    "Country indicator": "Country indicator",
}

gt_translations = es_translations.copy()  # Guatemala usa las mismas traducciones que Colombia

for file_path in file_paths:
    print(f"\n=== Procesando {file_path} ===")
    
    # Determinar qué diccionario usar
    if 'en_US' in file_path:
        translations = en_translations
    elif 'es_GT' in file_path:
        translations = gt_translations
    else:  # es_CO
        translations = es_translations
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Procesar líneas
    output = []
    skip_next_fuzzy = False
    current_msgid = None
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Eliminar líneas con #, fuzzy
        if line.strip().startswith('#, fuzzy'):
            print(f"  ✓ Removido fuzzy para: {current_msgid}")
            i += 1
            continue
        
        # Detectar msgid
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            current_msgid = line[7:-2]  # Remover 'msgid "' y '"\n'
        
        # Reemplazar msgstr vacío si tenemos traducción
        if line.startswith('msgstr ""') and line.strip() == 'msgstr ""':
            if current_msgid and current_msgid in translations:
                output.append(f'msgstr "{translations[current_msgid]}"\n')
                print(f"  ✓ Traducido: {current_msgid} -> {translations[current_msgid]}")
                i += 1
                continue
        
        # Reemplazar msgstr existente si es fuzzy
        if line.startswith('msgstr "') and current_msgid in translations:
            # Verificar si la línea anterior era fuzzy (ya eliminada)
            if len(output) > 0 and not output[-1].startswith('#, fuzzy'):
                # Solo reemplazar si es diferente
                existing = line[8:-2]  # Extraer traducción existente
                if existing != translations[current_msgid]:
                    output.append(f'msgstr "{translations[current_msgid]}"\n')
                    print(f"  ✓ Actualizado: {current_msgid} -> {translations[current_msgid]}")
                    i += 1
                    continue
        
        output.append(line)
        i += 1
    
    # Guardar archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(output)
    
    print(f"  ✅ Archivo actualizado")

print("\n✅ Todos los archivos procesados")
