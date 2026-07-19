"""
Methods for configuring logging (using loguru).
"""

import sys

from loguru import logger


def configure_logging(level: str) -> None:
    """Configure default logging for vrvv package"""
    normalized_level = level.upper()
    logger.remove()
    logger.add(
        sys.stderr,
        level=normalized_level,
        format="<level>{level: <8}</level> | {message}",
    )
    logger.debug("Configured logging with level '{}'.", normalized_level)
