from typing import List, Dict
import requests
from flask import current_app, session
from config import Config

class RoleService:
    """Servicio para manejar roles desde la API"""
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Obtener headers de autenticación"""
        token = session.get('access_token')
        if token:
            return {'Authorization': f'Bearer {token}'}
        return {}
    
    def _normalize_role_data(self, api_role: Dict) -> Dict:
        """Convierte la estructura de la API a la estructura interna"""
        role_name = api_role.get('name', '')
        return {
            'id': api_role.get('id'),
            'name': role_name,
            'display_name': role_name,  # Usar el mismo nombre que viene de la API
            'description': api_role.get('description', ''),
            'composite': api_role.get('composite', False),
            'client_role': api_role.get('clientRole', True),
            'container_id': api_role.get('containerId', '')
        }
    
    def get_all(self) -> List[Dict]:
        """Obtener todos los roles desde la API"""
        try:
            response = requests.get(
                f"{Config.API_BASE_URL}/users/get-client-roles",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            current_app.logger.info(f"Roles API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                api_response = response.json()
                
                # Log para ver qué estructura tiene la respuesta
                current_app.logger.info(f"API Response type: {type(api_response)}")
                current_app.logger.info(f"API Response keys (if dict): {list(api_response.keys()) if isinstance(api_response, dict) else 'Not a dict'}")
                current_app.logger.info(f"API Response sample: {str(api_response)[:500]}...")
                
                # Manejar diferentes formatos de respuesta
                roles_data = []
                
                if isinstance(api_response, list):
                    # Respuesta directa como lista
                    roles_data = api_response
                elif isinstance(api_response, dict):
                    # Respuesta como diccionario, buscar la lista de roles
                    if 'roles' in api_response:
                        roles_data = api_response['roles']
                    elif 'data' in api_response:
                        roles_data = api_response['data']
                    elif 'items' in api_response:
                        roles_data = api_response['items']
                    elif 'results' in api_response:
                        roles_data = api_response['results']
                    else:
                        # Si no encontramos una clave conocida, logeemos todas las claves
                        current_app.logger.error(f"Could not find roles array in dict response. Available keys: {list(api_response.keys())}")
                        return []
                
                # Verificar que ahora tenemos una lista
                if not isinstance(roles_data, list):
                    current_app.logger.error(f"Expected list but got {type(roles_data)} for roles data")
                    return []
                
                # Normalizar los roles
                normalized_roles = []
                for api_role in roles_data:
                    try:
                        normalized_role = self._normalize_role_data(api_role)
                        normalized_roles.append(normalized_role)
                    except Exception as e:
                        current_app.logger.error(f"Error normalizing role {api_role.get('name', 'unknown')}: {e}")
                        continue
                
                current_app.logger.info(f"Successfully loaded {len(normalized_roles)} roles")
                return normalized_roles
            
            elif response.status_code == 401:
                current_app.logger.error("Unauthorized access to roles API - token may be expired")
                return []
            elif response.status_code == 403:
                current_app.logger.error("Forbidden access to roles API - insufficient permissions")
                return []
            else:
                current_app.logger.error(f"Error fetching roles from API: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            current_app.logger.error("Timeout connecting to roles API")
            return []
        except requests.exceptions.ConnectionError:
            current_app.logger.error("Connection error to roles API")
            return []
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error connecting to roles API: {e}")
            return []
        except Exception as e:
            current_app.logger.error(f"Unexpected error in RoleService.get_all: {e}")
            return []

    def create(self, name: str, description: str = "", composite: bool = False) -> Dict:
        """Crear un nuevo rol"""
        try:
            print(f"Attempting to create role: {name}")
            
            # Preparar datos para la API
            role_data = {
                "name": name,
                "description": description,
                "composite": composite
            }
            
            print(f"Creating role with data: {role_data}")
            
            # Asegurar que Content-Type esté en los headers
            headers = self._get_auth_headers()
            headers['Content-Type'] = 'application/json'
            
            response = requests.post(
                f"{Config.API_BASE_URL}/roles/create",
                headers=headers,
                json=role_data,
                timeout=10
            )
            
            print(f"Create role response status: {response.status_code}")
            print(f"Create role response content: {response.text}")
            
            if response.status_code == 200:
                # Rol creado exitosamente
                print("Rol creado con éxito en la API")
                
                if response.content:
                    try:
                        api_response = response.json()
                        
                        # Si la respuesta contiene el rol creado, normalizarlo
                        if isinstance(api_response, dict) and 'id' in api_response:
                            normalized_role = self._normalize_role_data(api_response)
                            print(f"Rol normalizado: {normalized_role}")
                            return normalized_role
                        
                        # Si la respuesta tiene un mensaje y ID
                        elif isinstance(api_response, dict) and 'role_id' in api_response:
                            role_id = api_response.get('role_id')
                            message = api_response.get('message', '')
                            print(f"API Response: {api_response}")
                            
                            # Crear respuesta normalizada
                            return {
                                'id': role_id,
                                'name': name,
                                'display_name': name,
                                'description': description,
                                'composite': composite,
                                'client_role': True,
                                'container_id': ''
                            }
                        
                        else:
                            print(f"Unexpected response format: {api_response}")
                            # Crear respuesta básica
                            return {
                                'id': 'temp_id',
                                'name': name,
                                'display_name': name,
                                'description': description,
                                'composite': composite,
                                'client_role': True,
                                'container_id': ''
                            }
                            
                    except Exception as json_error:
                        print(f"Error parsing create role response: {json_error}")
                        return {
                            'id': 'temp_id',
                            'name': name,
                            'display_name': name,
                            'description': description,
                            'composite': composite,
                            'client_role': True,
                            'container_id': ''
                        }
                else:
                    # Sin contenido en la respuesta
                    return {
                        'id': 'temp_id',
                        'name': name,
                        'display_name': name,
                        'description': description,
                        'composite': composite,
                        'client_role': True,
                        'container_id': ''
                    }
                    
            elif response.status_code == 201:
                # Rol creado exitosamente (código estándar para creación)
                print("Rol creado con éxito (201)")
                
                if response.content:
                    try:
                        api_role = response.json()
                        normalized_role = self._normalize_role_data(api_role)
                        print(f"Rol normalizado: {normalized_role}")
                        return normalized_role
                    except Exception as json_error:
                        print(f"Error parsing JSON response: {json_error}")
                        return {
                            'id': 'temp_id',
                            'name': name,
                            'display_name': name,
                            'description': description,
                            'composite': composite,
                            'client_role': True,
                            'container_id': ''
                        }
            
            elif response.status_code == 400:
                # Error de validación
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Error de validación')
                    print(f"Error 400 de la API: {error_msg}")
                    raise ValueError(error_msg)
                except ValueError:
                    raise  # Re-lanzar ValueError
                except:
                    raise ValueError('Error de validación en los datos del rol')
            
            elif response.status_code == 409:
                # Rol ya existe
                print("Error 409: Rol ya existe")
                raise ValueError('Ya existe un rol con ese nombre')
            
            elif response.status_code == 403:
                # Sin permisos
                print("Error 403: Sin permisos para crear roles")
                raise ValueError('No tienes permisos para crear roles')
            
            else:
                print(f"Error inesperado de la API: {response.status_code}")
                raise Exception(f"Error del servidor: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            print("Error: Timeout en la conexión")
            current_app.logger.error("Timeout connecting to create role API")
            raise Exception("Tiempo de espera agotado - intenta nuevamente")
        
        except requests.exceptions.ConnectionError:
            print("Error: Error de conexión")
            current_app.logger.error("Connection error to create role API")
            raise Exception("Error de conexión con el servidor")
        
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            current_app.logger.error(f"Error connecting to create role API: {e}")
            raise Exception("Error de conexión con el servidor")
        
        except ValueError as e:
            print(f"Error de validación: {e}")
            raise  # Re-lanzar errores de validación
        
        except Exception as e:
            print(f"Error inesperado en create: {e}")
            current_app.logger.error(f"Unexpected error creating role: {e}")
            raise Exception(f"Error inesperado: {str(e)}")