"""
This module defines the Record class used to manage
company financial data.
"""

from typing import Dict, Union


class Record:
    """
    A class to represent a company's financial record.
    """

    def __init__(
        self,
        company_name: str,
        industry: str,
        location: str,
        financials: Dict[str, Union[int, float]],
    ):
        """
        Initialize the Record instance with company details
        and financial metrics.

        Args:
            company_name (str): The name of the company.
            industry (str): The industry in which the company operates.
            location (str): The location of the company.
            financials (Dict[str, Union[int, float]]): A dictionary
            of financial metrics.
        """
        self.company_name = company_name
        self.industry = industry
        self.location = location
        self.financials = financials

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "Record":
        """
        Create a Record instance from a dictionary.

        Args:
            row (Dict[str, str]): A dictionary containing company data.

        Returns:
            Record: A new instance of Record.
        """
        financials = {
            "Market Capitalization": int(row["Market Capitalization"]),
            "Revenue (in millions)": float(row["Revenue (in millions)"]),
            "EBITDA (in millions)": float(row["EBITDA (in millions)"]),
            "Net Income (in millions)": float(row["Net Income (in millions)"]),
            "Debt (in millions)": float(row["Debt (in millions)"]),
            "Equity (in millions)": float(row["Equity (in millions)"]),
            "Enterprise Value (in millions)": float(
                row["Enterprise Value (in millions)"]
            ),
            "P/E Ratio": float(row["P/E Ratio"]),
            "Revenue Growth Rate (%)": float(row["Revenue Growth Rate (%)"]),
            "EBITDA Margin (%)": float(row["EBITDA Margin (%)"]),
            "Net Income Margin (%)": float(row["Net Income Margin (%)"]),
            "ROE (Return on Equity) (%)": float(
                row["ROE (Return on Equity) (%)"]
            ),
            "ROA (Return on Assets) (%)": float(
                row["ROA (Return on Assets) (%)"]
            ),
            "Current Ratio": float(
                row.get("Current Ratio", 0)
            ),  # Optional field
            "Debt to Equity Ratio": float(row["Debt to Equity Ratio"]),
        }
        return cls(
            company_name=row["Company Name"],
            industry=row["Industry"],
            location=row["Location"],
            financials=financials,
        )

    def to_dict(self) -> Dict[str, Union[int, float, str]]:
        """
        Convert the Record instance to a dictionary.

        Returns:
            Dict[str, Union[int, float, str]]: The instance attributes
            as a dictionary.
        """
        return {
            "Company Name": self.company_name,
            "Industry": self.industry,
            "Location": self.location,
            "Market Capitalization": self.financials["Market Capitalization"],
            "Revenue (in millions)": self.financials["Revenue (in millions)"],
            "EBITDA (in millions)": self.financials["EBITDA (in millions)"],
            "Net Income (in millions)": self.financials[
                "Net Income (in millions)"
            ],
            "Debt (in millions)": self.financials["Debt (in millions)"],
            "Equity (in millions)": self.financials["Equity (in millions)"],
            "Enterprise Value (in millions)": self.financials[
                "Enterprise Value (in millions)"
            ],
            "P/E Ratio": self.financials["P/E Ratio"],
            "Revenue Growth Rate (%)": self.financials[
                "Revenue Growth Rate (%)"
            ],
            "EBITDA Margin (%)": self.financials["EBITDA Margin (%)"],
            "Net Income Margin (%)": self.financials["Net Income Margin (%)"],
            "ROE (Return on Equity) (%)": self.financials[
                "ROE (Return on Equity) (%)"
            ],
            "ROA (Return on Assets) (%)": self.financials[
                "ROA (Return on Assets) (%)"
            ],
            "Current Ratio": self.financials["Current Ratio"],
            "Debt to Equity Ratio": self.financials["Debt to Equity Ratio"],
        }
