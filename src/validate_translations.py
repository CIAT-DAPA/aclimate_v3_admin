"""
Script para validar traducciones y detectar patrones sospechosos.
Ejecutar desde: src/
"""

import re
import os
from collections import defaultdict

class TranslationValidator:
    def __init__(self, po_file_path, language_code):
        self.po_file = po_file_path
        self.language = language_code
        self.warnings = []
        self.errors = []
        
    def parse_po_file(self):
        """Parse el archivo .po y extrae msgid/msgstr pairs"""
        translations = []
        
        with open(self.po_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_msgid = None
        current_msgstr = None
        current_location = None
        line_number = 0
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Ubicación del mensaje
            if line.startswith('#:'):
                current_location = line[2:].strip()
                line_number = i
                
            # msgid
            elif line.startswith('msgid "'):
                current_msgid = line[7:-1]  # Remover 'msgid "' y '"'
                
            # msgstr
            elif line.startswith('msgstr "'):
                current_msgstr = line[8:-1]  # Remover 'msgstr "' y '"'
                
                if current_msgid and current_msgstr:
                    translations.append({
                        'msgid': current_msgid,
                        'msgstr': current_msgstr,
                        'location': current_location,
                        'line': line_number
                    })
                    current_msgid = None
                    current_msgstr = None
                    
        return translations
    
    def check_identical_translations(self, translations):
        """Detecta traducciones idénticas (sospechoso excepto para términos técnicos)"""
        known_technical_terms = [
            'ID', 'GPS', 'CSV', 'API', 'URL', 'HTTP', 'HTTPS', 'JSON',
            'OK', 'Email', 'Admin', 'ext_id'
        ]
        
        for trans in translations:
            msgid = trans['msgid']
            msgstr = trans['msgstr']
            
            # Ignorar traducciones vacías
            if not msgid or not msgstr:
                continue
            
            # Traducción idéntica
            if msgid == msgstr:
                # Verificar si es un término técnico conocido
                if msgid not in known_technical_terms and len(msgid) > 3:
                    self.warnings.append({
                        'type': 'IDENTICAL_TRANSLATION',
                        'severity': 'medium',
                        'line': trans['line'],
                        'location': trans['location'],
                        'msgid': msgid,
                        'msgstr': msgstr,
                        'message': f"Traducción idéntica al original (puede ser intencional)"
                    })
    
    def check_length_discrepancies(self, translations):
        """Detecta traducciones mucho más largas o cortas que el original"""
        for trans in translations:
            msgid = trans['msgid']
            msgstr = trans['msgstr']
            
            # Ignorar traducciones vacías
            if not msgid or not msgstr:
                continue
            
            len_msgid = len(msgid)
            len_msgstr = len(msgstr)
            
            # Traducción excesivamente larga (más del doble)
            if len_msgstr > len_msgid * 2.5 and len_msgid > 10:
                self.warnings.append({
                    'type': 'TOO_LONG',
                    'severity': 'low',
                    'line': trans['line'],
                    'location': trans['location'],
                    'msgid': msgid,
                    'msgstr': msgstr,
                    'message': f"Traducción muy larga ({len_msgstr} chars vs {len_msgid} chars original)"
                })
            
            # Traducción excesivamente corta (menos de la mitad)
            elif len_msgstr < len_msgid * 0.4 and len_msgid > 15 and len_msgstr > 5:
                self.warnings.append({
                    'type': 'TOO_SHORT',
                    'severity': 'low',
                    'line': trans['line'],
                    'location': trans['location'],
                    'msgid': msgid,
                    'msgstr': msgstr,
                    'message': f"Traducción muy corta ({len_msgstr} chars vs {len_msgid} chars original)"
                })
    
    def check_missing_translations(self, translations):
        """Detecta traducciones vacías"""
        for trans in translations:
            msgid = trans['msgid']
            msgstr = trans['msgstr']
            
            # Traducción vacía (pero msgid no vacío)
            if msgid and not msgstr:
                self.errors.append({
                    'type': 'MISSING_TRANSLATION',
                    'severity': 'high',
                    'line': trans['line'],
                    'location': trans['location'],
                    'msgid': msgid,
                    'msgstr': msgstr,
                    'message': f"Traducción faltante"
                })
    
    def check_placeholder_consistency(self, translations):
        """Verifica que los placeholders (variables) estén presentes en ambos lados"""
        for trans in translations:
            msgid = trans['msgid']
            msgstr = trans['msgstr']
            
            # Ignorar traducciones vacías
            if not msgid or not msgstr:
                continue
            
            # Buscar placeholders tipo %(variable)s, {variable}, %s, etc.
            placeholders_msgid = set(re.findall(r'%\([^)]+\)[sd]|%[sd]|\{[^}]+\}', msgid))
            placeholders_msgstr = set(re.findall(r'%\([^)]+\)[sd]|%[sd]|\{[^}]+\}', msgstr))
            
            # Placeholders faltantes en la traducción
            missing = placeholders_msgid - placeholders_msgstr
            if missing:
                self.errors.append({
                    'type': 'MISSING_PLACEHOLDERS',
                    'severity': 'high',
                    'line': trans['line'],
                    'location': trans['location'],
                    'msgid': msgid,
                    'msgstr': msgstr,
                    'message': f"Faltan placeholders en la traducción: {', '.join(missing)}"
                })
            
            # Placeholders extra en la traducción
            extra = placeholders_msgstr - placeholders_msgid
            if extra:
                self.errors.append({
                    'type': 'EXTRA_PLACEHOLDERS',
                    'severity': 'high',
                    'line': trans['line'],
                    'location': trans['location'],
                    'msgid': msgid,
                    'msgstr': msgstr,
                    'message': f"Placeholders extra en la traducción: {', '.join(extra)}"
                })
    
    def check_common_mistakes(self, translations):
        """Detecta errores comunes de traducción"""
        # Patrones sospechosos en español
        suspicious_patterns = {
            'es_CO': [
                (r'\bno hay\b.*\bregistrad', 'Importar|Upload|Create'),  # "No hay X registrados" usado para "Importar"
                (r'\bAcciones\b', 'Instructions|Instrucciones'),  # "Acciones" usado para "Instrucciones"
                (r'\bUbicaciones\b$', 'Back|Volver'),  # "Ubicaciones" solo usado para "Volver a Ubicaciones"
                (r'\bInformación del usuario\b', 'Format|CSV'),  # "Información del usuario" usado para "Formato"
            ],
            'es_GT': [
                (r'\bno hay\b.*\bregistrad', 'Importar|Upload|Create'),
                (r'\bAcciones\b', 'Instructions|Instrucciones'),
            ]
        }
        
        if self.language not in suspicious_patterns:
            return
        
        for trans in translations:
            msgid = trans['msgid']
            msgstr = trans['msgstr']
            
            if not msgid or not msgstr:
                continue
            
            # Verificar patrones sospechosos
            for pattern, conflicting in suspicious_patterns[self.language]:
                if re.search(pattern, msgstr, re.IGNORECASE):
                    # Verificar si el msgid NO contiene las palabras conflictivas
                    if not re.search(conflicting, msgid, re.IGNORECASE):
                        self.warnings.append({
                            'type': 'SUSPICIOUS_PATTERN',
                            'severity': 'high',
                            'line': trans['line'],
                            'location': trans['location'],
                            'msgid': msgid,
                            'msgstr': msgstr,
                            'message': f"Patrón sospechoso detectado: '{pattern}' en traducción no relacionada"
                        })
    
    def check_duplicate_translations(self, translations):
        """Detecta si diferentes msgid tienen la misma traducción"""
        msgstr_to_msgids = defaultdict(list)
        
        for trans in translations:
            msgid = trans['msgid']
            msgstr = trans['msgstr']
            
            if msgid and msgstr and len(msgstr) > 5:
                msgstr_to_msgids[msgstr].append({
                    'msgid': msgid,
                    'line': trans['line'],
                    'location': trans['location']
                })
        
        # Buscar traducciones duplicadas
        for msgstr, msgids in msgstr_to_msgids.items():
            if len(msgids) > 1:
                # Verificar que los msgid sean realmente diferentes
                unique_msgids = set([m['msgid'] for m in msgids])
                if len(unique_msgids) > 1:
                    self.warnings.append({
                        'type': 'DUPLICATE_TRANSLATION',
                        'severity': 'medium',
                        'msgstr': msgstr,
                        'msgids': [m['msgid'] for m in msgids],
                        'locations': [m['location'] for m in msgids],
                        'message': f"La misma traducción '{msgstr}' se usa para {len(unique_msgids)} textos diferentes"
                    })
    
    def validate(self):
        """Ejecuta todas las validaciones"""
        print(f"\n{'='*80}")
        print(f"Validando traducciones: {self.language}")
        print(f"Archivo: {self.po_file}")
        print(f"{'='*80}\n")
        
        translations = self.parse_po_file()
        print(f"📊 Total de traducciones: {len(translations)}\n")
        
        # Ejecutar todas las validaciones
        self.check_missing_translations(translations)
        self.check_identical_translations(translations)
        self.check_length_discrepancies(translations)
        self.check_placeholder_consistency(translations)
        self.check_common_mistakes(translations)
        self.check_duplicate_translations(translations)
        
        # Reportar errores
        if self.errors:
            print(f"❌ ERRORES ({len(self.errors)}):")
            print("=" * 80)
            for error in self.errors:
                print(f"\n🔴 {error['type']} (Línea {error.get('line', '?')})")
                print(f"   Severidad: {error['severity'].upper()}")
                if error.get('location'):
                    print(f"   Ubicación: {error['location']}")
                print(f"   msgid:  \"{error['msgid']}\"")
                print(f"   msgstr: \"{error['msgstr']}\"")
                print(f"   ⚠️  {error['message']}")
        
        # Reportar advertencias
        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS ({len(self.warnings)}):")
            print("=" * 80)
            
            # Agrupar por tipo
            warnings_by_type = defaultdict(list)
            for warning in self.warnings:
                warnings_by_type[warning['type']].append(warning)
            
            for warning_type, warnings in warnings_by_type.items():
                print(f"\n🟡 {warning_type} ({len(warnings)} casos):")
                print("-" * 80)
                
                for warning in warnings[:10]:  # Mostrar máximo 10 por tipo
                    if warning.get('line'):
                        print(f"\n   Línea {warning['line']}")
                    if warning.get('location'):
                        print(f"   Ubicación: {warning['location']}")
                    if warning.get('msgid'):
                        print(f"   msgid:  \"{warning['msgid'][:80]}{'...' if len(warning['msgid']) > 80 else ''}\"")
                    if warning.get('msgstr'):
                        print(f"   msgstr: \"{warning['msgstr'][:80]}{'...' if len(warning['msgstr']) > 80 else ''}\"")
                    if warning.get('msgids'):
                        print(f"   msgids: {warning['msgids'][:3]}")
                    print(f"   💡 {warning['message']}")
                
                if len(warnings) > 10:
                    print(f"\n   ... y {len(warnings) - 10} casos más")
        
        # Resumen
        print(f"\n{'='*80}")
        print("📋 RESUMEN:")
        print(f"   ✅ Traducciones totales: {len(translations)}")
        print(f"   ❌ Errores: {len(self.errors)}")
        print(f"   ⚠️  Advertencias: {len(self.warnings)}")
        
        if not self.errors and not self.warnings:
            print("\n   🎉 ¡No se encontraron problemas!")
        
        print(f"{'='*80}\n")
        
        return {
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'total': len(translations)
        }


def main():
    """Valida todos los archivos de traducción"""
    
    # Configurar encoding UTF-8 para Windows
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    languages = [
        ('app/translations/es_CO/LC_MESSAGES/messages.po', 'es_CO'),
        ('app/translations/es_GT/LC_MESSAGES/messages.po', 'es_GT'),
        ('app/translations/en_US/LC_MESSAGES/messages.po', 'en_US'),
    ]
    
    total_errors = 0
    total_warnings = 0
    
    for po_file, lang_code in languages:
        if not os.path.exists(po_file):
            print(f"⚠️  Archivo no encontrado: {po_file}")
            continue
        
        validator = TranslationValidator(po_file, lang_code)
        results = validator.validate()
        
        total_errors += results['errors']
        total_warnings += results['warnings']
    
    # Resumen global
    print("\n" + "="*80)
    print("📊 RESUMEN GLOBAL DE VALIDACIÓN")
    print("="*80)
    print(f"   Total de errores: {total_errors}")
    print(f"   Total de advertencias: {total_warnings}")
    
    if total_errors == 0 and total_warnings == 0:
        print("\n   ✅ ¡Todas las traducciones están correctas!")
    elif total_errors == 0:
        print("\n   ⚠️  Hay algunas advertencias pero no errores críticos")
    else:
        print("\n   ❌ Se encontraron errores que deben corregirse")
    
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
