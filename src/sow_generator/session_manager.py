"""Session Manager for tracking SOW generation progress.

This module manages sessions for SOW generation, tracking progress through
different stages and storing session state in memory.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class GenerationStage(str, Enum):
    """Enumeration of SOW generation stages."""

    IDLE = "idle"
    UPLOADING = "uploading"
    EXTRACTING = "extracting"
    GENERATING = "generating"
    COMPLETE = "complete"
    ERROR = "error"


class SessionManager:
    """Manages SOW generation sessions and their progress."""

    def __init__(self):
        """Initialize the session manager with empty session storage."""
        self.sessions: Dict[str, dict] = {}

    def create_session(
        self,
        proposal_url: str,
        document_title: str = "Generated_SOW"
    ) -> str:
        """Create a new SOW generation session.

        Args:
            proposal_url: Google Drive URL to the proposal file
            document_title: Title for the generated SOW document

        Returns:
            Unique session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "session_id": session_id,
            "proposal_url": proposal_url,
            "document_title": document_title,
            "stage": GenerationStage.IDLE,
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result_url": None,
            "error": None,
            "metadata": {}
        }
        return session_id

    def update_progress(
        self,
        session_id: str,
        stage: GenerationStage,
        progress: int,
        message: Optional[str] = None
    ) -> None:
        """Update the progress of a session.

        Args:
            session_id: Session ID to update
            stage: Current generation stage
            progress: Progress percentage (0-100)
            message: Optional progress message
        """
        if session_id in self.sessions:
            self.sessions[session_id]["stage"] = stage
            self.sessions[session_id]["progress"] = progress
            self.sessions[session_id]["updated_at"] = datetime.now().isoformat()

            if message:
                self.sessions[session_id]["message"] = message

    def set_result(
        self,
        session_id: str,
        result_url: str,
        metadata: Optional[dict] = None
    ) -> None:
        """Set the final result for a completed session.

        Args:
            session_id: Session ID
            result_url: URL to the generated SOW document
            metadata: Optional metadata about the generated document
        """
        if session_id in self.sessions:
            self.sessions[session_id]["result_url"] = result_url
            self.sessions[session_id]["stage"] = GenerationStage.COMPLETE
            self.sessions[session_id]["progress"] = 100
            self.sessions[session_id]["updated_at"] = datetime.now().isoformat()

            if metadata:
                self.sessions[session_id]["metadata"].update(metadata)

    def set_error(
        self,
        session_id: str,
        error: str
    ) -> None:
        """Set an error for a failed session.

        Args:
            session_id: Session ID
            error: Error message
        """
        if session_id in self.sessions:
            self.sessions[session_id]["error"] = error
            self.sessions[session_id]["stage"] = GenerationStage.ERROR
            self.sessions[session_id]["updated_at"] = datetime.now().isoformat()

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data by ID.

        Args:
            session_id: Session ID to retrieve

        Returns:
            Session data dictionary or None if not found
        """
        return self.sessions.get(session_id)

    def get_all_sessions(self) -> Dict[str, dict]:
        """Get all sessions.

        Returns:
            Dictionary of all sessions
        """
        return self.sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# Global session manager instance
session_manager = SessionManager()
