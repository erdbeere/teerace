from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from django.test.client import Client
from django.utils import simplejson
from race.models import Map, Server
from lib.aes import aes_encrypt

class TestCase(DjangoTestCase):
	fixtures = ['tests.json']

	def setUp(self):
		self.client = JsonClient()
		self.user = User.objects.get(pk=1)
		self.map = Map.objects.get(pk=1)
		self.server = Server.objects.get(pk=1)
		self.extra = {
			'HTTP_API_AUTH': self.server.public_key,
		}


class JsonClient(Client):

	def post(self, path, data=None, content_type='application/json',
		follow=False, **extra):
		if content_type == 'application/json':
			data = simplejson.dumps(data)
		return super(JsonClient, self).post(path, data, content_type, follow, **extra)


class ApiTest(TestCase):

	def test_auth_success(self):
		# we intentionally want to receive 405 Not Implemented
		response = self.client.get('/api/1/runs/', {}, **self.extra)
		self.assertEqual(response.status_code, 405)

	def test_auth_invalid_key(self):
		self.extra['HTTP_API_AUTH'] = 'invalid'
		response = self.client.get('/api/1/runs/', {}, **self.extra)
		self.assertEqual(response.status_code, 401)


class RunTest(TestCase):

	def test_create_run_success(self):
		data = {
			'map_name': self.map.name,
			'user_id': self.user.id,
			'nickname': "[GER] Ueber Tester",
			'time': 14.72,
			'created_at': "2010-12-10 16:53:20",
		}
		response = self.client.post('/api/1/runs/', data, **self.extra)
		self.assertEqual(response.status_code, 201)

	def test_create_run_wrong_map(self):
		data = {
			'map_name': "wrong_map",
			'user_id': self.user.id,
			'nickname': "[AUS] Lame Badass",
			'time': 151.02,
		}
		response = self.client.post('/api/1/runs/', data, **self.extra)
		self.assertEqual(response.status_code, 400)

	def test_create_map_wrong_user(self):
		data = {
			'map_name': "wrong_map",
			'user_id': 666, # what
			'nickname': "[AUS] Lame Badass",
			'time': 151.02,
		}
		response = self.client.post('/api/1/runs/', data, **self.extra)
		self.assertEqual(response.status_code, 400)


class UserTestCase(TestCase):

	def test_validate_user_success(self):
		data = {
			'username': "testclient",
			'password': "test123",
		}
		data['password'] = aes_encrypt(data['password'], self.server.private_key)
		response = self.client.post('/api/1/users/validate/', data, **self.extra)
		self.assertTrue(simplejson.loads(response.content))

	def test_validate_user_wrong_password(self):
		data = {
			'username': "testclient",
			'password': "toast123", # WHOOOPS, A TYPO!
		}
		data['password'] = aes_encrypt(data['password'], self.server.private_key)
		response = self.client.post('/api/1/users/validate/', data, **self.extra)
		self.assertFalse(simplejson.loads(response.content))

	def test_validate_user_wrong_username(self):
		data = {
			'username': "toastclient", # O NOEZ
			'password': "toast123", # WHOOOPS, A TYPO!
		}
		data['password'] = aes_encrypt(data['password'], self.server.private_key)
		response = self.client.post('/api/1/users/validate/', data, **self.extra)
		self.assertFalse(simplejson.loads(response.content))
