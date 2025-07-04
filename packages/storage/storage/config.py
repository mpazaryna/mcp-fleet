"""
Storage configuration management
"""

import os
from typing import Literal

from pydantic import BaseModel, Field


class StorageConfig(BaseModel):
    """Configuration for storage backends"""

    backend_type: Literal["json_file", "directory"] = "json_file"
    data_path: str = Field(description="Path to storage directory")
    create_dirs: bool = True
    backup_enabled: bool = False

    @classmethod
    def from_env(cls, prefix: str = "STORAGE") -> "StorageConfig":
        """Create config from environment variables"""
        backend_type_str = os.getenv(f"{prefix}_BACKEND_TYPE", "json_file")
        # Ensure backend_type is valid
        backend_type: Literal["json_file", "directory"] = (
            "json_file" if backend_type_str not in ["json_file", "directory"] else backend_type_str  # type: ignore
        )
        
        return cls(
            backend_type=backend_type,
            data_path=os.getenv(f"{prefix}_PATH", "./data"),
            create_dirs=os.getenv(f"{prefix}_CREATE_DIRS", "true").lower() == "true",
            backup_enabled=os.getenv(f"{prefix}_BACKUP", "false").lower() == "true",
        )
