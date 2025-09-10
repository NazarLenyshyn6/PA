"""
This module defines request models related to session creation.

Models:
    NewSessionRequest: Schema for validating requests to create a new session.
"""

from pydantic import BaseModel


class NewSessionRequest(BaseModel):
    """
    Data model representing a request to create a new session.

    Attributes:
        title (str): The title of the session to be created.
    """

    title: str
