"""Standardize raw CFOUR data into expected shape."""

from loguru import logger

from vrvv.core.quantities import StandardData
from vrvv.ingest.cfour.raw import RawDataCFOUR


def normalize_cfour_data(raw_data: RawDataCFOUR) -> StandardData:
    """Convert original units, organization of CFOUR data into StandardData"""
    logger.info("CFOUR normalization requested for '{}'.", raw_data.source_path)
    message = "CFOUR normalization logic is not implemented yet."
    raise NotImplementedError(message)
