"""
This module defines the `SessionClient` class for interacting with a session
management API service. It provides methods to:

- Retrieve all sessions available to the user
- Retrieve or set the active session
- Create new sessions
- Delete sessions

All methods are implemented as `@staticmethod`s and use the `requests` library
to communicate with an external microservice. The class extends `BaseClient`
to inherit consistent HTTP response handling behavior.
"""

import requests

from clients.base import BaseClient


class SessionClient(BaseClient):
    """
    A client class for performing session-related operations via HTTP.

    This client communicates with a session management microservice to:
    - List all sessions
    - Manage the active session
    - Create new sessions
    - Delete existing sessions

    Inherits from:
        BaseClient: Provides `_handle_response()` for error-safe parsing.
    """

    @staticmethod
    def get_sessions(token: str, url: str = "http://127.0.0.1:8001/api/v1/sessions"):
        """
        Fetch a list of all sessions accessible to the current user.

        Args:
            token: Bearer token for authentication.
            url: API endpoint for listing sessions.

        Raises:
            requests.HTTPError: If the request fails or response is invalid.

        Returns:
            dict: Parsed JSON response containing the list of sessions.
        """

        # Set authorization header
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Send GET request to fetch sessions
        response = requests.get(url=url, headers=headers)

        return SessionClient._handle_response(response)

    @staticmethod
    def get_active_session_id(
        token: str, url: str = "http://127.0.0.1:8001/api/v1/sessions/active"
    ):
        """
        Retrieve the currently active session ID.

        Args:
            token: Bearer token for authentication.
            url: API endpoint for fetching the active session.

        Returns:
            dict: JSON response with active session details.
        """

        # Set authorization header
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Send GET request to retrieve active session
        response = requests.get(url=url, headers=headers)

        return SessionClient._handle_response(response)

    @staticmethod
    def create_session(
        token: str, title: str, url="http://127.0.0.1:8001/api/v1/sessions"
    ):
        """
        Create a new session with the specified title.

        Args:
            token: Bearer token for authentication.
            title: Title of the session to create.
            url: API endpoint for creating sessions.

        Returns:
            dict: JSON response confirming session creation.
        """

        # Set authorization header
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Request payload
        data = {"title": title}

        # Send POST request to create a new session
        response = requests.post(url=url, json=data, headers=headers)

        return SessionClient._handle_response(response)

    @staticmethod
    def set_active_session(
        token: str,
        title: str,
        base_url: str = "http://127.0.0.1:8001/api/v1/sessions/active",
    ):
        """
        Set a specific session as the currently active session.

        Args:
            token: Bearer token for authentication.
            title: Title of the session to activate.
            base_url: Base endpoint for setting active session.

        Returns:
            dict: JSON response confirming the update.
        """
        # Construct session-specific URL
        url = base_url + f"/{title}"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        # Send POST request to set session as actives
        response = requests.post(url=url, headers=headers)

        return SessionClient._handle_response(response)

    @staticmethod
    def delete_session(
        token: str, title: str, base_url: str = "http://127.0.0.1:8001/api/v1/sessions"
    ):
        """
        Delete a session by title.

        Args:
            token (str): Bearer token for authentication.
            title (str): Title of the session to delete.
            base_url (str): Base endpoint for deleting sessions.

        Returns:
            dict: JSON response confirming deletion.
        """
        # Construct session-specific URL for deletion
        url = base_url + f"/{title}"
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Send DELETE request
        response = requests.delete(url=url, headers=headers)

        return SessionClient._handle_response(response)
