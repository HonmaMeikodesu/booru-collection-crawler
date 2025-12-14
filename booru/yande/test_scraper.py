#!/usr/bin/env python3
"""
Test suite for Yande scraper
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from yande_scraper import YandeScraper, TaskManager
from bs4 import BeautifulSoup


def test_pagination_parsing():
    """Test extraction of pagination from HTML"""
    print("Testing pagination parsing...")
    
    # Read the sample postList.html
    html_file = Path(__file__).parent / "docs" / "postList.html"
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find next page link
    next_link = soup.select_one('a.next_page')
    if next_link and next_link.get('href'):
        next_url = next_link['href']
        print(f"✓ Next page link found: {next_url}")
        
        # Verify it contains expected query parameters
        if 'page=2' in next_url and 'tags=honma_meiko' in next_url:
            print("✓ Next page URL contains correct parameters")
        else:
            print("✗ Next page URL missing expected parameters")
            return False
    else:
        print("✗ Next page link not found")
        return False
    
    return True


def test_post_id_extraction():
    """Test extraction of post IDs from search results page"""
    print("\nTesting post ID extraction...")
    
    # Read the sample postList.html
    html_file = Path(__file__).parent / "docs" / "postList.html"
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Create scraper instance (without network calls)
    scraper = YandeScraper()
    post_ids = scraper._extract_post_ids_from_page(soup)
    
    if post_ids:
        print(f"✓ Successfully extracted {len(post_ids)} post IDs")
        print(f"  Sample post IDs: {post_ids[:5]}")
        
        # Verify expected post ID is in the list
        if 1239787 in post_ids:
            print("✓ Expected post ID 1239787 found in results")
        else:
            print("✗ Expected post ID 1239787 not found")
            return False
    else:
        print("✗ No post IDs extracted")
        return False
    
    return True


def test_post_details_extraction():
    """Test extraction of image URL and tags from post page"""
    print("\nTesting post details extraction...")
    
    # Read the sample post.html
    html_file = Path(__file__).parent / "docs" / "post.html"
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract image URL
    image_url = None
    all_links = soup.select('li a')
    for link in all_links:
        if "Download larger version" in link.get_text():
            image_url = link.get('href')
            break
    
    if image_url:
        print(f"✓ Successfully extracted image URL")
        print(f"  URL: {image_url[:80]}...")
    else:
        print("✗ Image URL not found")
        return False
    
    # Extract tags
    tags = {
        'artist': [],
        'copyright': [],
        'character': [],
        'general': []
    }
    
    tag_sidebar = soup.select_one('#tag-sidebar')
    if tag_sidebar:
        for tag_type in ['artist', 'copyright', 'character', 'general']:
            tag_items = tag_sidebar.select(f'li.tag-type-{tag_type} a[href*="/post?tags="]')
            for tag_link in tag_items:
                tag_name = tag_link.get_text(strip=True)
                if tag_name:
                    tags[tag_type].append(tag_name)
    
    print(f"✓ Successfully extracted tags")
    print(f"  Tags found:")
    for tag_type, tag_list in tags.items():
        if tag_list:
            print(f"    {tag_type}: {len(tag_list)} tags")
    
    # Verify expected tags
    if 'tanaka masayoshi' in tags['artist']:
        print("✓ Expected artist tag found")
    else:
        print("✗ Expected artist tag not found")
        return False
    
    if 'honma meiko' in tags['character']:
        print("✓ Expected character tag found")
    else:
        print("✗ Expected character tag not found")
        return False
    
    return True


def test_task_folder_creation():
    """Test tag sanitization for folder names"""
    print("\nTesting task folder creation...")
    
    # Test tag sanitization
    test_tags = "honma_meiko test-tag"
    sanitized = TaskManager.sanitize_tags(test_tags)
    
    expected = "honma_meiko_test-tag"
    if sanitized == expected:
        print(f"✓ Tag sanitization works: '{test_tags}' -> '{sanitized}'")
    else:
        print(f"✗ Tag sanitization failed: expected '{expected}', got '{sanitized}'")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Yande Scraper Test Suite")
    print("=" * 60)
    
    tests = [
        test_pagination_parsing,
        test_post_id_extraction,
        test_post_details_extraction,
        test_task_folder_creation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{len(tests)} passed")
    print("=" * 60)
    
    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
