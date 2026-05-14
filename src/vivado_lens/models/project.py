"""Project configuration model (replaces raw project.json dict)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    """Vivado project configuration."""

    part: str
    top: str = "top"
    sim_top: str = ""
    src_files: list[str] = Field(default_factory=list)
    tb_files: list[str] = Field(default_factory=list)
    xdc_files: list[str] = Field(default_factory=list)
    xpr_path: str = ""
    project_dir: str = ""

    @classmethod
    def load(cls, project_dir: Path) -> "ProjectConfig":
        """Load from project.json in the given directory."""
        import json

        cfg_path = project_dir / "project.json"
        if not cfg_path.exists():
            raise FileNotFoundError(f"project.json not found in {project_dir}")
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        return cls(**data)

    def save(self, project_dir: Path) -> None:
        """Write to project.json."""
        import json

        cfg_path = project_dir / "project.json"
        cfg_path.write_text(
            json.dumps(self.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
