"""
This module provides the `AuthClient` class for handling user authentication
requests to an API. It extends the `BaseClient` to provide utility methods
for registering users, logging in, and retrieving the currently authenticated
user. All methods are implemented as static methods for convenience.
"""

import requests

from clients.base import BaseClient


class AuthClient(BaseClient):
    """
    A client for handling authentication-related API calls.

    This class provides methods to:
    - Register a new user
    - Log in with existing credentials
    - Retrieve details of the currently authenticated user

    Inherits from:
        BaseClient: Provides `_handle_response` for consistent response handling.
    """

    @staticmethod
    def register_user(
        email: str,
        password: str,
        url: str = "http://127.0.0.1:8000/api/v1/auth/register",
    ):
        """
        Register a new user in the authentication system.

        Args:
            email: The user's email address.
            password: The user's password (min length typically enforced server-side).
            url: The API endpoint for user registration.
                 Defaults to the local development endpoint.

        Raises:
            requests.HTTPError: If the request fails or JSON parsing fails.

        Returns:
            dict: Parsed JSON response from the API.
        """
        # Payload containing new user credentials
        user_data = {"email": email, "password": password}

        # Send POST request to the registration endpoint
        response = requests.post(url=url, json=user_data)

        return AuthClient._handle_response(response)

    @staticmethod
    def login(
        email: str, password: str, url: str = "http://127.0.0.1:8000/api/v1/auth/login"
    ):
        """
        Log in a user and obtain an access token.

        Args:
            emai: The user's email address.
            passwor: The user's password.
            url The API endpoint for login.
                                 Defaults to the local development endpoint.

        Raises:
            requests.HTTPError: If authentication fails or JSON parsing fails.

        Returns:
            dict: Parsed JSON response containing the access token.
        """
        # OAuth2 requires `username` instead of `email`
        data = {
            "username": email,
            "password": password,
        }

        # Set headers for form-urlencoded request
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Send POST request to the login endpoint
        response = requests.post(url=url, data=data, headers=headers)

        return AuthClient._handle_response(response)

    @staticmethod
    def get_current_user(token: str, url: str = "http://127.0.0.1:8000/api/v1/auth/me"):
        """
        Retrieve details of the currently authenticated user.

        Args:
            token: Bearer token obtained during login.
            url: The API endpoint for fetching user info.
                                 Defaults to the local development endpoint.

        Raises:
            requests.HTTPError: If authentication fails or JSON parsing fails.

        Returns:
            dict: Parsed JSON response with user details.
        """

        # Authorization header containing Bearer token
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Send GET request to the current user endpoint
        response = requests.get(url=url, headers=headers)

        # Send GET request to the current user endpoin
        return AuthClient._handle_response(response)
