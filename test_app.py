from unittest import TestCase
from app import app

class Test(TestCase):
    def test_home(self):
        with app.test_client() as client:
            resp = client.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Where Twitch', html)