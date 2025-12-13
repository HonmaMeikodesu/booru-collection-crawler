#!/usr/bin/env python3
"""
Test script for Rule34 scraper
Tests basic functionality without downloading full datasets
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rule34.rule34_scraper import Rule34Scraper, BASE_URL

def test_url_building():
    """Test URL construction with various tag combinations"""
    print("Testing URL construction...")
    scraper = Rule34Scraper()
    
    # Test single tag
    url = scraper._build_search_url("hatsune_miku", 1)
    print(f"Single tag (page 1): {url}")
    assert "hatsune_miku" in url
    assert "page=post" in url
    assert "s=list" in url
    
    # Test multiple tags
    url = scraper._build_search_url("hatsune_miku vocaloid", 1)
    print(f"Multiple tags (page 1): {url}")
    assert "hatsune_miku" in url
    assert "vocaloid" in url
    assert "+" in url
    
    # Test tags with special characters
    url = scraper._build_search_url("anohana:_the_flower_we_saw_that_day", 1)
    print(f"Special chars (page 1): {url}")
    assert "%3a" in url.lower() or "%3A" in url  # : should be encoded
    
    # Test page 2
    url = scraper._build_search_url("hatsune_miku", 2)
    print(f"Single tag (page 2): {url}")
    assert "pid=42" in url
    
    print("✓ URL construction tests passed\n")


def test_pagination():
    """Test pagination detection"""
    print("Testing pagination...")
    scraper = Rule34Scraper()
    
    # Test with a tag that has multiple pages
    try:
        total_pages = scraper.get_last_page_number("hatsune_miku")
        print(f"Total pages for 'hatsune_miku': {total_pages}")
        assert total_pages >= 1
        print("✓ Pagination test passed\n")
    except Exception as e:
        print(f"✗ Pagination test failed: {e}\n")
        raise


def test_post_id_extraction():
    """Test extracting post IDs from a page"""
    print("Testing post ID extraction...")
    scraper = Rule34Scraper()
    
    try:
        post_ids = scraper.get_post_ids_from_page("hatsune_miku", 1)
        print(f"Found {len(post_ids)} posts on page 1")
        print(f"Sample post IDs: {post_ids[:5]}")
        assert len(post_ids) > 0
        assert all(isinstance(pid, int) for pid in post_ids)
        print("✓ Post ID extraction test passed\n")
    except Exception as e:
        print(f"✗ Post ID extraction test failed: {e}\n")
        raise


def test_post_details():
    """Test getting post details"""
    print("Testing post details retrieval...")
    scraper = Rule34Scraper()
    
    try:
        # Get a post ID first
        post_ids = scraper.get_post_ids_from_page("hatsune_miku", 1)
        if not post_ids:
            print("No posts found to test")
            return
        
        test_post_id = post_ids[0]
        print(f"Testing with post ID: {test_post_id}")
        
        image_url, tags = scraper.get_post_details(test_post_id)
        
        print(f"Image URL: {image_url}")
        print(f"Tag categories found: {list(tags.keys())}")
        print(f"Sample tags:")
        for category, tag_list in tags.items():
            if tag_list:
                print(f"  {category}: {tag_list[:3]}")
        
        assert image_url is not None
        assert image_url.startswith('http')
        assert isinstance(tags, dict)
        assert all(key in tags for key in ['artist', 'copyright', 'character', 'general', 'meta'])
        
        print("✓ Post details test passed\n")
    except Exception as e:
        print(f"✗ Post details test failed: {e}\n")
        raise


def main():
    """Run all tests"""
    print("=" * 60)
    print("Rule34 Scraper Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_url_building()
        test_pagination()
        test_post_id_extraction()
        test_post_details()
        
        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print("=" * 60)
        print(f"Test suite failed: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
