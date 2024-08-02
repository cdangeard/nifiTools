import unittest
import src.nifiAPI as nif

class Test_Api_test(unittest.TestCase):
    def setUp(self):
        nifi = nif.nifiAPI_userAuth(host="https://localhost:8443/",
                                    username="drimer", password="passpasspass")
        self.nifi = nifi

    def test_api_test(self):
        self.assertEqual(1, 1)

    def test_getResponse(self):
        response = self.nifi.callAPI("/access", "GET", None)
        self.assertIsInstance(response, dict)
        self.assertEqual(response['statusCode'], 200)

    def test_post(self):
        pass
        
if __name__ == '__main__':
    unittest.main()