"""
This module defines the DatabaseService class used to interact
with the company's financial data stored in a CSV file.
"""

import csv
from typing import Dict, Optional
from models import Record  # pylint: disable=import-error


class DatabaseService:
    """
    A class to represent the service that interacts with the
    company's financial database.
    """

    def __init__(self, database_file: str):
        """
        Initialize the DatabaseService instance with the
        database file path.

        Args:
            database_file (str): The path to the CSV file
            containing the database.
        """
        self.database_file = database_file
        self.data: Optional[Dict[str, Record]] = None

    def connect(self) -> bool:
        """
        Connect to the database and load data from the CSV file.

        Returns:
            bool: True if the connection and data loading are
            successful, False otherwise.
        """
        try:
            with open(self.database_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.data = {
                    row["Company Name"]: Record.from_dict(row)
                    for row in reader
                }
            return True
        except FileNotFoundError:
            self.data = None
            return False

    def like(self, company_name: str) -> Optional[Record]:
        """
        Query the database for a specific company's record
        by normalizing whitespace.

        Args:
            company_name (str): The name of the company to query.

        Returns:
            Optional[Record]: The Record of the company if found,
            None otherwise.

        Raises:
            ValueError: If the database is not connected.
        """
        if self.data is None:
            raise ValueError("Database not connected. Call connect() first.")

        # Normalize the company name by removing whitespaces
        normalized_name = company_name.replace(" ", "")

        # Search for the normalized name in the data
        for key in self.data.keys():
            if key.replace(" ", "") == normalized_name:
                return self.data[key]

        return None

    def query(self, company_name: str) -> Optional[Record]:
        """
        Query the database for a specific company's record.

        Args:
            company_name (str): The name of the company to query.

        Returns:
            Optional[Record]: The Record of the company if found,
            None otherwise.

        Raises:
            ValueError: If the database is not connected.
        """
        if self.data is None:
            raise ValueError("Database not connected. Call connect() first.")

        # First, try to get the exact match
        record = self.data.get(company_name)

        if record is not None:
            return record

        # If exact match is not found, try the like method
        return self.like(company_name)
