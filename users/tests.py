from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock
from users.backends import TenantAwareBackend
from organization.models import Organization
import uuid

User = get_user_model()


class TenantAwareBackendTestCase(TestCase):
    """
    Pruebas unitarias para el backend de autenticación TenantAwareBackend.
    Utiliza una base de datos de prueba de Django (SQLite por defecto).
    """

    def setUp(self):
        """
        Configura el entorno de prueba creando organizaciones y usuarios de prueba.
        """
        self.backend = TenantAwareBackend()

        # Crear organizaciones de prueba (instancias reales)
        self.org_a = Organization.objects.create(
            schema_name='org_a',
            name='Organización A'
        )

        self.org_b = Organization.objects.create(
            schema_name='org_b',
            name='Organización B'
        )

        self.org_public = Organization.objects.create(
            schema_name='public',
            name='Público'
        )

        # Crear usuario de Organización A
        self.user_org_a = User.objects.create_user(
            username='user_org_a',
            password='testpass123',
            email='user_a@test.com'
        )
        self.user_org_a.organization = self.org_a
        self.user_org_a.save()

        # Crear usuario de Organización B
        self.user_org_b = User.objects.create_user(
            username='user_org_b',
            password='testpass123',
            email='user_b@test.com'
        )
        self.user_org_b.organization = self.org_b
        self.user_org_b.save()

        # Crear superusuario sin organización
        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='adminpass123',
            email='admin@test.com'
        )
        self.superuser.organization = None
        self.superuser.save()

        # Crear usuario inactivo
        self.inactive_user = User.objects.create_user(
            username='inactive_user',
            password='testpass123',
            email='inactive@test.com',
            is_active=False
        )
        self.inactive_user.organization = self.org_a
        self.inactive_user.save()

    def _create_mock_request(self, tenant):
        """
        Crea un objeto request mockeado con un tenant específico.

        Args:
            tenant: Instancia de organización/tenant

        Returns:
            Mock: Objeto request con el atributo tenant configurado
        """
        request = Mock()
        request.tenant = tenant
        return request

    def test_usuario_correcto_en_su_tenant(self):
        """
        ✅ Caso 1: Usuario correcto intentando autenticarse en su propio tenant.
        Resultado esperado: Autenticación exitosa.
        """
        request = self._create_mock_request(self.org_a)

        user = self.backend.authenticate(
            request=request,
            username='user_org_a',
            password='testpass123'
        )

        self.assertIsNotNone(user, "El usuario debería autenticarse correctamente en su tenant")
        self.assertEqual(user.username, 'user_org_a')

    def test_usuario_correcto_en_tenant_diferente(self):
        """
        ❌ Caso 2: Usuario intentando autenticarse en un tenant diferente al suyo.
        Resultado esperado: Autenticación rechazada.
        """
        # Usuario de org_a intentando autenticarse en org_b
        request = self._create_mock_request(self.org_b)

        user = self.backend.authenticate(
            request=request,
            username='user_org_a',
            password='testpass123'
        )

        self.assertIsNone(user, "El usuario NO debería autenticarse en un tenant diferente")

    def test_superusuario_sin_organizacion_en_cualquier_tenant(self):
        """
        ✅ Caso 3: Superusuario sin organización accediendo a cualquier tenant.
        Resultado esperado: Autenticación exitosa en todos los tenants.
        """
        # Superusuario en org_a
        request_a = self._create_mock_request(self.org_a)
        user_a = self.backend.authenticate(
            request=request_a,
            username='superuser',
            password='adminpass123'
        )
        self.assertIsNotNone(user_a, "Superusuario debería autenticarse en org_a")

        # Superusuario en org_b
        request_b = self._create_mock_request(self.org_b)
        user_b = self.backend.authenticate(
            request=request_b,
            username='superuser',
            password='adminpass123'
        )
        self.assertIsNotNone(user_b, "Superusuario debería autenticarse en org_b")

    def test_admin_publico_permite_login(self):
        """
        ✅ Caso 4: Usuario intentando autenticarse en el esquema público.
        Resultado esperado: Permite el login a cualquier usuario.
        """
        request = self._create_mock_request(self.org_public)

        # Usuario de org_a en esquema público
        user_a = self.backend.authenticate(
            request=request,
            username='user_org_a',
            password='testpass123'
        )
        self.assertIsNotNone(user_a, "Usuario debería autenticarse en esquema público")

        # Usuario de org_b en esquema público
        user_b = self.backend.authenticate(
            request=request,
            username='user_org_b',
            password='testpass123'
        )
        self.assertIsNotNone(user_b, "Usuario debería autenticarse en esquema público")

    def test_credenciales_incorrectas(self):
        """
        ❌ Caso 5: Usuario con credenciales incorrectas.
        Resultado esperado: Autenticación rechazada.
        """
        request = self._create_mock_request(self.org_a)

        # Contraseña incorrecta
        user = self.backend.authenticate(
            request=request,
            username='user_org_a',
            password='wrongpassword'
        )
        self.assertIsNone(user, "No debería autenticarse con contraseña incorrecta")

        # Usuario inexistente
        user = self.backend.authenticate(
            request=request,
            username='nonexistent_user',
            password='testpass123'
        )
        self.assertIsNone(user, "No debería autenticarse con usuario inexistente")

    def test_usuario_inactivo_rechazado(self):
        """
        ❌ Caso adicional: Usuario inactivo intentando autenticarse.
        Resultado esperado: Autenticación rechazada.
        """
        request = self._create_mock_request(self.org_a)

        user = self.backend.authenticate(
            request=request,
            username='inactive_user',
            password='testpass123'
        )

        self.assertIsNone(user, "Usuario inactivo NO debería autenticarse")

    def test_request_sin_tenant(self):
        """
        ❌ Caso adicional: Request sin tenant configurado.
        Resultado esperado: Autenticación rechazada.
        """
        request = Mock()
        request.tenant = None

        user = self.backend.authenticate(
            request=request,
            username='user_org_a',
            password='testpass123'
        )

        self.assertIsNone(user, "No debería autenticarse sin tenant en el request")

    def test_credenciales_vacias(self):
        """
        ❌ Caso adicional: Credenciales vacías (None).
        Resultado esperado: Autenticación rechazada.
        """
        request = self._create_mock_request(self.org_a)

        # Username None
        user = self.backend.authenticate(
            request=request,
            username=None,
            password='testpass123'
        )
        self.assertIsNone(user, "No debería autenticarse con username=None")

        # Password None
        user = self.backend.authenticate(
            request=request,
            username='user_org_a',
            password=None
        )
        self.assertIsNone(user, "No debería autenticarse con password=None")

    def test_get_user_metodo(self):
        """
        ✅ Prueba del método get_user.
        Resultado esperado: Devuelve el usuario si existe y está activo.
        """
        # Obtener usuario activo
        user = self.backend.get_user(self.user_org_a.id)
        self.assertIsNotNone(user, "Debería obtener el usuario activo")
        self.assertEqual(user.username, 'user_org_a')

        # Obtener usuario inactivo
        user_inactive = self.backend.get_user(self.inactive_user.id)
        self.assertIsNone(user_inactive, "No debería obtener usuario inactivo")

        # ID inexistente (generar UUID aleatorio)
        random_uuid = uuid.uuid4()
        user_none = self.backend.get_user(random_uuid)
        self.assertIsNone(user_none, "No debería obtener usuario inexistente")

    def test_usuario_normal_sin_organizacion_rechazado(self):
        """
        ❌ Caso adicional: Usuario normal (no superusuario) sin organización
        intentando autenticarse en un tenant.
        Resultado esperado: Autenticación rechazada.
        """
        # Crear usuario normal sin organización
        user_no_org = User.objects.create_user(
            username='user_no_org',
            password='testpass123',
            email='noorg@test.com'
        )
        user_no_org.organization = None
        user_no_org.is_superuser = False
        user_no_org.save()

        request = self._create_mock_request(self.org_a)

        user = self.backend.authenticate(
            request=request,
            username='user_no_org',
            password='testpass123'
        )

        self.assertIsNone(user, "Usuario normal sin organización NO debería autenticarse en un tenant")


class TenantAwareBackendIntegrationTestCase(TestCase):
    """
    Pruebas de integración adicionales para casos edge.
    """

    def setUp(self):
        self.backend = TenantAwareBackend()

    def test_comportamiento_con_kwargs_adicionales(self):
        """
        Verifica que el backend maneje kwargs adicionales correctamente.
        """
        org = Organization.objects.create(
            schema_name='test_org',
            name='Test Organization'
        )

        user = User.objects.create_user(
            username='test_user',
            password='testpass123'
        )
        user.organization = org
        user.save()

        request = Mock()
        request.tenant = org

        # Autenticación con kwargs adicionales (ignorados)
        authenticated_user = self.backend.authenticate(
            request=request,
            username='test_user',
            password='testpass123',
            extra_param='ignored'
        )

        self.assertIsNotNone(authenticated_user, "Debería autenticarse ignorando kwargs adicionales")
