"""Global configuration for Vivado toolchain paths."""

from pathlib import Path
from pydantic import BaseModel, Field


class VivadoConfig(BaseModel):
    """Vivado installation and tool paths."""

    vivado_bin: Path = Field(default=Path("D:/vivado/Vivado/2017.4/bin"))
    surfer_exe: Path = Field(default=Path("D:/surfer/surfer.exe"))

    @property
    def vivado(self) -> Path:
        return self.vivado_bin / "vivado.bat"

    @property
    def xvlog(self) -> Path:
        return self.vivado_bin / "xvlog.bat"

    @property
    def xelab(self) -> Path:
        return self.vivado_bin / "xelab.bat"

    @property
    def xsim(self) -> Path:
        return self.vivado_bin / "xsim.bat"
