import unittest

from bluesnap.client import Client


class ClientTestCase(unittest.TestCase):
    DUMMY_CREDENTIALS = {
        'username': 'username',
        'password': 'password',
        'default_store_id': '1',
        'seller_id': '1',
        'default_currency': 'GBP'
    }

    def setUp(self):
        self.client = Client(env='live', **self.DUMMY_CREDENTIALS)

    def test_env(self):
        self.assertEqual(sorted(list(Client.ENDPOINTS.keys())), ['live', 'sandbox'])

        for env, endpoint_url in Client.ENDPOINTS.items():
            client = Client(env=env, **self.DUMMY_CREDENTIALS)
            self.assertEqual(client.endpoint_url, endpoint_url)
