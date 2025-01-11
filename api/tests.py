import unittest
from unittest.mock import patch, MagicMock
import json
from app import app

class TestReservationAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('psycopg2.connect')
    def test_make_reservation(self, mock_connect):
        # Mock the context managers
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # Simulating reservation ID being returned

        test_data = {
            "customer_id": 1,
            "restaurant_id": 1,
            "make_date": "2025-01-11",
            "reservation_date": "2025-01-12",
            "num_persons": 4,
            "optional_message": "Birthday celebration"
        }

        response = self.app.post('/make_reservation',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['reservation_id'], 1)
        self.assertIn("Message", response_data)

    @patch('psycopg2.connect')
    def test_get_reservations_by_user(self, mock_connect):
        # Mock the context managers
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, 1, 1, "2025-01-11", "2025-01-12", 4, "Birthday celebration")]

        response = self.app.get('/get_reservations_by_user?customer_id=1')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data['reservations']), 1)
        self.assertEqual(response_data['reservations'][0]['reservation_id'], 1)
        self.assertEqual(response_data['reservations'][0]['message'], "Birthday celebration")

    @patch('psycopg2.connect')
    def test_get_reservations_by_user_no_reservations(self, mock_connect):
        # Mock the context managers
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []  # No reservations found

        response = self.app.get('/get_reservations_by_user?customer_id=1')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], "No reservations found")

    @patch('psycopg2.connect')
    def test_get_reservations_by_restaurant(self, mock_connect):
        # Mock the context managers
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 1, 1, "2025-01-11", "2025-01-12", 4, "Birthday celebration")
        ]

        response = self.app.get('/get_reservations_by_restaurant?restaurant_id=1')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data['reservations']), 1)
        self.assertEqual(response_data['reservations'][0]['reservation_id'], 1)
        self.assertEqual(response_data['reservations'][0]['message'], "Birthday celebration")

    @patch('psycopg2.connect')
    def test_get_reservations_by_restaurant_no_reservations(self, mock_connect):
        # Mock the context managers
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []  # No reservations found

        response = self.app.get('/get_reservations_by_restaurant?restaurant_id=1')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], "No reservations found")

if __name__ == '__main__':
    unittest.main()
