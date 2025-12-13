#!/usr/bin/env python3
"""
Rule34 Scraper Entry Point
Provides a simple import interface for the Rule34 scraper
"""

from .rule34_scraper import (
    Rule34Scraper,
    TaskManager,
    BASE_URL,
    VERSION,
    ImageNotFoundError,
    ServerRefusedError,
    ProxyConnectionError,
    ProxyAuthError
)

__all__ = [
    'Rule34Scraper',
    'TaskManager',
    'BASE_URL',
    'VERSION',
    'ImageNotFoundError',
    'ServerRefusedError',
    'ProxyConnectionError',
    'ProxyAuthError'
]
