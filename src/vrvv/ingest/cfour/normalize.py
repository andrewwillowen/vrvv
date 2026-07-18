"""Standardize raw CFOUR data into expected shape."""

from vrvv.core.quantities import StandardData

from .raw import RawDataCFOUR


def normalize_cfour_data(raw_data: RawDataCFOUR) -> StandardData:
    """Convert original units, organization of CFOUR data into StandardData"""
    pass
