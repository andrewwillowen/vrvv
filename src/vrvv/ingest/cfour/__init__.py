"""
CFOUR parser plugin for vrvv.

Contains methods solely for finding and parsing
relevant data in CFOUR files, then exposing that
through the plugin system for use in the rest of
the vrvv package.
"""

from vrvv.ingest.cfour.normalize import normalize_cfour_data
from vrvv.ingest.cfour.parser import CFOUR_PLUGIN, CFOURParser
from vrvv.ingest.cfour.raw import HarmonicFrequencies, RawDataCFOUR

__all__ = [
    "CFOUR_PLUGIN",
    "CFOURParser",
    "HarmonicFrequencies",
    "RawDataCFOUR",
    "normalize_cfour_data",
]
