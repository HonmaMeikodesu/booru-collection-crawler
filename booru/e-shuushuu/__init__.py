"""
E-Shuushuu Web Scraper Module

A command-line tool for downloading images and metadata from E-Shuushuu (e-shuushuu.net).
"""

from .eshuushuu_scraper import (
    EShuushuuScraper,
    TaskManager,
    ProxyConnectionError,
    ProxyAuthError,
    ServerRefusedError,
    ImageNotFoundError,
)

__version__ = '1.0'
__author__ = 'Booru Collection Crawler Project'
__all__ = [
    'EShuushuuScraper',
    'TaskManager',
    'ProxyConnectionError',
    'ProxyAuthError',
    'ServerRefusedError',
    'ImageNotFoundError',
]
