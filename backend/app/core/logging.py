"""
Structured Logging Configuration.

Governed by: part1_discovery_engine_implementation_spec.md (Section 25)
Produces structured log format for request observability.
"""

import logging
import sys


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("discovery_engine")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = setup_logging()
