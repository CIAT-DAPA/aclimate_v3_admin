from typing import List, Dict
from datetime import datetime
import requests
from flask import current_app, session
from config import Config

class UserService:
    """Servicio para manejar usuarios"""
    def _get_auth_headers(self) -> Dict[str, str]:
        """Obtener headers de autenticación"""
        token = session.get('access_token')
        if token:
            return {'Authorization': f'Bearer {token}'}
        return {}
    
    def _normalize_user_data(self, api_user: Dict) -> Dict:
        """Convierte la estructura de la API a la estructura interna"""
        # Obtener el primer rol o asignar valores por defecto
        client_roles = api_user.get('client_roles', [])
        if client_roles:
            first_role = client_roles[0]
            role_id = first_role.get('id', 'unknown')
            role_name = first_role.get('name', 'Unknown')
        else:
            role_id = 'guest'
            role_name = 'Guest'
        
        # Convertir timestamp de milisegundos a datetime
        created_timestamp = api_user.get('createdTimestamp', 0)
        created_at = datetime.fromtimestamp(created_timestamp / 1000) if created_timestamp else datetime.now()
        
        return {
            'id': api_user.get('id'),
            'username': api_user.get('username'),
            'email': api_user.get('email'),
            'first_name': api_user.get('firstName', ''),
            'last_name': api_user.get('lastName', ''),
            'role_id': role_id,
            'role_name': role_name,
            'enabled': api_user.get('enabled', True),
            'email_verified': api_user.get('emailVerified', False),
            'created_timestamp': created_timestamp,
            'created_at': created_at,
            'updated_at': created_at,
            'totp': api_user.get('totp', False),
            'access': api_user.get('access', {}),
            'client_roles': client_roles
        }
    
    def get_all(self) -> List[Dict]:
        """Obtener todos los usuarios desde la API"""
        try:
            response = requests.get(
                f"{Config.API_BASE_URL}/users/get-users",
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            print(f"API Response Status: {response.status_code}")
            print(f"API Response Content: {response.text[:500]}...")
            
            if response.status_code == 200:
                api_users = response.json()
                
                # La respuesta es una lista directamente
                if isinstance(api_users, list):
                    normalized_users = []
                    for api_user in api_users:
                        try:
                            normalized_user = self._normalize_user_data(api_user)
                            normalized_users.append(normalized_user)
                        except Exception as e:
                            current_app.logger.error(f"Error normalizing user {api_user.get('id', 'unknown')}: {e}")
                            continue
                    
                    return normalized_users
                
                else:
                    current_app.logger.error(f"Unexpected API response format: {type(api_users)}")
                    return []
            else:
                current_app.logger.error(f"Error fetching users from API: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error connecting to users API: {e}")
            return []
        except Exception as e:
            current_app.logger.error(f"Unexpected error in get_all: {e}")
            return []
        
    def create(self, username: str, email: str, first_name: str, last_name: str, password: str) -> Dict:
        """Crear nuevo usuario en la API"""
        try:
            # Preparar el payload según la estructura que espera la API
            user_data = {
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "emailVerified": False,
                "enabled": True,
                "attributes": {},
                "credentials": [
                    {
                        "type": "password",
                        "value": password,
                        "temporary": False
                    }
                ]
            }
            
            print(f"Creating user with data: {user_data}")
            
            # Asegurar que Content-Type esté en los headers
            headers = self._get_auth_headers()
            headers['Content-Type'] = 'application/json'
            
            response = requests.post(
                f"{Config.API_BASE_URL}/users/create-user",
                headers=headers,
                json=user_data,
                timeout=10
            )
            
            print(f"Create user response status: {response.status_code}")
            print(f"Create user response content: {response.text}")
            
            # Tu API devuelve 200 en lugar de 201
            if response.status_code == 200:
                # Usuario creado exitosamente
                print("Usuario creado con éxito en la API")
                
                # Tu API devuelve: {"message":"User created and 'webadminsimple' role assigned successfully","user_id":"f0ceba5f-eada-484c-ba54-95f0f2bbb8c6"}
                if response.content:
                    try:
                        api_response = response.json()
                        user_id = api_response.get('user_id')
                        message = api_response.get('message', '')
                        
                        print(f"API Response: {api_response}")
                        
                        # Crear una respuesta normalizada con la información disponible
                        return {
                            'id': user_id,
                            'username': username,
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'role_id': 'webadminsimple',  # Extraído del mensaje
                            'role_name': 'Web Admin Simple',
                            'enabled': True,
                            'email_verified': False,
                            'created_timestamp': int(datetime.now().timestamp() * 1000),
                            'created_at': datetime.now(),
                            'updated_at': datetime.now(),
                            'api_message': message
                        }
                        
                    except Exception as json_error:
                        print(f"Error parsing JSON response: {json_error}")
                        # Si no puede parsear la respuesta, crear una respuesta simulada
                        return {
                            'id': 'temp_id',
                            'username': username,
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'role_id': 'guest',
                            'role_name': 'Guest',
                            'enabled': True,
                            'email_verified': False,
                            'created_timestamp': int(datetime.now().timestamp() * 1000),
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        }
                else:
                    # Sin contenido
                    print("API devolvió 200 sin contenido")
                    return {
                        'id': 'created_successfully',
                        'username': username,
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'role_id': 'guest',
                        'role_name': 'Guest',
                        'enabled': True,
                        'email_verified': False,
                        'created_timestamp': int(datetime.now().timestamp() * 1000),
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
            
            elif response.status_code == 201:
                # Por si acaso también acepta 201
                print("Usuario creado con éxito en la API (201)")
                if response.content:
                    try:
                        api_user = response.json()
                        normalized_user = self._normalize_user_data(api_user)
                        print(f"Usuario normalizado: {normalized_user}")
                        return normalized_user
                    except Exception as json_error:
                        print(f"Error parsing JSON response: {json_error}")
                        return {
                            'id': 'temp_id',
                            'username': username,
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'role_id': 'guest',
                            'role_name': 'Guest',
                            'enabled': True,
                            'email_verified': False,
                            'created_timestamp': int(datetime.now().timestamp() * 1000),
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
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
                    raise ValueError('Error de validación en los datos del usuario')
            
            elif response.status_code == 409:
                # Usuario ya existe
                print("Error 409: Usuario ya existe")
                raise ValueError('Ya existe un usuario con ese nombre de usuario o email')
            
            else:
                print(f"Error inesperado de la API: {response.status_code}")
                raise Exception(f"Error del servidor: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            current_app.logger.error(f"Error connecting to create user API: {e}")
            raise Exception("Error de conexión con el servidor")
        
        except ValueError as e:
            print(f"Error de validación: {e}")
            raise  # Re-lanzar errores de validación
        
        except Exception as e:
            print(f"Error inesperado en create: {e}")
            current_app.logger.error(f"Unexpected error creating user: {e}")
            raise Exception(f"Error inesperado: {str(e)}")