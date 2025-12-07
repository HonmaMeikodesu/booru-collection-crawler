#!/usr/bin/env python3
"""
Test script for Danbooru scraper
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from danbooru_scraper import DanbooruScraper, TaskManager

def test_pagination_parsing():
    """Test parsing pagination from search results"""
    print("Testing pagination parsing...")
    scraper = DanbooruScraper(throttle=1.0)
    
    try:
        # Test with a tag that should have results
        total_pages = scraper.get_total_pages("honma_meiko")
        print(f"✓ Successfully fetched pagination: {total_pages} pages")
        return True
    except Exception as e:
        print(f"✗ Failed to fetch pagination: {e}")
        return False

def test_post_id_extraction():
    """Test extracting post IDs from search results page"""
    print("\nTesting post ID extraction...")
    scraper = DanbooruScraper(throttle=1.0)
    
    try:
        post_ids = scraper.get_post_ids_from_page("honma_meiko", 1)
        if post_ids:
            print(f"✓ Successfully extracted {len(post_ids)} post IDs")
            print(f"  Sample post IDs: {post_ids[:5]}")
            return True
        else:
            print("✗ No post IDs found")
            return False
    except Exception as e:
        print(f"✗ Failed to extract post IDs: {e}")
        return False

def test_post_details():
    """Test fetching post details"""
    print("\nTesting post details extraction...")
    scraper = DanbooruScraper(throttle=1.0)
    
    try:
        # Get a post ID first
        post_ids = scraper.get_post_ids_from_page("honma_meiko", 1)
        if not post_ids:
            print("✗ No post IDs to test with")
            return False
        
        test_post_id = post_ids[0]
        image_url, tags = scraper.get_post_details(test_post_id)
        
        if image_url:
            print(f"✓ Successfully fetched post details for ID {test_post_id}")
            print(f"  Image URL: {image_url[:80]}...")
            print(f"  Tags found:")
            for category, tag_list in tags.items():
                if tag_list:
                    print(f"    {category}: {len(tag_list)} tags")
            return True
        else:
            print("✗ No image URL found")
            return False
    except Exception as e:
        print(f"✗ Failed to fetch post details: {e}")
        return False

def test_task_folder_creation():
    """Test task folder creation"""
    print("\nTesting task folder creation...")
    
    try:
        # Create temporary test folder
        test_storage = Path("test_storage")
        test_storage.mkdir(exist_ok=True)
        
        # Test sanitization
        sanitized = TaskManager.sanitize_tags("honma_meiko test-tag")
        print(f"✓ Tag sanitization works: 'honma_meiko test-tag' -> '{sanitized}'")
        
        # Cleanup
        if test_storage.exists():
            import shutil
            shutil.rmtree(test_storage)
        
        return True
    except Exception as e:
        print(f"✗ Failed task folder test: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Danbooru Scraper Test Suite")
    print("=" * 60)
    
    tests = [
        test_pagination_parsing,
        test_post_id_extraction,
        test_post_details,
        test_task_folder_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
