#!/usr/bin/env python3
"""
Test suite for TBIB Scraper
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

from tbib_scraper import (
    TbibScraper,
    TaskManager,
    STATUS_PENDING,
    STATUS_COMPLETE,
    BASE_URL
)


class TestTbibScraper(unittest.TestCase):
    """Test cases for TbibScraper class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scraper = TbibScraper(throttle=0)  # No throttle for tests
    
    def test_build_search_url(self):
        """Test search URL construction"""
        # Single tag
        url = self.scraper._build_search_url("honma_meiko")
        self.assertIn("tags=honma_meiko", url)
        
        # Multiple tags
        url = self.scraper._build_search_url("honma_meiko ano_hi_mita_hana")
        self.assertIn("tags=honma_meiko+ano_hi_mita_hana", url)
        
        # Special characters should be encoded
        url = self.scraper._build_search_url("tag with spaces")
        self.assertIn("tag+with+spaces", url)
    
    def test_extract_post_ids_from_page(self):
        """Test post ID extraction from HTML"""
        html = '''
        <div id="post-list">
            <div class="content">
                <div><span><a id="p26054136" href="...">Link</a></span></div>
                <div><span><a id="p26054137" href="...">Link</a></span></div>
                <div><span><a id="p26054138" href="...">Link</a></span></div>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        post_ids = self.scraper._extract_post_ids_from_page(soup)
        
        self.assertEqual(len(post_ids), 3)
        self.assertIn(26054136, post_ids)
        self.assertIn(26054137, post_ids)
        self.assertIn(26054138, post_ids)
    
    def test_extract_post_ids_empty_page(self):
        """Test extraction from empty page"""
        html = '<div id="post-list"><div class="content"></div></div>'
        soup = BeautifulSoup(html, 'html.parser')
        post_ids = self.scraper._extract_post_ids_from_page(soup)
        
        self.assertEqual(len(post_ids), 0)
    
    @patch('tbib_scraper.BeautifulSoup')
    @patch.object(TbibScraper, '_make_request')
    def test_get_post_details_success(self, mock_request, mock_soup):
        """Test successful post details extraction"""
        # Mock HTML response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html></html>'
        mock_request.return_value = mock_response
        
        # Mock BeautifulSoup parsing
        mock_soup_instance = MagicMock()
        mock_soup.return_value = mock_soup_instance
        
        # Mock finding original image link
        mock_link = Mock()
        mock_link.get_text.return_value = "Original image"
        mock_link.get.return_value = "//tbib.org//images/test.png"
        mock_soup_instance.select.return_value = [mock_link]
        
        # Mock tag sidebar
        mock_sidebar = Mock()
        mock_h6_copyright = Mock()
        mock_h6_copyright.name = 'h6'
        mock_h6_copyright.get_text.return_value = "Copyright"
        
        mock_li = Mock()
        mock_li.name = 'li'
        mock_li.get.return_value = ['tag-type-copyright']
        mock_tag_link = Mock()
        mock_tag_link.get_text.return_value = "test_series"
        mock_li.select_one.return_value = mock_tag_link
        
        mock_sidebar.find_all.return_value = [mock_h6_copyright, mock_li]
        mock_soup_instance.select_one.return_value = mock_sidebar
        
        image_url, tags = self.scraper.get_post_details(12345)
        
        self.assertTrue(image_url.startswith('https:'))
        self.assertIn('copyright', tags)
    
    def test_proxy_setup(self):
        """Test proxy configuration"""
        scraper = TbibScraper(proxy="http://localhost:8080")
        self.assertIsNotNone(scraper.proxy_config)
        self.assertEqual(scraper.proxy_config['http'], 'http://localhost:8080')
        
        # With auth
        scraper = TbibScraper(proxy="http://localhost:8080", proxy_auth="user:pass")
        self.assertIn('user:pass', scraper.proxy_config['http'])


class TestTaskManager(unittest.TestCase):
    """Test cases for TaskManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.task_folder = Path(self.test_dir) / "test_task"
        self.task_folder.mkdir()
        (self.task_folder / "posts").mkdir()
    
    def tearDown(self):
        """Clean up test files"""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_sanitize_tags(self):
        """Test tag sanitization for folder names"""
        # Basic sanitization
        result = TaskManager.sanitize_tags("honma_meiko")
        self.assertEqual(result, "honma_meiko")
        
        # Spaces to underscores
        result = TaskManager.sanitize_tags("honma meiko test")
        self.assertEqual(result, "honma_meiko_test")
        
        # Special characters removed
        result = TaskManager.sanitize_tags("tag@#$%test")
        self.assertEqual(result, "tagtest")
        
        # Lowercase conversion
        result = TaskManager.sanitize_tags("TestTag")
        self.assertEqual(result, "testtag")
        
        # Long tags truncated with hash
        long_tag = "a" * 60
        result = TaskManager.sanitize_tags(long_tag)
        self.assertEqual(len(result), 57)  # 50 chars + _ + 6 hash chars
        self.assertIn("_", result)
    
    def test_create_task_folder(self):
        """Test task folder creation"""
        task_mgr = TaskManager.create_task_folder(Path(self.test_dir), "test_tag")
        
        self.assertTrue(task_mgr.task_folder.exists())
        self.assertTrue((task_mgr.task_folder / "posts").exists())
    
    def test_save_and_load_metadata(self):
        """Test metadata persistence"""
        task_mgr = TaskManager(self.task_folder)
        
        metadata = {
            'search_tags': 'test',
            'total_posts': 10,
            'status': STATUS_PENDING
        }
        
        task_mgr.save_metadata(metadata)
        self.assertTrue(task_mgr.metadata_file.exists())
        
        loaded = task_mgr.load_metadata()
        self.assertEqual(loaded['search_tags'], 'test')
        self.assertEqual(loaded['total_posts'], 10)
    
    def test_save_and_load_post_list(self):
        """Test post list persistence"""
        task_mgr = TaskManager(self.task_folder)
        
        post_list = [
            {'post_id': 123, 'status': STATUS_PENDING},
            {'post_id': 456, 'status': STATUS_COMPLETE}
        ]
        
        task_mgr.save_post_list(post_list)
        self.assertTrue(task_mgr.post_list_file.exists())
        
        loaded = task_mgr.load_post_list()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]['post_id'], 123)
    
    def test_save_image(self):
        """Test image file saving"""
        task_mgr = TaskManager(self.task_folder)
        
        image_data = b'\x89PNG\r\n\x1a\n'  # PNG header
        filename = task_mgr.save_image(12345, image_data, 'png')
        
        self.assertEqual(filename, '12345.png')
        filepath = task_mgr.posts_folder / filename
        self.assertTrue(filepath.exists())
        
        with open(filepath, 'rb') as f:
            saved_data = f.read()
        self.assertEqual(saved_data, image_data)
    
    def test_save_tags(self):
        """Test tags metadata saving"""
        task_mgr = TaskManager(self.task_folder)
        
        tags = {
            'copyright': ['series1'],
            'character': ['char1', 'char2'],
            'artist': [],
            'general': ['tag1'],
            'meta': []
        }
        
        task_mgr.save_tags(12345, tags)
        
        tags_file = task_mgr.posts_folder / '12345_tags.json'
        self.assertTrue(tags_file.exists())
        
        import json
        with open(tags_file, 'r') as f:
            saved_tags = json.load(f)
        
        self.assertEqual(saved_tags['post_id'], 12345)
        self.assertEqual(saved_tags['copyright'], ['series1'])
        self.assertEqual(len(saved_tags['character']), 2)
    
    def test_get_file_size_mb(self):
        """Test file size calculation"""
        task_mgr = TaskManager(self.task_folder)
        
        # Create test file
        test_data = b'x' * (1024 * 1024)  # 1 MB
        task_mgr.save_image(99999, test_data, 'jpg')
        
        size = task_mgr.get_file_size_mb(99999, 'jpg')
        self.assertAlmostEqual(size, 1.0, places=1)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files"""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_folder_collision_handling(self):
        """Test folder name collision resolution"""
        # Create first task
        task_mgr1 = TaskManager.create_task_folder(Path(self.test_dir), "test_tag")
        
        # Create second task with same tags - should get timestamp suffix
        task_mgr2 = TaskManager.create_task_folder(Path(self.test_dir), "test_tag")
        
        self.assertNotEqual(task_mgr1.task_folder, task_mgr2.task_folder)
        self.assertTrue(task_mgr1.task_folder.exists())
        self.assertTrue(task_mgr2.task_folder.exists())


if __name__ == '__main__':
    unittest.main()
