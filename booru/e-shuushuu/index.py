#!/usr/bin/env python3
"""
E-Shuushuu module entry point
"""

from .eshuushuu_scraper import (
    EShuushuuScraper,
    TaskManager,
    mode_new,
    mode_resume,
    mode_sync,
    download_posts,
    sync_posts,
    main
)

__all__ = [
    'EShuushuuScraper',
    'TaskManager',
    'mode_new',
    'mode_resume',
    'mode_sync',
    'download_posts',
    'sync_posts',
    'main'
]

__version__ = '1.0'

if __name__ == '__main__':
    main()
