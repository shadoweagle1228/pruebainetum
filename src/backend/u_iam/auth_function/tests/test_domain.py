import unittest
from unittest.mock import MagicMock
import sys
import os

# Add parent directory to path so we can import domain
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain import (
    AuthenticationUseCase, LegacyAuthPort, DeviceRepositoryPort, 
    TokenGeneratorPort, LegacyCredentials, User, JWT
)

class TestAuthenticationUseCase(unittest.TestCase):
    def setUp(self):
        self.auth_port = MagicMock(spec=LegacyAuthPort)
        self.device_repo = MagicMock(spec=DeviceRepositoryPort)
        self.token_gen = MagicMock(spec=TokenGeneratorPort)
        self.use_case = AuthenticationUseCase(self.auth_port, self.device_repo, self.token_gen)

    def test_login_success(self):
        # Arrange
        credentials = LegacyCredentials(username="testuser", password="password")
        mock_user = User(user_id="U123", role="CORP", status="ACTIVE")
        mock_jwt = JWT(token="jwt.token.sig", expires_at=999999999)
        
        self.auth_port.authenticate.return_value = mock_user
        self.token_gen.generate_token.return_value = mock_jwt

        # Act
        result = self.use_case.login(
            credentials=credentials,
            device_id="DEV-456",
            push_token="push-tok",
            public_key_pem="PEM-KEY"
        )

        # Assert
        self.assertEqual(result.token, "jwt.token.sig")
        self.auth_port.authenticate.assert_called_once_with(credentials)
        self.device_repo.save.assert_called_once()
        self.token_gen.generate_token.assert_called_once()
        
        # Verify device properties passed to save
        saved_device = self.device_repo.save.call_args[0][0]
        self.assertEqual(saved_device.user_id, "U123")
        self.assertEqual(saved_device.device_id, "DEV-456")

    def test_login_invalid_credentials(self):
        # Arrange
        credentials = LegacyCredentials(username="wrong", password="pwd")
        self.auth_port.authenticate.return_value = None

        # Act & Assert
        with self.assertRaisesRegex(ValueError, "Invalid credentials"):
            self.use_case.login(credentials, "DEV-1", "push", "pem")
            
        self.device_repo.save.assert_not_called()

    def test_login_inactive_user(self):
        # Arrange
        credentials = LegacyCredentials(username="inactive", password="pwd")
        mock_user = User(user_id="U123", role="CORP", status="INACTIVE")
        self.auth_port.authenticate.return_value = mock_user

        # Act & Assert
        with self.assertRaisesRegex(ValueError, "User is not active"):
            self.use_case.login(credentials, "DEV-1", "push", "pem")

if __name__ == '__main__':
    unittest.main()
