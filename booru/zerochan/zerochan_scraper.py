#!/usr/bin/env python3
"""
Zerochan Web Scraper
A command-line tool for downloading images from Zerochan
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
from urllib.parse import urljoin, urlparse, quote
import logging

import requests
from bs4 import BeautifulSoup


# Constants
BASE_URL = "https://www.zerochan.net"
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

class ServerResourceNotFoundError(Exception):
    """Raised when server returns 404"""
    pass


class ZerochanScraper:
    """Main scraper class for Zerochan"""
    
    def __init__(self, throttle: float = DEFAULT_THROTTLE, 
                 max_retries: int = DEFAULT_MAX_RETRIES,
                 proxy: Optional[str] = None,
                 proxy_auth: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        self.throttle = throttle
        self.max_retries = max_retries
        self.session = requests.Session()
        self.last_request_time = 0
        self.cookies_acquired = False
        self.logged_in = False
        self.username = username
        self.password = password
        
        # Configure browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        })
        
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
        """Test proxy connection to Zerochan"""
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
    
    def _is_anti_bot_page(self, response: requests.Response) -> bool:
        """Check if response is the anti-bot verification page"""
        if response.status_code != 503:
            return False
        
        # Check for anti-bot page markers
        response_text = response.text
        return '/xbotcheck-image.svg' in response_text or 'Checking browser' in response_text
    
    def _login(self) -> bool:
        """Login to Zerochan to access full post data"""
        if not self.username or not self.password:
            return False
        
        try:
            logger.info(f"Logging in as {self.username}...")
            
            # Prepare login form data
            login_url = f"{BASE_URL}/login"
            form_data = {
                'ref': '/',
                'name': self.username,
                'password': self.password,
                'login': '登录'  # Login button text
            }
            
            # Set form-specific headers
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f'{BASE_URL}/login?ref=%2F',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Make login request
            self._throttle_request()
            response = self.session.post(login_url, data=form_data, headers=headers, timeout=30, allow_redirects=True)
            
            # Check if login was successful
            # Successful login typically redirects and sets cookies
            if response.status_code == 200:
                # Verify login by checking if session cookies were set
                if 'z_id' in self.session.cookies or 'z_hash' in self.session.cookies:
                    logger.info("Login successful")
                    self.logged_in = True
                    return True
                else:
                    logger.warning("Login request completed but session cookies not found")
                    return False
            else:
                logger.warning(f"Login request returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Login failed: {e}")
            return False
    
    def _acquire_cookies(self) -> bool:
        """Acquire cookies by requesting the anti-bot verification image"""
        try:
            logger.info("Anti-bot verification detected, acquiring cookies...")
            
            # Request the anti-bot image to get additional cookies
            image_url = f"{BASE_URL}/xbotcheck-image.svg"
            self._throttle_request()
            response = self.session.get(image_url, timeout=30)
            
            # Check if request was successful
            if response.status_code == 200:
                logger.info("Cookie acquisition successful")
                self.cookies_acquired = True
                return True
            else:
                logger.warning(f"Anti-bot image request returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Anti-bot page detected but cookie acquisition failed: {e}")
            return False
    
    def _make_request(self, url: str, retry_count: int = 0) -> requests.Response:
        """Make HTTP request with retry logic"""
        # Perform login if credentials provided and not logged in yet
        if self.username and self.password and not self.logged_in:
            self._login()
        
        self._throttle_request()
        
        try:
            response = self.session.get(url, timeout=30)
            
            # Check for anti-bot page (503 with verification)
            if self._is_anti_bot_page(response):
                if not self.cookies_acquired:
                    # First time encountering anti-bot page, acquire cookies
                    if self._acquire_cookies():
                        # Retry the original request with acquired cookies
                        logger.info(f"Retrying request with acquired cookies: {url}")
                        self._throttle_request()
                        response = self.session.get(url, timeout=30)
                        
                        # Check if still getting 503 after cookie acquisition
                        if self._is_anti_bot_page(response):
                            logger.warning("503 response persists after cookie acquisition")
                            raise ServerRefusedError("Anti-bot verification failed after cookie acquisition")
                    else:
                        # Cookie acquisition failed
                        raise ServerRefusedError("Failed to acquire anti-bot cookies")
                else:
                    # Already acquired cookies but still getting 503
                    logger.warning("503 response persists after cookie acquisition")
                    raise ServerRefusedError("Anti-bot verification failed despite having cookies")
            
            # Check for server refusal
            if response.status_code in [403, 410]:
                logger.error(f"HTTP {response.status_code} - Server refused request")
                logger.error(f"URL: {url}")
                logger.error(f"Headers: {dict(response.headers)}")
                raise ServerRefusedError(f"Server returned {response.status_code}")
            
            # Check for 404
            if response.status_code == 404:
                logger.warning(f"Resource not found: {url}")
                raise ServerResourceNotFoundError(f"Server returned {response.status_code}")
            
            response.raise_for_status()
            return response
            
        except ServerRefusedError:
            raise
        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                delay = DEFAULT_RETRY_DELAY * (RETRY_BACKOFF_MULTIPLIER ** retry_count)
                logger.warning(f"Request eailed: {e}. Retrying in {delay}s... (Attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(delay)
                return self._make_request(url, retry_count + 1)
            else:
                logger.error(f"Request failed after {self.max_retries} retries: {e}")
                raise
    
    def _build_search_url(self, keywords: str) -> str:
        """Build search URL from keywords"""
        # Replace spaces with +
        formatted = keywords.replace(' ', '+')
        # URL encode (quote preserves + and other safe chars)
        encoded = quote(formatted, safe='+,')
        return f"{BASE_URL}/{encoded}"
    
    def get_all_post_ids(self, keywords: str) -> List[int]:
        """Get all post IDs from search results by following pagination"""
        all_post_ids = []
        current_url = self._build_search_url(keywords)
        page_num = 1
        
        while current_url:
            logger.info(f"Fetching page {page_num}...")
            response = self._make_request(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract post IDs from current page
            post_ids = self._extract_post_ids(soup)
            all_post_ids.extend(post_ids)
            logger.info(f"Found {len(post_ids)} posts on page {page_num}")
            
            # Find next page link
            next_link = soup.select_one('nav.pagination > a[rel="next"]')
            if next_link and next_link.get('href'):
                current_url = urljoin(current_url, next_link['href'])
                print(f"next current url: {current_url}")
                page_num += 1
            else:
                # No next page, we're done
                current_url = None
        
        logger.info(f"Total pages found: {page_num}")
        return all_post_ids
    
    def _extract_post_ids(self, soup: BeautifulSoup) -> List[int]:
        """Extract post IDs from page"""
        post_ids = []
        # Find all li elements in ul#thumbs2
        thumbs = soup.select('ul#thumbs2 > li')
        
        for thumb in thumbs:
            post_id = thumb.get('data-id')
            if post_id:
                post_ids.append(int(post_id))
        
        return post_ids
    
    def get_post_details(self, post_id: int) -> Optional[str]:
        """
        Get image URL for a post
        Returns: image_url or None
        """
        url = f"{BASE_URL}/{post_id}"
        
        response = self._make_request(url)
        if response.status_code == 404:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract image URL from JSON-LD
        script_tag = soup.select_one('div#content > script')
        if not script_tag:
            logger.warning(f"Post {post_id}: No script tag found")
            return None
        
        try:
            # Parse JSON from script content
            json_data = json.loads(script_tag.string)
            image_url = json_data.get('contentUrl')
            
            if not image_url:
                logger.warning(f"Post {post_id}: No contentUrl in JSON-LD")
                return None
            
            return image_url
            
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Post {post_id}: Failed to parse JSON-LD: {e}")
            return None
    
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
    def sanitize_keywords(keywords: str) -> str:
        """Sanitize keywords for folder name"""
        # Replace spaces with underscores
        sanitized = keywords.replace(' ', '_')
        # Replace commas with underscores
        sanitized = sanitized.replace(',', '_')
        # Remove special characters except underscore and hyphen
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', sanitized)
        # Convert to lowercase
        sanitized = sanitized.lower()
        # Truncate to 50 characters
        if len(sanitized) > 50:
            # Append hash to ensure uniqueness
            keyword_hash = hashlib.md5(keywords.encode()).hexdigest()[:6]
            sanitized = sanitized[:50] + '_' + keyword_hash
        return sanitized
    
    @staticmethod
    def create_task_folder(storage_path: Path, keywords: str) -> 'TaskManager':
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
        folder_name = TaskManager.sanitize_keywords(keywords)
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
    logger.info(f"Zerochan Scraper v{VERSION}")
    logger.info(f"Mode: new")
    logger.info(f"Keywords: {args.keywords}")
    logger.info(f"Storage: {args.storage_path}")
    
    # Create scraper
    scraper = ZerochanScraper(
        throttle=args.throttle,
        max_retries=args.max_retries,
        proxy=args.proxy,
        proxy_auth=args.proxy_auth,
        username=args.username,
        password=args.password
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
    task_manager = TaskManager.create_task_folder(Path(args.storage_path), args.keywords)
    
    # Initialize metadata
    metadata = {
        'search_keywords': args.keywords,
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
        # Get all post IDs
        logger.info("Fetching search results...")
        all_post_ids = scraper.get_all_post_ids(args.keywords)
        logger.info(f"Total posts found: {len(all_post_ids)}")
        
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
        logger.error(f'  python zerochan_scraper.py --mode resume --task-path "{task_manager.task_folder}"')
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
    logger.info(f"Zerochan Scraper v{VERSION}")
    logger.info(f"Mode: resume")
    logger.info(f"Task path: {args.task_path}")
    
    # Load task
    task_manager = TaskManager(Path(args.task_path))
    metadata = task_manager.load_metadata()
    post_list = task_manager.load_post_list()
    
    logger.info(f"Keywords: {metadata['search_keywords']}")
    
    # Create scraper
    scraper = ZerochanScraper(
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
        logger.error(f'  python zerochan_scraper.py --mode resume --task-path "{task_manager.task_folder}"')
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
    logger.info(f"Zerochan Scraper v{VERSION}")
    logger.info(f"Mode: sync")
    logger.info(f"Task path: {args.task_path}")
    
    # Load task
    task_manager = TaskManager(Path(args.task_path))
    metadata = task_manager.load_metadata()
    post_list = task_manager.load_post_list()
    
    logger.info(f"Keywords: {metadata['search_keywords']}")
    
    # Create scraper
    scraper = ZerochanScraper(
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


def download_posts(scraper: ZerochanScraper, task_manager: TaskManager, 
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
            image_url = scraper.get_post_details(post_id)
            
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
            
        except ServerRefusedError:
            post['status'] = STATUS_FAIL
            task_manager.save_post_list(post_list)
            raise
        except Exception as e:
            logger.error(f"Post {post_id}: Download failed - {e}")
            post['status'] = STATUS_FAIL
            task_manager.save_post_list(post_list)
            # Continue to next post


def sync_posts(scraper: ZerochanScraper, task_manager: TaskManager,
               metadata: Dict, post_list: List[Dict]):
    """Sync task with remote server to get new posts"""
    keywords = metadata['search_keywords']
    
    # Get current post list from server
    logger.info("Fetching current post list from server...")
    remote_post_ids = scraper.get_all_post_ids(keywords)
    
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
        description='Zerochan Web Scraper - Download images from Zerochan',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--mode', required=True, choices=['new', 'resume', 'sync'],
                       help='Operation mode')
    
    # Mode-specific arguments
    parser.add_argument('--keywords', help='Search keywords (required for new mode)')
    parser.add_argument('--storage-path', help='Storage path (required for new mode)')
    parser.add_argument('--task-path', help='Task folder path (required for resume/sync modes)')
    
    # Optional arguments
    parser.add_argument('--throttle', type=float, default=DEFAULT_THROTTLE,
                       help=f'Seconds between requests (default: {DEFAULT_THROTTLE})')
    parser.add_argument('--max-retries', type=int, default=DEFAULT_MAX_RETRIES,
                       help=f'Maximum retry attempts (default: {DEFAULT_MAX_RETRIES})')
    parser.add_argument('--proxy', help='Proxy server URL (HTTP/HTTPS/SOCKS5)')
    parser.add_argument('--proxy-auth', help='Proxy authentication (username:password)')
    parser.add_argument('--username', help='Zerochan account username for login')
    parser.add_argument('--password', help='Zerochan account password for login')
    
    args = parser.parse_args()
    
    # Validate mode-specific arguments
    if args.mode == 'new':
        if not args.keywords or not args.storage_path:
            logger.error("--keywords and --storage-path are required for new mode")
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
