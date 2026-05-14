"""vivado-lens: Agent-native bridge for Xilinx Vivado."""

__version__ = "0.1.0"

from vivado_lens.models.base import VivadoResult, CommandStatus
from vivado_lens.client import VivadoBridge

__all__ = ["VivadoBridge", "VivadoResult", "CommandStatus", "__version__"]
