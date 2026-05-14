"""Project management commands: open and init."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from vivado_bridge.models.project import ProjectConfig


def open_project(xpr_path: Path) -> ProjectConfig:
    """Parse an existing Vivado .xpr file into ProjectConfig."""
    if not xpr_path.exists():
        raise FileNotFoundError(f".xpr not found: {xpr_path}")

    tree = ET.parse(xpr_path)
    root = tree.getroot()
    project_dir = xpr_path.parent

    part = ""
    for opt in root.iter("Option"):
        if opt.get("Name") == "Part":
            part = opt.get("Val", "")
            break

    src_files: list[str] = []
    tb_files: list[str] = []
    xdc_files: list[str] = []
    top_module = ""
    sim_top = ""

    for fset in root.iter("FileSet"):
        fset_type = fset.get("Type", "")
        for file_elem in fset.iter("File"):
            raw_path = file_elem.get("Path", "")
            resolved = raw_path.replace("$PPRDIR", str(project_dir.as_posix()))
            resolved = str(Path(resolved).resolve())
            if fset_type == "DesignSrcs":
                src_files.append(resolved)
            elif fset_type == "Constrs":
                xdc_files.append(resolved)
            elif fset_type == "SimulationSrcs":
                tb_files.append(resolved)

        for prop in fset.iter("Option"):
            if prop.get("Name") == "TopModule":
                if fset_type == "DesignSrcs":
                    top_module = prop.get("Val", "")
                elif fset_type == "SimulationSrcs":
                    sim_top = prop.get("Val", "")

    for d in ["sim", "synth", "impl", "tcl"]:
        (project_dir / d).mkdir(exist_ok=True)

    cfg = ProjectConfig(
        part=part,
        top=top_module,
        sim_top=sim_top,
        src_files=src_files,
        tb_files=tb_files,
        xdc_files=xdc_files,
        xpr_path=str(xpr_path),
        project_dir=str(project_dir),
    )
    cfg.save(project_dir)
    return cfg


def init_project(project_dir: Path, part: str, top: str = "top") -> ProjectConfig:
    """Initialize a new project directory."""
    for d in ["src", "tb", "tcl", "sim", "synth", "impl"]:
        (project_dir / d).mkdir(parents=True, exist_ok=True)

    cfg = ProjectConfig(part=part, top=top, project_dir=str(project_dir))

    cfg_path = project_dir / "project.json"
    if cfg_path.exists():
        existing = ProjectConfig.load(project_dir)
        cfg = existing.model_copy(update={k: v for k, v in cfg.model_dump().items() if v})

    cfg.save(project_dir)
    return cfg
