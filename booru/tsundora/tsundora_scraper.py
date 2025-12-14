#!/usr/bin/env python3
"""
Tsundora Web Scraper
A command-line tool for downloading images from Tsundora
"""

import argparse
import sys
import os
import json
import time
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, quote_plus
import logging

import requests
from bs4 import BeautifulSoup


# Constants
BASE_URL = "https://tsundora.com"
VERSION = "1.0"
DEFAULT_THROTTLE = 2.5
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 5
RETRY_BACKOFF_MULTIPLIER = 2

# Exit codes
EXIT_SUCCESS = 0
EXIT_INVALID_ARGS = 1
EXIT_TASK_VALIDATION_FAILED = 2
EXIT_NETWORK_ERROR = 3
EXIT_SERVER_REFUSED = 4
EXIT_STORAGE_ERROR = 5
EXIT_PROXY_CONNECTION_FAILED = 6
EXIT_PROXY_AUTH_FAILED = 7

# Task statuses
STATUS_PENDING = "PENDING"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_COMPLETE = "COMPLETE"
STATUS_FAILED = "FAILED"
STATUS_FAIL = "FAIL"


def setup_logging():
    """Configure logging for the scraper"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class ProxyConnectionError(Exception):
    """Raised when proxy connection fails"""
    pass


class ProxyAuthError(Exception):
    """Raised when proxy authentication fails"""
    pass


class ServerRefusedError(Exception):
    """Raised when server returns 403/410"""
    pass


class ImageNotFoundError(Exception):
    """Raised when original image link not found"""
    pass


class TsundoraScraper:
    """Main scraper class for Tsundora"""
    
    def __init__(self, throttle: float = DEFAULT_THROTTLE, 
                 max_retries: int = DEFAULT_MAX_RETRIES,
                 proxy: Optional[str] = None,
                 proxy_auth: Optional[str] = None):
        self.throttle = throttle
        self.max_retries = max_retries
        self.session = requests.Session()
        self.last_request_time = 0
        
        # Setup proxy if provided
        self.proxy_config = self._setup_proxy(proxy, proxy_auth)
        if self.proxy_config:
            self.session.proxies.update(self.proxy_config)
            logger.info(f"Proxy: {self._get_proxy_display_string(proxy, proxy_auth)}")
    
    def _setup_proxy(self, proxy: Optional[str], proxy_auth: Optional[str]) -> Optional[Dict]:
        """Setup proxy configuration"""
        if not proxy:
            return None
        
        # Parse proxy URL
        parsed = urlparse(proxy)
        
        # Handle proxy authentication
        if proxy_auth and '@' not in proxy:
            # Separate auth provided, inject into URL
            scheme = parsed.scheme
            netloc = f"{proxy_auth}@{parsed.netloc}"
            proxy_url = f"{scheme}://{netloc}"
        else:
            proxy_url = proxy
        
        # Return proxy dict for requests library
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def _get_proxy_display_string(self, proxy: str, proxy_auth: Optional[str]) -> str:
        """Get proxy display string without exposing credentials"""
        parsed = urlparse(proxy)
        auth_status = ""
        if proxy_auth or '@' in proxy:
            auth_status = " (authenticated)"
        return f"{parsed.scheme}://{parsed.netloc}{auth_status}"
    
    def _validate_proxy(self):
        """Test proxy connection to Tsundora"""
        try:
            logger.info("Testing proxy connection...")
            response = self.session.get(BASE_URL, timeout=10)
            response.raise_for_status()
            logger.info("Proxy connection successful")
        except requests.exceptions.ProxyError as e:
            logger.error(f"Proxy connection failed: {e}")
            raise ProxyConnectionError("Failed to connect through proxy")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 407:
                logger.error("Proxy authentication failed")
                raise ProxyAuthError("Proxy authentication required or credentials invalid")
            raise
    
    def _throttle_request(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.throttle:
            time.sleep(self.throttle - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, retry_count: int = 0) -> requests.Response:
        """Make HTTP request with retry logic"""
        self._throttle_request()
        
        try:
            response = self.session.get(url, timeout=30)
            
            # Check for server refusal
            if response.status_code in [403, 410]:
                logger.error(f"HTTP {response.status_code} - Server refused request")
                logger.error(f"URL: {url}")
                logger.error(f"Headers: {dict(response.headers)}")
                raise ServerRefusedError(f"Server returned {response.status_code}")
            
            # Check for 404
            if response.status_code == 404:
                logger.warning(f"Resource not found: {url}")
                return response
            
            response.raise_for_status()
            return response
            
        except ServerRefusedError:
            raise
        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                delay = DEFAULT_RETRY_DELAY * (RETRY_BACKOFF_MULTIPLIER ** retry_count)
                logger.warning(f"Request failed: {e}. Retrying in {delay}s... (Attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(delay)
                return self._make_request(url, retry_count + 1)
            else:
                logger.error(f"Request failed after {self.max_retries} retries: {e}")
                raise
    
    def _build_search_url(self, keyword: str, page: int = 1) -> str:
        """Build search URL with proper keyword encoding"""
        # URL encode the keyword
        encoded_keyword = quote_plus(keyword)
        
        if page == 1:
            return f"{BASE_URL}/?s={encoded_keyword}"
        else:
            return f"{BASE_URL}/page/{page}?s={encoded_keyword}"
    
    def get_all_post_ids(self, keyword: str) -> List[int]:
        """
        Get all post IDs by following pagination until exhaustion
        Returns list of post IDs
        """
        all_post_ids = []
        page_num = 1
        
        while True:
            logger.info(f"Fetching page {page_num}...")
            current_url = self._build_search_url(keyword, page_num)
            response = self._make_request(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract post IDs from current page
            post_ids = self._extract_post_ids_from_page(soup)
            if not post_ids:
                # No posts found on this page, we've reached the end
                break
            
            all_post_ids.extend(post_ids)
            logger.info(f"Found {len(post_ids)} posts on page {page_num}")
            
            # Find next page link
            next_link = soup.select_one('.next.page-numbers')
            if next_link and next_link.get('href'):
                page_num += 1
            else:
                # No more pages
                break
        
        logger.info(f"Total pages traversed: {page_num}")
        logger.info(f"Total posts found: {len(all_post_ids)}")
        return all_post_ids
    
    def _extract_post_ids_from_page(self, soup: BeautifulSoup) -> List[int]:
        """Extract post IDs from a search results page"""
        post_ids = []
        
        # Find all post preview links: .article_content .article-box a
        post_links = soup.select('.article_content .article-box a')
        if not post_links:
            return post_ids
        
        for link in post_links:
            # Get href attribute (format: https://tsundora.com/{post_id})
            href = link.get('href')
            if href:
                try:
                    # Extract post ID from URL
                    # Example: https://tsundora.com/165099 -> 165099
                    post_id_str = href.rstrip('/').split('/')[-1]
                    post_id = int(post_id_str)
                    post_ids.append(post_id)
                except (ValueError, IndexError):
                    logger.warning(f"Invalid post URL format: {href}")
                    continue
        
        return post_ids
    
    def get_post_details(self, post_id: int) -> Tuple[Optional[str], Dict[str, List[str]]]:
        """
        Get image URL for a post
        Returns: (image_url, tags_dict)
        Note: Tsundora doesn't have tags, so tags_dict will be empty
        """
        url = f"{BASE_URL}/{post_id}"
        
        response = self._make_request(url)
        if response.status_code == 404:
            return None, {}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract image URL - find img tag in #main .entry-content
        image_url = None
        img_tag = soup.select_one('#main .entry-content img')
        if img_tag:
            # Get src attribute
            src = img_tag.get('src')
            if src:
                # The src contains size suffix like -960x1024.jpg
                # Example: https://tsundora.com/image/2015/04/ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai-132-960x1024.jpg
                # We need to remove the size suffix to get the original
                # Pattern: filename-WIDTHxHEIGHT.ext -> filename.ext
                # Remove the -WIDTHxHEIGHT pattern before extension
                image_url = re.sub(r'-\d+x\d+(\.[a-z]+)$', r'\1', src)
                # If no pattern matched, use original src
                if image_url == src:
                    image_url = src
        
        if not image_url:
            raise ImageNotFoundError(f"Image not found for post {post_id}")
        
        # Tsundora doesn't have tags, return empty dict
        tags = {}
        
        return image_url, tags
    
    def download_image(self, url: str) -> bytes:
        """Download image to memory"""
        response = self._make_request(url)
        
        # Validate content length if available
        content_length = response.headers.get('Content-Length')
        if content_length:
            expected_length = int(content_length)
            actual_length = len(response.content)
            if expected_length != actual_length:
                raise ValueError(f"Content length mismatch: expected {expected_length}, got {actual_length}")
        
        return response.content


class TaskManager:
    """Manages task folder structure and metadata"""
    
    def __init__(self, task_folder: Path):
        self.task_folder = Path(task_folder)
        self.metadata_file = self.task_folder / "task_metadata.json"
        self.post_list_file = self.task_folder / "post_list.json"
        self.posts_folder = self.task_folder / "posts"
    
    @staticmethod
    def sanitize_keyword(keyword: str) -> str:
        """Sanitize keyword for folder name"""
        # Replace spaces with underscores
        sanitized = keyword.replace(' ', '_')
        # Remove special characters except underscore and hyphen
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', sanitized)
        # Convert to lowercase
        sanitized = sanitized.lower()
        # Truncate to 50 characters
        if len(sanitized) > 50:
            # Append hash to ensure uniqueness
            keyword_hash = hashlib.md5(keyword.encode()).hexdigest()[:6]
            sanitized = sanitized[:50] + '_' + keyword_hash
        return sanitized
    
    @staticmethod
    def create_task_folder(storage_path: Path, keyword: str) -> 'TaskManager':
        """Create new task folder"""
        # Validate storage path
        storage_path = Path(storage_path)
        if not storage_path.exists():
            logger.error(f"Storage path does not exist: {storage_path}")
            sys.exit(EXIT_STORAGE_ERROR)
        
        if not os.access(storage_path, os.W_OK):
            logger.error(f"Storage path is not writable: {storage_path}")
            sys.exit(EXIT_STORAGE_ERROR)
        
        # Create task folder
        folder_name = TaskManager.sanitize_keyword(keyword)
        task_folder = storage_path / folder_name
        
        # If folder exists, append timestamp
        if task_folder.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            task_folder = storage_path / f"{folder_name}_{timestamp}"
        
        task_folder.mkdir(parents=True, exist_ok=True)
        (task_folder / "posts").mkdir(exist_ok=True)
        
        logger.info(f"Creating task folder: {task_folder}")
        
        return TaskManager(task_folder)
    
    def save_metadata(self, metadata: Dict):
        """Save task metadata"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def load_metadata(self) -> Dict:
        """Load task metadata"""
        if not self.metadata_file.exists():
            logger.error(f"Task metadata not found: {self.metadata_file}")
            sys.exit(EXIT_TASK_VALIDATION_FAILED)
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_post_list(self, posts: List[Dict]):
        """Save post list"""
        with open(self.post_list_file, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
    
    def load_post_list(self) -> List[Dict]:
        """Load post list"""
        if not self.post_list_file.exists():
            logger.error(f"Post list not found: {self.post_list_file}")
            sys.exit(EXIT_TASK_VALIDATION_FAILED)
        
        with open(self.post_list_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_image(self, post_id: int, image_data: bytes, extension: str):
        """Save image to disk"""
        filename = f"{post_id}.{extension}"
        filepath = self.posts_folder / filename
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        return filename
    
    def save_tags(self, post_id: int, tags: Dict[str, List[str]]):
        """Save tags metadata"""
        tags_data = {
            'post_id': post_id,
            **tags
        }
        
        filename = f"{post_id}_tags.json"
        filepath = self.posts_folder / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tags_data, f, indent=2, ensure_ascii=False)
    
    def get_file_size_mb(self, post_id: int, extension: str) -> float:
        """Get file size in MB"""
        filename = f"{post_id}.{extension}"
        filepath = self.posts_folder / filename
        
        if filepath.exists():
            size_bytes = filepath.stat().st_size
            return size_bytes / (1024 * 1024)
        return 0.0


def mode_new(args):
    """Execute new task creation mode"""
    logger.info(f"Tsundora Scraper v{VERSION}")
    logger.info(f"Mode: new")
    logger.info(f"Keyword: {args.keyword}")
    logger.info(f"Storage: {args.storage_path}")
    
    # Create scraper
    scraper = TsundoraScraper(
        throttle=args.throttle,
        max_retries=args.max_retries,
        proxy=args.proxy,
        proxy_auth=args.proxy_auth
    )
    
    # Validate proxy if configured
    if args.proxy:
        try:
            scraper._validate_proxy()
        except ProxyConnectionError:
            sys.exit(EXIT_PROXY_CONNECTION_FAILED)
        except ProxyAuthError:
            sys.exit(EXIT_PROXY_AUTH_FAILED)
    
    # Create task folder
    task_manager = TaskManager.create_task_folder(Path(args.storage_path), args.keyword)
    
    # Initialize metadata
    metadata = {
        'search_keyword': args.keyword,
        'storage_path': str(args.storage_path),
        'task_folder': str(task_manager.task_folder),
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
        'last_synced': None,
        'status': STATUS_IN_PROGRESS,
        'total_posts': 0,
        'completed_posts': 0,
        'mode_history': ['new']
    }
    task_manager.save_metadata(metadata)
    
    try:
        # Get all post IDs by traversing pagination
        all_post_ids = scraper.get_all_post_ids(args.keyword)
        
        # Create post list with initial status
        post_list = []
        for post_id in all_post_ids:
            post_list.append({
                'post_id': post_id,
                'status': STATUS_PENDING,
                'image_url': None,
                'file_extension': None,
                'download_timestamp': None
            })
        
        # Update metadata
        metadata['total_posts'] = len(all_post_ids)
        task_manager.save_metadata(metadata)
        task_manager.save_post_list(post_list)
        
        # Download posts
        download_posts(scraper, task_manager, post_list, metadata)
        
        # Mark task as complete
        metadata['status'] = STATUS_COMPLETE
        metadata['last_updated'] = datetime.now().isoformat()
        task_manager.save_metadata(metadata)
        
        logger.info(f"Task complete. Total posts: {metadata['completed_posts']}")
        sys.exit(EXIT_SUCCESS)
        
    except ServerRefusedError as e:
        logger.error(f"Server refused request: {e}")
        logger.error("Task state saved. Resume with:")
        logger.error(f'  python safebooru_scraper.py --mode resume --task-path "{task_manager.task_folder}"')
        metadata['status'] = STATUS_FAILED
        metadata['last_updated'] = datetime.now().isoformat()
        task_manager.save_metadata(metadata)
        sys.exit(EXIT_SERVER_REFUSED)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        metadata['status'] = STATUS_FAILED
        metadata['last_updated'] = datetime.now().isoformat()
        task_manager.save_metadata(metadata)
        sys.exit(EXIT_NETWORK_ERROR)


def mode_resume(args):
    """Execute resume mode"""
    logger.info(f"Tsundora Scraper v{VERSION}")
    logger.info(f"Mode: resume")
    logger.info(f"Task path: {args.task_path}")
    
    # Load task
    task_manager = TaskManager(Path(args.task_path))
    metadata = task_manager.load_metadata()
    post_list = task_manager.load_post_list()
    
    logger.info(f"Keyword: {metadata['search_keyword']}")
    
    # Create scraper
    scraper = TsundoraScraper(
        throttle=args.throttle if hasattr(args, 'throttle') else DEFAULT_THROTTLE,
        max_retries=args.max_retries if hasattr(args, 'max_retries') else DEFAULT_MAX_RETRIES,
        proxy=args.proxy,
        proxy_auth=args.proxy_auth
    )
    
    # Validate proxy if configured
    if args.proxy:
        try:
            scraper._validate_proxy()
        except ProxyConnectionError:
            sys.exit(EXIT_PROXY_CONNECTION_FAILED)
        except ProxyAuthError:
            sys.exit(EXIT_PROXY_AUTH_FAILED)
    
    # Find incomplete posts
    incomplete_posts = [p for p in post_list if p['status'] != STATUS_COMPLETE]
    logger.info(f"Resume info: {len(incomplete_posts)} posts remaining")
    
    # Update mode history
    if 'resume' not in metadata.get('mode_history', []):
        metadata['mode_history'].append('resume')
    
    metadata['status'] = STATUS_IN_PROGRESS
    task_manager.save_metadata(metadata)
    
    try:
        # Resume download
        download_posts(scraper, task_manager, post_list, metadata)
        
        # Download phase complete
        logger.info(f"Download phase complete: {metadata['completed_posts']}/{metadata['total_posts']} posts")
        
        # Auto-trigger sync
        logger.info("Triggering automatic sync operation...")
        sync_posts(scraper, task_manager, metadata, post_list)
        
        # Mark as complete
        metadata['status'] = STATUS_COMPLETE
        metadata['last_updated'] = datetime.now().isoformat()
        task_manager.save_metadata(metadata)
        
        logger.info(f"Task complete. Total posts: {metadata['completed_posts']}")
        sys.exit(EXIT_SUCCESS)
        
    except ServerRefusedError as e:
        logger.error(f"Server refused request: {e}")
        logger.error("Task state saved. Resume with:")
        logger.error(f'  python tsundora_scraper.py --mode resume --task-path "{task_manager.task_folder}"')
        metadata['status'] = STATUS_FAILED
        metadata['last_updated'] = datetime.now().isoformat()
        task_manager.save_metadata(metadata)
        sys.exit(EXIT_SERVER_REFUSED)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        metadata['status'] = STATUS_FAILED
        metadata['last_updated'] = datetime.now().isoformat()
        task_manager.save_metadata(metadata)
        sys.exit(EXIT_NETWORK_ERROR)


def mode_sync(args):
    """Execute sync mode"""
    logger.info(f"Tsundora Scraper v{VERSION}")
    logger.info(f"Mode: sync")
    logger.info(f"Task path: {args.task_path}")
    
    # Load task
    task_manager = TaskManager(Path(args.task_path))
    metadata = task_manager.load_metadata()
    post_list = task_manager.load_post_list()
    
    logger.info(f"Keyword: {metadata['search_keyword']}")
    
    # Create scraper
    scraper = TsundoraScraper(
        throttle=args.throttle if hasattr(args, 'throttle') else DEFAULT_THROTTLE,
        max_retries=args.max_retries if hasattr(args, 'max_retries') else DEFAULT_MAX_RETRIES,
        proxy=args.proxy,
        proxy_auth=args.proxy_auth
    )
    
    # Validate proxy if configured
    if args.proxy:
        try:
            scraper._validate_proxy()
        except ProxyConnectionError:
            sys.exit(EXIT_PROXY_CONNECTION_FAILED)
        except ProxyAuthError:
            sys.exit(EXIT_PROXY_AUTH_FAILED)
    
    # Update mode history
    if 'sync' not in metadata.get('mode_history', []):
        metadata['mode_history'].append('sync')
    
    try:
        sync_posts(scraper, task_manager, metadata, post_list)
        
        metadata['status'] = STATUS_COMPLETE
        metadata['last_updated'] = datetime.now().isoformat()
        task_manager.save_metadata(metadata)
        
        logger.info(f"Task complete. Total posts: {metadata['completed_posts']}")
        sys.exit(EXIT_SUCCESS)
        
    except ServerRefusedError as e:
        logger.error(f"Server refused request: {e}")
        logger.error("Manual intervention required.")
        sys.exit(EXIT_SERVER_REFUSED)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(EXIT_NETWORK_ERROR)


def download_posts(scraper: TsundoraScraper, task_manager: TaskManager, 
                   post_list: List[Dict], metadata: Dict):
    """Download posts from the list"""
    total = len(post_list)
    
    for i, post in enumerate(post_list, 1):
        if post['status'] == STATUS_COMPLETE:
            continue
        
        post_id = post['post_id']
        logger.info(f"Downloading post {i}/{total} (ID: {post_id})")
        
        try:
            # Get post details
            image_url, tags = scraper.get_post_details(post_id)
            
            if not image_url:
                logger.warning(f"Post {post_id}: No image URL found")
                post['status'] = STATUS_FAIL
                task_manager.save_post_list(post_list)
                continue
            
            # Extract file extension
            extension = image_url.split('.')[-1].split('?')[0]
            
            # Download image
            image_data = scraper.download_image(image_url)
            
            # Save image
            filename = task_manager.save_image(post_id, image_data, extension)
            file_size = task_manager.get_file_size_mb(post_id, extension)
            logger.info(f"Image saved: {filename} ({file_size:.1f} MB)")
            
            # Save tags (skip for Tsundora as it has no tags)
            if tags:
                task_manager.save_tags(post_id, tags)
                logger.info(f"Tags saved: {post_id}_tags.json")
            
            # Update post status
            post['status'] = STATUS_COMPLETE
            post['image_url'] = image_url
            post['file_extension'] = extension
            post['download_timestamp'] = datetime.now().isoformat()
            
            # Update metadata
            metadata['completed_posts'] = sum(1 for p in post_list if p['status'] == STATUS_COMPLETE)
            metadata['last_updated'] = datetime.now().isoformat()
            
            # Save progress
            task_manager.save_post_list(post_list)
            task_manager.save_metadata(metadata)
            
        except ImageNotFoundError as e:
            logger.error(f"Post {post_id}: {e}")
            post['status'] = STATUS_FAIL
            task_manager.save_post_list(post_list)
        except ServerRefusedError:
            post['status'] = STATUS_FAIL
            task_manager.save_post_list(post_list)
            raise
        except Exception as e:
            logger.error(f"Post {post_id}: Download failed - {e}")
            post['status'] = STATUS_FAIL
            task_manager.save_post_list(post_list)
            # Continue to next post


def sync_posts(scraper: TsundoraScraper, task_manager: TaskManager,
               metadata: Dict, post_list: List[Dict]):
    """Sync task with remote server to get new posts"""
    keyword = metadata['search_keyword']
    
    # Get current post list from server
    logger.info("Fetching current post list from server...")
    remote_post_ids = scraper.get_all_post_ids(keyword)
    
    # Compare with local
    local_post_ids = set(p['post_id'] for p in post_list)
    new_post_ids = set(remote_post_ids) - local_post_ids
    
    if not new_post_ids:
        logger.info("Sync complete: No new posts found")
        metadata['last_synced'] = datetime.now().isoformat()
        task_manager.save_metadata(metadata)
        return
    
    logger.info(f"Found {len(new_post_ids)} new posts")
    
    # Add new posts to list
    for post_id in new_post_ids:
        post_list.append({
            'post_id': post_id,
            'status': STATUS_PENDING,
            'image_url': None,
            'file_extension': None,
            'download_timestamp': None
        })
    
    # Update metadata
    metadata['total_posts'] = len(post_list)
    task_manager.save_post_list(post_list)
    task_manager.save_metadata(metadata)
    
    # Download new posts
    new_posts = [p for p in post_list if p['post_id'] in new_post_ids]
    download_posts(scraper, task_manager, new_posts, metadata)
    
    # Update sync timestamp
    metadata['last_synced'] = datetime.now().isoformat()
    metadata['total_posts'] = len(post_list)
    metadata['completed_posts'] = sum(1 for p in post_list if p['status'] == STATUS_COMPLETE)
    task_manager.save_metadata(metadata)
    task_manager.save_post_list(post_list)
    
    logger.info(f"Sync complete: {len(new_post_ids)} new posts downloaded")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Tsundora Web Scraper - Download images from Tsundora',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--mode', required=True, choices=['new', 'resume', 'sync'],
                       help='Operation mode')
    
    # Mode-specific arguments
    parser.add_argument('--keyword', help='Search keyword (required for new mode)')
    parser.add_argument('--storage-path', help='Storage path (required for new mode)')
    parser.add_argument('--task-path', help='Task folder path (required for resume/sync modes)')
    
    # Optional arguments
    parser.add_argument('--throttle', type=float, default=DEFAULT_THROTTLE,
                       help=f'Seconds between requests (default: {DEFAULT_THROTTLE})')
    parser.add_argument('--max-retries', type=int, default=DEFAULT_MAX_RETRIES,
                       help=f'Maximum retry attempts (default: {DEFAULT_MAX_RETRIES})')
    parser.add_argument('--proxy', help='Proxy server URL (HTTP/HTTPS/SOCKS5)')
    parser.add_argument('--proxy-auth', help='Proxy authentication (username:password)')
    
    args = parser.parse_args()
    
    # Validate mode-specific arguments
    if args.mode == 'new':
        if not args.keyword or not args.storage_path:
            logger.error("--keyword and --storage-path are required for new mode")
            sys.exit(EXIT_INVALID_ARGS)
        mode_new(args)
    elif args.mode in ['resume', 'sync']:
        if not args.task_path:
            logger.error("--task-path is required for resume/sync modes")
            sys.exit(EXIT_INVALID_ARGS)
        if args.mode == 'resume':
            mode_resume(args)
        else:
            mode_sync(args)


if __name__ == '__main__':
    main()
