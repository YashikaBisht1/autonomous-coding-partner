"""
File system operations for generated projects
"""
import os
import shutil
import logging
from typing import List, Dict, Any
from pathlib import Path
import aiofiles
import json

logger = logging.getLogger(__name__)


class InvalidFilePathError(ValueError):
    """Raised when a requested file path is outside the project workspace."""


class FileManager:
    """Manages file operations for generated projects"""

    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"FileManager using workspace: {self.workspace_path.absolute()}")

    def _get_safe_path(self, project_id: str, file_path: str) -> Path:
        """
        Build a safe path under the project directory.

        Prevents path traversal attacks by resolving the final path and ensuring
        it remains inside the project's workspace directory.
        """
        project_dir = (self.workspace_path / project_id).resolve()
        # Normalise the requested path and resolve against project_dir
        requested_path = (project_dir / file_path).resolve()

        try:
            requested_path.relative_to(project_dir)
        except ValueError:
            # Attempted traversal outside the project directory
            logger.warning(
                "Blocked path traversal attempt for project %s: %s",
                project_id,
                file_path,
            )
            raise InvalidFilePathError("Invalid file path")

        return requested_path

    def create_project_directory(self, project_id: str) -> Path:
        """Create a directory for a project"""
        project_dir = self.workspace_path / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created project directory: {project_dir}")
        return project_dir

    def get_project_dir(self, project_id: str) -> str:
        """Get the absolute path to a project directory"""
        return str((self.workspace_path / project_id).resolve())

    async def save_file(self, project_id: str, file_path: str, content: str) -> bool:
        """Save a file to the project directory"""
        try:
            project_dir = self.workspace_path / project_id
            project_dir.mkdir(parents=True, exist_ok=True)

            full_path = self._get_safe_path(project_id, file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(full_path, "w", encoding="utf-8") as f:
                await f.write(content)

            logger.info(f"Saved file: {full_path} ({len(content)} chars)")
            return True

        except InvalidFilePathError as e:
            logger.error("Invalid path for saving file %s: %s", file_path, e)
            return False
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            return False

    async def read_file(self, project_id: str, file_path: str) -> str:
        """Read file content"""
        try:
            full_path = self._get_safe_path(project_id, file_path)
            async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return content
        except InvalidFilePathError as e:
            logger.error("Invalid path for reading file %s: %s", file_path, e)
            return ""
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

    def get_project_files(self, project_id: str) -> List[str]:
        """Get list of files in project"""
        project_dir = self.workspace_path / project_id
        if not project_dir.exists():
            return []

        files: List[str] = []
        for root, dirs, filenames in os.walk(project_dir):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), project_dir)
                files.append(rel_path)

        return files


# Create a global instance
file_manager = FileManager()