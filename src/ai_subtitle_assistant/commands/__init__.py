"""
This module contains the command-line entry points for the toolset.
"""

from . import transcribe_cmd, translate_cmd, config_cmd

__all__ = ["transcribe_cmd", "translate_cmd", "config_cmd"]
