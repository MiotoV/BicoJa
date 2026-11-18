from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError
from django.test import TestCase

Usuario = get_user_model()
SENHA = "Senha-forte-123"


class UsuarioTests(TestCase):
    def test_email_e_salvo_em_minusculas(self):
        usuario = Usuario.objects.create_user(email="  Ana.Souza@Email.COM ", password=SENHA)
        self.assertEqual(usuario.email, "ana.souza@email.com")

    def test_email_nao_repete_mesmo_com_maiusculas(self):
        Usuario.objects.create_user(email="ana@email.com", password=SENHA)
        with self.assertRaises(IntegrityError):
            Usuario.objects.create_user(email="ANA@email.com", password=SENHA)

    def test_banco_recusa_email_com_maiusculas(self):
        with self.assertRaises(IntegrityError):
            Usuario.objects.bulk_create([Usuario(email="Ana@Email.com")])

    def test_login_aceita_email_com_maiusculas(self):
        Usuario.objects.create_user(email="ana@email.com", password=SENHA)
        self.assertIsNotNone(authenticate(email="ANA@Email.com", password=SENHA))

    def test_login_recusa_senha_errada(self):
        Usuario.objects.create_user(email="ana@email.com", password=SENHA)
        self.assertIsNone(authenticate(email="ana@email.com", password="senha-errada"))

    def test_senha_guardada_com_argon2(self):
        usuario = Usuario.objects.create_user(email="ana@email.com", password=SENHA)
        self.assertTrue(usuario.password.startswith("argon2"))
        self.assertNotIn(SENHA, usuario.password)

    def test_conta_sem_senha_nao_consegue_entrar(self):
        usuario = Usuario.objects.create_user(email="convite@email.com")
        self.assertFalse(usuario.has_usable_password())

    def test_uuid_gerado_e_unico(self):
        a = Usuario.objects.create_user(email="a@email.com", password=SENHA)
        b = Usuario.objects.create_user(email="b@email.com", password=SENHA)
        self.assertNotEqual(a.uuid, b.uuid)

    def test_administrador_nasce_como_equipe(self):
        admin = Usuario.objects.create_superuser(email="admin@bicoja.com", password=SENHA)
        self.assertEqual(admin.tipo, Usuario.Tipo.EQUIPE)
        self.assertTrue(admin.is_staff and admin.is_superuser)

    def test_usuario_comum_nao_acessa_o_painel(self):
        usuario = Usuario.objects.create_user(email="ana@email.com", password=SENHA)
        self.assertFalse(usuario.is_staff)
        self.assertEqual(usuario.tipo, Usuario.Tipo.PRESTADOR)