"""
This module provides the BaseClient class for handling HTTP responses
in a standardized way. It ensures error handling and consistent JSON
parsing across client implementations.
"""

import requests


class BaseClient:
    """
    A base client utility class for handling HTTP responses.

    This class provides common functionality to parse responses
    and raise appropriate errors for client implementations.
    """

    @staticmethod
    def _handle_response(response: requests.Response):
        """
        Process an HTTP response object.

        Raises an HTTPError if the response status indicates a failure.
        Attempts to parse and return the response as JSON. If parsing
        fails, raises an HTTPError with the raw response text.

        Args:
            response: The HTTP response object.

        Raises:
            requests.HTTPError: If the response contains an HTTP error
                or if JSON parsing fails.

        Returns:
            dict: Parsed JSON content of the response.
        """
        response.raise_for_status()

        try:
            return response.json()
        except ValueError as e:
            raise requests.HTTPError(
                f"Failed to parse JSON response. Response text: {response.text}",
                response=response,
            ) from e
