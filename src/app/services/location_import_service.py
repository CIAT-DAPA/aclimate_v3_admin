"""
Servicio para importar locaciones desde un archivo CSV
"""
import csv
import io
from typing import Dict, List, Tuple
from flask import current_app
from aclimate_v3_orm.services import (
    MngLocationService,
    MngAdmin1Service,
    MngAdmin2Service,
    MngSourceService,
    MngCountryService
)
from aclimate_v3_orm.schemas import LocationCreate, Admin1Create, Admin2Create, SourceCreate
from aclimate_v3_orm.enums import SourceType


class LocationImportService:
    """Servicio para importar locaciones desde CSV"""
    
    def __init__(self):
        self.location_service = MngLocationService()
        self.adm1_service = MngAdmin1Service()
        self.adm2_service = MngAdmin2Service()
        self.source_service = MngSourceService()
        self.country_service = MngCountryService()
    
    def import_from_csv(self, file_content: bytes, country_id: int) -> Dict:
        """
        Importa locaciones desde un archivo CSV
        
        Args:
            file_content: Contenido del archivo CSV en bytes
            country_id: ID del país para las locaciones
            
        Returns:
            Dict con estadísticas de la importación:
            {
                'locations_created': int,
                'locations_skipped': int,
                'adm1_created': int,
                'adm2_created': int,
                'errors': List[str]
            }
        """
        stats = {
            'locations_created': 0,
            'locations_skipped': 0,
            'adm1_created': 0,
            'adm2_created': 0,
            'sources_created': 0,
            'errors': []
        }
        
        # Cache para evitar consultas repetidas
        adm1_cache = {}  # {(name, ext_id): adm1_id}
        adm2_cache = {}  # {(name, ext_id, adm1_id): adm2_id}
        source_cache = {}  # {name: source_id}
        
        try:
            # Decodificar el contenido
            text_content = file_content.decode('utf-8-sig')  # utf-8-sig para manejar BOM
            csv_reader = csv.DictReader(io.StringIO(text_content))
            
            row_number = 1
            for row in csv_reader:
                row_number += 1
                try:
                    # Validar campos requeridos
                    required_fields = [
                        'ext_id', 'name', 'latitude', 'longitude', 'altitude',
                        'admin_level_1', 'admin_level_2', 'source_name'
                    ]
                    
                    missing_fields = [field for field in required_fields if not row.get(field, '').strip()]
                    if missing_fields:
                        stats['errors'].append(f"Fila {row_number}: Campos faltantes: {', '.join(missing_fields)}")
                        stats['locations_skipped'] += 1
                        continue
                    
                    # Verificar si la locación ya existe
                    existing_locations = self.location_service.get_by_ext_id(
                        ext_id=row['ext_id'].strip(),
                        enabled=True
                    )
                    
                    if not existing_locations:
                        # Buscar deshabilitadas
                        existing_locations = self.location_service.get_by_ext_id(
                            ext_id=row['ext_id'].strip(),
                            enabled=False
                        )
                    
                    if existing_locations and len(existing_locations) > 0:
                        current_app.logger.info(f"Locación {row['name']} ya existe (ext_id: {row['ext_id']})")
                        stats['locations_skipped'] += 1
                        continue
                    
                    # Procesar/crear ADM1
                    adm1_name = row['admin_level_1'].strip()
                    adm1_ext_id = row.get('ext_id_level_1', '').strip()
                    adm1_id = self._get_or_create_adm1(
                        name=adm1_name,
                        ext_id=adm1_ext_id,
                        country_id=country_id,
                        cache=adm1_cache,
                        stats=stats
                    )
                    
                    if not adm1_id:
                        stats['errors'].append(f"Fila {row_number}: No se pudo obtener/crear ADM1 '{adm1_name}'")
                        stats['locations_skipped'] += 1
                        continue
                    
                    # Procesar/crear ADM2
                    adm2_name = row['admin_level_2'].strip()
                    adm2_ext_id = row.get('ext_id_level_2', '').strip()
                    adm2_id = self._get_or_create_adm2(
                        name=adm2_name,
                        ext_id=adm2_ext_id,
                        adm1_id=adm1_id,
                        cache=adm2_cache,
                        stats=stats
                    )
                    
                    if not adm2_id:
                        stats['errors'].append(f"Fila {row_number}: No se pudo obtener/crear ADM2 '{adm2_name}'")
                        stats['locations_skipped'] += 1
                        continue
                    
                    # Obtener o crear source
                    source_name = row['source_name'].strip()
                    source_type = row.get('type_of_source', '').strip()
                    source_id, error = self._get_or_create_source(
                        name=source_name,
                        source_type=source_type,
                        cache=source_cache,
                        stats=stats
                    )
                    
                    # Si hay error con la fuente, omitir esta locación
                    if error:
                        stats['errors'].append(f"Fila {row_number}: {error}")
                        stats['locations_skipped'] += 1
                        continue
                    
                    if not source_id:
                        stats['errors'].append(f"Fila {row_number}: No se pudo obtener/crear fuente '{source_name}'")
                        stats['locations_skipped'] += 1
                        continue
                    
                    # Crear la locación
                    location_data = LocationCreate(
                        admin_2_id=adm2_id,
                        source_id=source_id,
                        name=row['name'].strip(),
                        ext_id=row['ext_id'].strip(),
                        latitude=float(row['latitude'].strip().replace(',', '.')),
                        longitude=float(row['longitude'].strip().replace(',', '.')),
                        altitude=float(row['altitude'].strip().replace(',', '.')),
                        enable=True,
                        visible=True
                    )
                    
                    self.location_service.create(location_data)
                    stats['locations_created'] += 1
                    current_app.logger.info(f"Locación creada: {row['name']}")
                    
                except ValueError as e:
                    stats['errors'].append(f"Fila {row_number}: Error de formato - {str(e)}")
                    stats['locations_skipped'] += 1
                except Exception as e:
                    current_app.logger.error(f"Error procesando fila {row_number}: {e}")
                    stats['errors'].append(f"Fila {row_number}: {str(e)}")
                    stats['locations_skipped'] += 1
                    
        except Exception as e:
            current_app.logger.error(f"Error general al importar CSV: {e}")
            stats['errors'].append(f"Error general: {str(e)}")
        
        return stats
    
    def _get_or_create_adm1(self, name: str, ext_id: str, country_id: int, 
                           cache: Dict, stats: Dict) -> int:
        """Obtiene o crea un ADM1"""
        cache_key = (name, ext_id)
        
        # Verificar cache
        if cache_key in cache:
            return cache[cache_key]
        
        # Buscar por ext_id si está disponible
        if ext_id:
            # Buscar habilitados
            existing = self.adm1_service.get_by_ext_id(ext_id, enabled=True)
            if existing:
                cache[cache_key] = existing.id
                return existing.id
            # Buscar deshabilitados
            existing = self.adm1_service.get_by_ext_id(ext_id, enabled=False)
            if existing:
                cache[cache_key] = existing.id
                return existing.id
        
        # Buscar por nombre
        existing_by_name = self.adm1_service.get_by_name(name, enabled=True)
        if existing_by_name and len(existing_by_name) > 0:
            adm1_id = existing_by_name[0].id
            cache[cache_key] = adm1_id
            return adm1_id
        
        # Buscar deshabilitados por nombre
        existing_by_name = self.adm1_service.get_by_name(name, enabled=False)
        if existing_by_name and len(existing_by_name) > 0:
            adm1_id = existing_by_name[0].id
            cache[cache_key] = adm1_id
            return adm1_id
        
        # Crear nuevo ADM1
        try:
            new_adm1 = Admin1Create(
                name=name,
                ext_id=ext_id,
                country_id=country_id,
                enable=True
            )
            created = self.adm1_service.create(new_adm1)
            stats['adm1_created'] += 1
            cache[cache_key] = created.id
            current_app.logger.info(f"ADM1 creado: {name} (ext_id: {ext_id})")
            return created.id
        except Exception as e:
            current_app.logger.error(f"Error creando ADM1 '{name}': {e}")
            return None
    
    def _get_or_create_adm2(self, name: str, ext_id: str, adm1_id: int,
                           cache: Dict, stats: Dict) -> int:
        """Obtiene o crea un ADM2"""
        cache_key = (name, ext_id, adm1_id)
        
        # Verificar cache
        if cache_key in cache:
            return cache[cache_key]
        
        # Buscar por ext_id si está disponible
        if ext_id:
            # Buscar habilitados
            existing = self.adm2_service.get_by_ext_id(ext_id, enabled=True)
            if existing:
                cache[cache_key] = existing.id
                return existing.id
            # Buscar deshabilitados
            existing = self.adm2_service.get_by_ext_id(ext_id, enabled=False)
            if existing:
                cache[cache_key] = existing.id
                return existing.id
        
        # Buscar por nombre y adm1_id
        existing_by_name = self.adm2_service.get_by_name(name, enabled=True)
        if existing_by_name and len(existing_by_name) > 0:
            # Verificar que pertenezca al mismo adm1
            for adm2 in existing_by_name:
                if adm2.admin_1_id == adm1_id:
                    cache[cache_key] = adm2.id
                    return adm2.id
        
        # Buscar deshabilitados
        existing_by_name = self.adm2_service.get_by_name(name, enabled=False)
        if existing_by_name and len(existing_by_name) > 0:
            # Verificar que pertenezca al mismo adm1
            for adm2 in existing_by_name:
                if adm2.admin_1_id == adm1_id:
                    cache[cache_key] = adm2.id
                    return adm2.id
        
        # Crear nuevo ADM2
        try:
            new_adm2 = Admin2Create(
                name=name,
                ext_id=ext_id,
                admin_1_id=adm1_id,
                visible=True,
                enable=True
            )
            created = self.adm2_service.create(new_adm2)
            stats['adm2_created'] += 1
            cache[cache_key] = created.id
            current_app.logger.info(f"ADM2 creado: {name} (ext_id: {ext_id})")
            return created.id
        except Exception as e:
            current_app.logger.error(f"Error creando ADM2 '{name}': {e}")
            return None
    
    def _get_or_create_source(self, name: str, source_type: str, cache: Dict, stats: Dict) -> tuple:
        """
        Obtiene o crea una fuente de datos
        
        Returns:
            tuple: (source_id, error_message) - error_message es None si no hay error
        """
        cache_key = (name, source_type)
        
        # Verificar cache
        if cache_key in cache:
            return (cache[cache_key], None)
        
        # Buscar fuente existente por nombre
        sources = self.source_service.get_all()
        for source in sources:
            if source.name.upper() == name.upper():
                cache[cache_key] = source.id
                return (source.id, None)
        
        # Fuente no existe, validar tipo antes de crear
        try:
            source_type_enum = SourceType(source_type.upper())
        except ValueError:
            # Tipo inválido - retornar error
            valid_types = ', '.join([st.value for st in SourceType])
            error_msg = f"Tipo de fuente inválido '{source_type}'. Valores válidos: {valid_types}"
            current_app.logger.error(f"Fuente '{name}': {error_msg}")
            return (None, error_msg)
        
        # Crear fuente con tipo válido
        try:
            new_source = SourceCreate(
                name=name,
                source_type=source_type_enum,
                enable=True
            )
            created = self.source_service.create(new_source)
            stats['sources_created'] += 1
            cache[cache_key] = created.id
            current_app.logger.info(f"Fuente creada: {name} (tipo: {source_type_enum.value})")
            return (created.id, None)
        except Exception as e:
            error_msg = f"Error creando fuente '{name}': {str(e)}"
            current_app.logger.error(error_msg)
            return (None, error_msg)
    
    def _get_source_id(self, source_name: str, cache: Dict) -> int:
        """Obtiene el ID de una fuente por nombre"""
        if source_name in cache:
            return cache[source_name]
        
        # Buscar todas las fuentes y filtrar por nombre
        sources = self.source_service.get_all()
        for source in sources:
            if source.name.upper() == source_name.upper():
                cache[source_name] = source.id
                return source.id
        
        return None
