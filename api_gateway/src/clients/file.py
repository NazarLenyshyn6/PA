"""
This module defines the `FileClient` class for interacting with a file
management API service. It provides methods to:

- Retrieve available files
- Retrieve or set the active file for a session
- Upload files with metadata
- Delete files (with validation to prevent deleting the active file)

All methods are implemented as `@staticmethod`s and use the `requests` library
to communicate with an external microservice. The class extends `BaseClient`
to inherit consistent HTTP response handling behavior.
"""

from uuid import UUID
from typing import Optional

import requests
from fastapi import UploadFile, HTTPException, status

from clients.base import BaseClient


class FileClient(BaseClient):
    """
    A client class for performing file-related operations via HTTP.

    This client communicates with a file management microservice to:
    - List files available to a user
    - Manage the active file for a given session
    - Upload new files
    - Delete existing files

    Inherits from:
        BaseClient: Provides `_handle_response()` for error-safe parsing.
    """

    @staticmethod
    def get_files(token: str, url: str = "http://127.0.0.1:8002/api/v1/files"):
        """
        Fetch a list of files accessible to the current user.

        Args:
            token: Bearer token for authentication.
            url: API endpoint for listing files.

        Raises:
            requests.HTTPError: If the request fails or response is invalid.

        Returns:
            dict: Parsed JSON response containing file list.
        """

        # Set authentication header
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Send GET request
        response = requests.get(url=url, headers=headers)

        return FileClient._handle_response(response)

    @staticmethod
    def get_active_file(
        token: str,
        session: UUID,
        base_url: str = "http://127.0.0.1:8002/api/v1/files/active",
    ):
        """
        Retrieve the currently active file for a session.

        Args:
            token: Bearer token for authentication
            session: Session identifier
            base_url: Base endpoint for active file retrieval

        Returns:
            dict: JSON response with active file details
        """

        # Construct URL for session-specific active file
        url = base_url + f"/{session}"

        # Set headers
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Send GET request
        response = requests.get(url=url, headers=headers)

        return FileClient._handle_response(response)

    @staticmethod
    def set_active_file(
        token: str,
        session: UUID,
        file_name: str,
        base_url: str = "http://127.0.0.1:8002/api/v1/files/active",
    ):
        """
        Set a specific file as active for the session.

        Args:
            token: Bearer token for authentication
            session: Session identifier
            file_name: Name of the file to activate
            base_url: Base endpoint for setting active file

        Returns:
            dict: JSON response confirming update
        """
        # Construct URL for session-specific active file
        url = base_url + f"/{session}"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        # Send POST request with JSON payload
        data = {"file_name": file_name}
        response = requests.post(url=url, headers=headers, json=data)

        return FileClient._handle_response(response)

    @staticmethod
    def upload_file(
        token: str,
        file_name: str,
        session_id: UUID,
        file: UploadFile,
        url="http://127.0.0.1:8002/api/v1/files",
    ):
        """
        Upload a file with associated metadata to the server.

        Args:
            token (str): Bearer token for authentication
            file_name (str): Logical name to store
            session_id (UUID): Session identifier
            file (UploadFile): FastAPI UploadFile object
            url (str): API endpoint for uploading files

        Returns:
            dict: JSON response confirming upload
        """

        # Prepare multipart/form-data payload
        files = {"file": (file.filename, file.file, file.content_type)}

        # Metadata fields sent along with the file
        data = {
            "file_name": file_name,
            "session_id": session_id,
        }

        # Authorization header
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Send POST request
        response = requests.post(url=url, files=files, data=data, headers=headers)

        return FileClient._handle_response(response)

    @staticmethod
    def delete_file(
        token: str,
        file_name: str,
        active_file_name: Optional[str],
        base_url: str = "http://127.0.0.1:8002/api/v1/files",
    ):
        """
        Delete a file from the server, ensuring it is not currently active.

        Args:
            token: Bearer token for authentication
            file_name: File name to delete
            active_file_name: Currently active file name
            base_url: Base endpoint for deleting files

        Raises:
            HTTPException: If the file to delete is currently active

        Returns:
            dict: JSON response confirming deletion
        """
        # Prevent deletion of active file
        if file_name == active_file_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delite active file; please deactivate it first",
            )

        # Construct URL for deletion
        url = base_url + f"/{file_name}"
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Send DELETE request
        response = requests.delete(url=url, headers=headers)

        return FileClient._handle_response(response)
