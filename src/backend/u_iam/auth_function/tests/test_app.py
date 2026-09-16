import unittest
import sys
from unittest.mock import patch, MagicMock

# Mock third-party dependencies before importing our code
sys.modules['boto3'] = MagicMock()
sys.modules['requests'] = MagicMock()

import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
from domain import JWT

class TestAppHandler(unittest.TestCase):
    
    @patch('app.use_case')
    def test_handler_success(self, mock_use_case):
        # Arrange
        mock_use_case.login.return_value = JWT(token="mocked.jwt.token", expires_at=123456789)
        
        event = {
            "requestContext": {"requestId": "req-123"},
            "body": json.dumps({
                "username": "user1",
                "password": "pwd",
                "deviceId": "dev1",
                "pushToken": "push1",
                "publicKeyPEM": "pem1"
            })
        }
        
        # Act
        response = app.handler(event, None)
        
        # Assert
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['accessToken'], "mocked.jwt.token")
        self.assertEqual(body['expiresIn'], 123456789)
        mock_use_case.login.assert_called_once()

    def test_handler_missing_fields(self):
        # Arrange
        event = {
            "requestContext": {"requestId": "req-123"},
            "body": json.dumps({
                "username": "user1",
                # missing password and others
            })
        }
        
        # Act
        response = app.handler(event, None)
        
        # Assert
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Missing required fields", response['body'])

    @patch('app.use_case')
    def test_handler_unauthorized(self, mock_use_case):
        # Arrange
        mock_use_case.login.side_effect = ValueError("Invalid credentials")
        
        event = {
            "requestContext": {"requestId": "req-123"},
            "body": json.dumps({
                "username": "user1", "password": "pwd",
                "deviceId": "dev1", "pushToken": "push1",
                "publicKeyPEM": "pem1"
            })
        }
        
        # Act
        response = app.handler(event, None)
        
        # Assert
        self.assertEqual(response['statusCode'], 401)
        self.assertIn("Unauthorized", response['body'])

if __name__ == '__main__':
    unittest.main()
