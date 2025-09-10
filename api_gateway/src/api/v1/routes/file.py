"""
File management API routes.

This module provides endpoints for listing, uploading, activating, and deleting
files. It leverages the `FileClient` for file operations and `SessionClient`
for resolving the active session. OAuth2 token authentication is required for
all endpoints.

Endpoints:
    GET /files/: List all available files for the authenticated user.
    GET /files/active: Retrieve the currently active file for the session.
    POST /files/active/: Set a specific file as active for the session.
    POST /files/: Upload a new file with metadata.
    DELETE /files/{file_name}: Delete a specific file (cannot delete active file).
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer

from schemas.file import ActiveFileRequest
from clients.file import FileClient
from clients.session import SessionClient

# OAuth2 dependency for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/gateway/auth/login")

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/")
def get_files(token: str = Depends(oauth2_scheme)):
    """
    List all files accessible to the authenticated user.

    Args:
        token: OAuth2 bearer token provided via dependency.

    Returns:
        dict: JSON response containing list of files.
    """
    return FileClient.get_files(token=token)


@router.get("/active")
def get_active_file(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the currently active file for the user's session.

    Args:
        token: OAuth2 bearer token provided via dependency.

    Returns:
        dict: JSON response containing details of the active file.
    """
    # Resolve active session ID
    session = SessionClient.get_active_session_id(token=token)

    return FileClient.get_active_file(token=token, session=session)


@router.post("/active/")
def set_active_file(
    active_file: ActiveFileRequest, token: str = Depends(oauth2_scheme)
):
    """
    Set a specific file as active for the current session.

    Args:
        active_file: Pydantic model containing file_name.
        token: OAuth2 bearer token provided via dependency.

    Returns:
        dict: JSON response confirming the active file has been updated.
    """

    # Resolve active session ID
    session = SessionClient.get_active_session_id(token=token)

    # Update active file for session
    return FileClient.set_active_file(
        token=token, session=session, file_name=active_file.file_name
    )


@router.post("/")
def upload_file(
    file_name: str = Form(),
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
):
    """
    Upload a new file with associated metadata to the server.

    Args:
        file_nam: Logical name of the file.
        description: Description for the file.
        file: File object provided by FastAPI form.
        toke: OAuth2 bearer token provided via dependency.

    Returns:
        dict: JSON response confirming the file has been uploaded.
    """
    # Resolve active session ID
    session_id = SessionClient.get_active_session_id(token=token)

    return FileClient.upload_file(
        token=token,
        file=file,
        file_name=file_name,
        session_id=session_id,
    )


@router.delete("/{file_name}")
def delete_file(file_name: str, token: str = Depends(oauth2_scheme)):
    """
    Delete a specific file from the server.

    Note: The currently active file cannot be deleted. Attempting to do so
    will raise an error in FileClient.

    Args:
        file_name: Name of the file to delete.
        token: OAuth2 bearer token provided via dependency.

    Returns:
        dict: JSON response confirming the file has been deleted.
    """
    # Resolve active session ID
    session_id = SessionClient.get_active_session_id(token=token)

    # Fetch current active file
    active_file = FileClient.get_active_file(token=token, session=session_id)
    active_file_name = active_file["file_name"]

    return FileClient.delete_file(
        token=token, file_name=file_name, active_file_name=active_file_name
    )
