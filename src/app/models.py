from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, role='admin'):
        self.id = id
        self.email = email
        self.password = password
        self.role = role
    
    def check_password(self, password):
        return self.password == password
    
    @staticmethod
    def get(email):
        # Por ahora solo tenemos un usuario hardcodeado
        if email == 'admin@test.com':
            return User(id=1, email='admin@test.com', password='123', role='admin')
        return None