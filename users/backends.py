from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class TenantAwareBackend(ModelBackend):
    """
    Backend de autenticación que verifica que el usuario pertenezca
    a la organización (tenant) desde la cual se está autenticando.

    Este backend extiende el ModelBackend estándar de Django y agrega
    una verificación adicional para asegurar que el usuario solo pueda
    iniciar sesión en el tenant al que pertenece.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica al usuario verificando:
        1. Credenciales válidas (username/password)
        2. Que el usuario pertenezca a la organización del tenant actual

        Args:
            request: HttpRequest con el tenant configurado
            username: Nombre de usuario
            password: Contraseña
            **kwargs: Argumentos adicionales

        Returns:
            User: Usuario autenticado si las credenciales son válidas y pertenece al tenant
            None: Si la autenticación falla por cualquier motivo
        """
        if username is None or password is None:
            return None

        # Obtener el tenant desde el request
        tenant = getattr(request, 'tenant', None)

        if tenant is None:
            # Si no hay tenant en el request, no permitir autenticación
            return None

        try:
            # Buscar el usuario por username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Usuario no existe
            return None

        # Verificar la contraseña
        if not user.check_password(password):
            return None

        # Verificar que el usuario esté activo
        if not self.user_can_authenticate(user):
            return None

        # VERIFICACIÓN CLAVE: Comprobar que el usuario pertenezca al tenant actual
        # Permitir usuarios sin organización (superusuarios) o del esquema público
        if tenant.schema_name == 'public':
            # En el esquema público, permitir cualquier usuario
            return user

        # Para otros tenants, verificar que la organización coincida
        if user.organization is None:
            # Usuario sin organización (superusuario global)
            # Permitir acceso solo si es superusuario
            if user.is_superuser:
                return user
            return None

        # Verificar que la organización del usuario coincida con el tenant
        if user.organization.id != tenant.id:
            # El usuario pertenece a una organización diferente
            return None

        # Todo está correcto: usuario válido para este tenant
        return user

    def get_user(self, user_id):
        """
        Obtiene un usuario por su ID.
        Método requerido por el backend de autenticación de Django.
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
