"""
This module defines the main entry point for the FastAPI application,
handling file uploads and data comparison.
"""

import os
import tempfile
from typing import Dict, Union
from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    Form,
    Request,
)  # pylint: disable=import-error
from fastapi.responses import JSONResponse  # pylint: disable=import-error
from dotenv import load_dotenv  # pylint: disable=import-error
from auth import AuthService, isapivalidated
from database_service import DatabaseService
from models import Record

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

DATABASE_PATH: str = os.getenv("DATABASE_FILE") or ""
ASSETS_PATH: str = os.getenv("ASSETS_PATH") or ""

if not DATABASE_PATH or not ASSETS_PATH:
    raise RuntimeError(
        "Environment variables DATABASE_FILE and ASSETS_PATH must be set."
    )

# Initialize services
auth_service = AuthService()
database_service = DatabaseService(DATABASE_PATH)

if not database_service.connect():
    raise RuntimeError("Failed to connect to the database.")


def compare_data(
    extracted_data: Dict[str, Union[int, float, str]], stored_data: Record
) -> Dict[str, Dict[str, Union[int, float, str, bool]]]:
    """Compare extracted data from PDF with stored data in the database."""
    discrepancies = {}
    stored_data_dict = stored_data.to_dict()

    for key, extracted_value in extracted_data.items():
        if key in stored_data_dict:
            stored_value = stored_data_dict[key]
            match = extracted_value == stored_value
            discrepancies[key] = {
                "extracted": extracted_value,
                "stored": stored_value,
                "match": match,
            }
    return discrepancies


def raise_http_exception(status_code: int, detail: str):
    """Raise an HTTP exception with a given status code and detail message."""
    raise HTTPException(status_code=status_code, detail=detail)


@app.post("/upload")
@isapivalidated(auth_service)
async def upload(
    request: Request,  # pylint: disable=unused-argument
    file: UploadFile = File(...),
    api_key: str = Form(...),  # pylint: disable=unused-argument
):
    """Endpoint to upload a PDF and compare extracted data with stored data."""
    pdf_service = auth_service.get_pdf_service()

    filename = file.filename or "default.pdf"
    file_location = os.path.join(ASSETS_PATH, filename)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(await file.read())
        temp_file.seek(0)

        # Extract data from PDF
        try:
            extracted_data = pdf_service.extract(file_location)
        except FileNotFoundError:
            raise_http_exception(
                400, "Cannot extract data. Invalid file provided."
            )

        if not extracted_data:
            raise_http_exception(
                400, "Extraction failed. Extracted data is empty."
            )

    # Get company name from extracted data
    try:
        company_name = extracted_data["Company Name"]
    except KeyError:
        raise_http_exception(400, "Company Name not found in extracted data.")

    # Query stored data
    stored_data = database_service.query(company_name)

    if stored_data is None:
        raise_http_exception(404, f"No data found for company {company_name}")

    assert isinstance(
        stored_data, Record
    )  # Type assertion to satisfy the type checker

    # Compare data
    discrepancies = compare_data(extracted_data, stored_data)

    # Create response
    response = {
        "company_name": company_name,
        "extracted_data": extracted_data,
        "stored_data": stored_data.to_dict(),
        "discrepancies": discrepancies,
    }

    return JSONResponse(content=response)


if __name__ == "__main__":
    import uvicorn  # pylint: disable=import-error

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
