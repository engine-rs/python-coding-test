"""
This module contains test cases for the application.
"""

import unittest
from unittest.mock import mock_open, patch, MagicMock
import os
from io import StringIO
from fastapi.testclient import TestClient  # pylint: disable=import-error
from models import Record
from auth import AuthService
from pdf_service import PdfService
from main import app, compare_data
from database_service import DatabaseService


class TestDatabaseService(unittest.TestCase):
    """
    Test cases for the DatabaseService class.
    """

    def setUp(self):
        """
        Set up the mock CSV content and DatabaseService instance.
        """
        self.database_file = "data/database.csv"
        self.database_service = DatabaseService(self.database_file)
        self.mock_csv_content = (
            "Company Name,Industry,Market Capitalization,Revenue (in millions)"
            ","
            "EBITDA (in millions),Net Income (in millions),Debt (in millions)"
            ","
            "Equity (in millions),Enterprise Value (in millions),P/E Ratio,"
            "Revenue Growth Rate (%),EBITDA Margin (%),Net Income Margin (%),"
            "ROE (Return on Equity) (%),ROA (Return on Assets) (%),Current "
            "Ratio,"
            "Debt to Equity Ratio,Location\n"
            "ExampleCo,Tech,5000,1500,500,200,300,2000,5200,25,10,33.33,13.33,"
            "10,5,2.0,0.15,San Francisco, CA\n"
            "HealthInc,Healthcare,3000,1000,250,80,150,666,3150,15,12,40,8,"
            "13.33,"
            "10,1.5,0.25,New York, NY"
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_connect_file_not_found(self, mock_file):
        """
        Test connecting to the database when the file is not found.
        """
        mock_file.side_effect = FileNotFoundError
        result = self.database_service.connect()
        self.assertFalse(result)
        self.assertIsNone(self.database_service.data)

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_connect_success(self, mock_file):
        """
        Test successful connection to the database.
        """
        mock_file.return_value = StringIO(self.mock_csv_content)
        result = self.database_service.connect()
        self.assertTrue(result)
        self.assertIsNotNone(self.database_service.data)
        self.assertIn("ExampleCo", self.database_service.data)
        self.assertIsInstance(self.database_service.data["ExampleCo"], Record)

    def test_query_not_connected(self):
        """
        Test querying the database before connecting.
        """
        with self.assertRaises(ValueError):
            self.database_service.query("ExampleCo")

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_query_success(self, mock_file):
        """
        Test querying the database successfully.
        """
        mock_file.return_value = StringIO(self.mock_csv_content)
        self.database_service.connect()
        record = self.database_service.query("ExampleCo")
        self.assertIsNotNone(record)
        self.assertEqual(record.company_name, "ExampleCo")
        self.assertEqual(record.industry, "Tech")

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_query_nonexistent_record(self, mock_file):
        """
        Test querying a non-existent record.
        """
        mock_file.return_value = StringIO(self.mock_csv_content)
        self.database_service.connect()
        record = self.database_service.query("NonExistentCo")
        self.assertIsNone(record)


class TestAuthService(unittest.TestCase):
    """
    Test cases for the AuthService class.
    """

    def setUp(self):
        """
        Set up the AuthService instance.
        """
        self.auth_service = AuthService()

    def test_validate_api_key_success(self):
        """
        Test API key validation success.
        """
        valid_api_key = "TEST_KEY"
        result = self.auth_service.validate_api_key(valid_api_key)
        self.assertTrue(result)
        self.assertIsInstance(self.auth_service.get_pdf_service(), PdfService)

    def test_validate_api_key_failure(self):
        """
        Test API key validation failure.
        """
        invalid_api_key = "INVALID_KEY"
        result = self.auth_service.validate_api_key(invalid_api_key)
        self.assertFalse(result)
        self.assertIsNone(self.auth_service.get_pdf_service())


class TestRecord(unittest.TestCase):
    """
    Test cases for the Record class.
    """

    def setUp(self):
        """
        Set up a sample dictionary representing a company's financial record.
        """
        self.example_record_dict = {
            "Company Name": "ExampleCo",
            "Industry": "Tech",
            "Market Capitalization": "5000",
            "Revenue (in millions)": "1500",
            "EBITDA (in millions)": "500",
            "Net Income (in millions)": "200",
            "Debt (in millions)": "300",
            "Equity (in millions)": "2000",
            "Enterprise Value (in millions)": "5200",
            "P/E Ratio": "25",
            "Revenue Growth Rate (%)": "10",
            "EBITDA Margin (%)": "33.33",
            "Net Income Margin (%)": "13.33",
            "ROE (Return on Equity) (%)": "10",
            "ROA (Return on Assets) (%)": "5",
            "Current Ratio": "2.0",
            "Debt to Equity Ratio": "0.15",
            "Location": "San Francisco, CA",
        }
        self.example_record = Record.from_dict(self.example_record_dict)

    def test_from_dict(self):
        """
        Test the from_dict method of the Record class.
        """
        record = Record.from_dict(self.example_record_dict)
        self.assertEqual(record.company_name, "ExampleCo")
        self.assertEqual(record.industry, "Tech")
        self.assertEqual(record.location, "San Francisco, CA")

        financials = record.financials
        self.assertEqual(financials["Market Capitalization"], 5000)
        self.assertEqual(financials["Revenue (in millions)"], 1500.0)
        self.assertEqual(financials["EBITDA (in millions)"], 500.0)
        self.assertEqual(financials["Net Income (in millions)"], 200.0)
        self.assertEqual(financials["Debt (in millions)"], 300.0)
        self.assertEqual(financials["Equity (in millions)"], 2000.0)
        self.assertEqual(financials["Enterprise Value (in millions)"], 5200.0)
        self.assertEqual(financials["P/E Ratio"], 25.0)
        self.assertEqual(financials["Revenue Growth Rate (%)"], 10.0)
        self.assertEqual(financials["EBITDA Margin (%)"], 33.33)
        self.assertEqual(financials["Net Income Margin (%)"], 13.33)
        self.assertEqual(financials["ROE (Return on Equity) (%)"], 10.0)
        self.assertEqual(financials["ROA (Return on Assets) (%)"], 5.0)
        self.assertEqual(financials["Current Ratio"], 2.0)
        self.assertEqual(financials["Debt to Equity Ratio"], 0.15)


class TestMain(unittest.TestCase):
    """
    Test cases for the main application.
    """

    def setUp(self):
        """
        Set up the TestClient and sample data.
        """
        self.client = TestClient(app)
        self.extracted_data = {
            "Company Name": "ExampleCo",
            "Industry": "Tech",
            "Market Capitalization": 5000,
            "Revenue (in millions)": 1500.0,
            "EBITDA (in millions)": 500.0,
            "Net Income (in millions)": 200.0,
            "Debt (in millions)": 300.0,
            "Equity (in millions)": 2000.0,
            "Enterprise Value (in millions)": 5200.0,
            "P/E Ratio": 25.0,
            "Revenue Growth Rate (%)": 10.0,
            "EBITDA Margin (%)": 33.33,
            "Net Income Margin (%)": 13.33,
            "ROE (Return on Equity) (%)": 10.0,
            "ROA (Return on Assets) (%)": 5.0,
            "Current Ratio": 2.0,
            "Debt to Equity Ratio": 0.15,
            "Location": "London, UK",
        }
        self.stored_data = Record.from_dict(self.extracted_data)

    def test_compare_data(self):
        """
        Test the compare_data function.
        """
        discrepancies = compare_data(self.extracted_data, self.stored_data)
        for key in self.extracted_data:
            self.assertIn(key, discrepancies)
            self.assertTrue(discrepancies[key]["match"])

        # Test with discrepancies
        self.extracted_data["Revenue (in millions)"] = 1400.0
        discrepancies = compare_data(self.extracted_data, self.stored_data)
        self.assertFalse(discrepancies["Revenue (in millions)"]["match"])

    @patch("main.auth_service.validate_api_key", return_value=True)
    @patch("main.auth_service.get_pdf_service")
    @patch("main.database_service.query")
    def test_upload(
        self, mock_query, mock_get_pdf_service, mock_validate_api_key
    ):  # pylint: disable=unused-argument
        """
        Test the /upload endpoint.
        """
        mock_pdf_service = MagicMock()
        mock_pdf_service.extract.return_value = self.extracted_data
        mock_get_pdf_service.return_value = mock_pdf_service
        mock_query.return_value = self.stored_data

        with open("example.pdf", "wb") as f:
            f.write(b"%PDF-1.4 example content")

        with open("example.pdf", "rb") as f:
            response = self.client.post(
                "/upload",
                files={"file": f},
                data={"company_name": "ExampleCo", "api_key": "TEST_KEY"},
            )

        os.remove("example.pdf")

        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response["company_name"], "ExampleCo")
        self.assertEqual(json_response["extracted_data"], self.extracted_data)
        self.assertEqual(
            json_response["stored_data"], self.stored_data.to_dict()
        )
        for key in self.extracted_data:
            self.assertIn(key, json_response["discrepancies"])

    @patch("main.auth_service.validate_api_key", return_value=False)
    def test_upload_invalid_api_key(
        self, mock_validate_api_key
    ):  # pylint: disable=unused-argument
        """
        Test the /upload endpoint with an invalid API key.
        """
        response = self.client.post(
            "/upload",
            files={"file": ("example.pdf", b"%PDF-1.4 example content")},
            data={"company_name": "ExampleCo", "api_key": "INVALID_KEY"},
        )
        self.assertEqual(response.status_code, 403)

    @patch("main.auth_service.validate_api_key", return_value=True)
    @patch("main.auth_service.get_pdf_service")
    @patch("main.database_service.query", return_value=None)
    def test_upload_company_not_found(
        self, mock_query, mock_get_pdf_service, mock_validate_api_key
    ):  # pylint: disable=unused-argument
        """
        Test the /upload endpoint when the company is not found.
        """
        mock_pdf_service = MagicMock()
        mock_pdf_service.extract.return_value = self.extracted_data
        mock_get_pdf_service.return_value = mock_pdf_service

        response = self.client.post(
            "/upload",
            files={"file": ("example.pdf", b"%PDF-1.4 example content")},
            data={"company_name": "NonExistentCo", "api_key": "TEST_KEY"},
        )
        self.assertEqual(response.status_code, 404)

    @patch("main.auth_service.validate_api_key", return_value=True)
    @patch("main.auth_service.get_pdf_service")
    def test_upload_no_company_name(
        self, mock_get_pdf_service, mock_validate_api_key
    ):  # pylint: disable=unused-argument
        """
        Test the /upload endpoint when 'Company Name' is not in extracted data.
        """
        mock_pdf_service = MagicMock()
        incomplete_extracted_data = self.extracted_data.copy()
        del incomplete_extracted_data["Company Name"]
        mock_pdf_service.extract.return_value = incomplete_extracted_data
        mock_get_pdf_service.return_value = mock_pdf_service

        with open("example.pdf", "wb") as f:
            f.write(b"%PDF-1.4 example content")

        with open("example.pdf", "rb") as f:
            response = self.client.post(
                "/upload",
                files={"file": f},
                data={"api_key": "TEST_KEY"},
            )

        os.remove("example.pdf")

        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertEqual(
            json_response["detail"],
            "Company Name not found in extracted data.",
        )


if __name__ == "__main__":
    unittest.main()
