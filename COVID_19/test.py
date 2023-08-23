from unittest import TestCase
from unittest.mock import patch

import user_manager


class TestUserManger(TestCase):
    @patch("requests.get")
    def test_get_user(self, mock_get):
        response = mock_get.return_value
        response.status_code = 200
        response.json.return_value = {
            "name": "Test User",
            "email": "user@test.com",
        }

        user = user_manager.get_user(1)

        self.assertEqual(user["name"], "Test User")
        self.assertEqual(user["email"], "user@test.com")
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users/1")