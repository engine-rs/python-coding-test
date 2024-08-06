"""
This module defines the AuthService class and the isapivalidated decorator
used to manage API key validation for accessing PDF services.
"""

from functools import wraps
from typing import Callable
from fastapi import HTTPException, Request  # pylint: disable=import-error
from pdf_service import PdfService  # pylint: disable=import-error


class AuthService:
    """
    A service for validating API keys and providing access to the PDF service.
    """

    def __init__(self):
        """
        Initialize the AuthService instance.
        """
        self.pdf_service = None

    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate the provided API key and initialize the PdfService.

        Args:
            api_key (str): The API key to validate.

        Returns:
            bool: True if the API key is valid, False otherwise.
        """
        try:
            self.pdf_service = PdfService(api_key)
            return True
        except AssertionError:
            return False

    def get_pdf_service(self) -> PdfService:
        """
        Get the initialized PdfService instance.

        Returns:
            PdfService: The PdfService instance.
        """
        return self.pdf_service


def isapivalidated(auth_service: AuthService) -> Callable:
    """
    Decorator to validate the API key before executing the function.

    Args:
        auth_service (AuthService): The AuthService instance to use for
        validation.

    Returns:
        Callable: The decorated function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def decorated_function(request: Request, *args, **kwargs):
            form = await request.form()
            api_key = form.get("api_key")
            if api_key is None or not isinstance(api_key, str):
                raise HTTPException(status_code=403, detail="Invalid API key")
            if not auth_service.validate_api_key(api_key):
                raise HTTPException(status_code=403, detail="Invalid API key")
            return await func(request, *args, **kwargs)

        return decorated_function

    return decorator
