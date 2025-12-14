#!/usr/bin/env python3
"""
Test suite for E-Shuushuu scraper
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from eshuushuu_scraper import EShuushuuScraper, TaskManager
from bs4 import BeautifulSoup


def test_extract_post_ids():
    """Test post ID extraction from HTML"""
    print("Testing post ID extraction...")
    
    # Load the sample HTML
    html_file = Path(__file__).parent / 'docs' / 'postList.html'
    if not html_file.exists():
        print(f"Warning: Sample HTML not found at {html_file}")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    scraper = EShuushuuScraper()
    
    post_ids = scraper._extract_post_ids_from_page(soup)
    
    print(f"Extracted {len(post_ids)} post IDs")
    print(f"First 5 IDs: {post_ids[:5]}")
    
    # Expected IDs from the sample HTML
    expected_ids = [1060480, 1055234, 1053029, 1045738, 1043329]
    
    if post_ids[:5] == expected_ids:
        print("✓ Post ID extraction test PASSED")
    else:
        print(f"✗ Post ID extraction test FAILED")
        print(f"Expected: {expected_ids}")
        print(f"Got: {post_ids[:5]}")


def test_pagination_detection():
    """Test pagination next link detection"""
    print("\nTesting pagination detection...")
    
    html_file = Path(__file__).parent / 'docs' / 'postList.html'
    if not html_file.exists():
        print(f"Warning: Sample HTML not found at {html_file}")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find next page link
    pagination = soup.select_one('.pagination')
    if pagination:
        next_link = pagination.select_one('.next a')
        if next_link and next_link.get('href'):
            next_url = next_link['href']
            print(f"Found next page link: {next_url}")
            
            # Verify the href contains both page and tags parameters
            if 'page=2' in next_url and 'tags=76604' in next_url:
                print("✓ Pagination detection test PASSED")
                
                # Test URL construction
                BASE_URL = "https://e-shuushuu.net"
                constructed_url = f"{BASE_URL}/search/results/{next_url}"
                expected_url = "https://e-shuushuu.net/search/results/?page=2&tags=76604"
                
                if constructed_url == expected_url:
                    print(f"✓ Constructed URL correct: {constructed_url}")
                else:
                    print(f"✗ URL construction failed")
                    print(f"  Expected: {expected_url}")
                    print(f"  Got: {constructed_url}")
            else:
                print("✗ Pagination detection test FAILED")
        else:
            print("✗ Next link not found")
    else:
        print("✗ Pagination section not found")


def test_task_folder_creation():
    """Test task folder name sanitization"""
    print("\nTesting task folder creation...")
    
    test_cases = [
        ("76604", "tag_76604"),
        ("12345", "tag_12345"),
        ("test-123", "tag_test-123"),
    ]
    
    all_passed = True
    for tag_id, expected in test_cases:
        result = TaskManager.sanitize_tag_id(tag_id)
        if result == expected:
            print(f"✓ Tag ID '{tag_id}' -> '{result}'")
        else:
            print(f"✗ Tag ID '{tag_id}' -> '{result}' (expected '{expected}')")
            all_passed = False
    
    if all_passed:
        print("✓ Task folder creation test PASSED")
    else:
        print("✗ Task folder creation test FAILED")


def test_url_construction():
    """Test search URL construction"""
    print("\nTesting URL construction...")
    
    scraper = EShuushuuScraper()
    
    # Test first page
    url1 = scraper._build_search_url("76604", page=1)
    expected1 = "https://e-shuushuu.net/search/results/?tags=76604"
    
    # Test second page
    url2 = scraper._build_search_url("76604", page=2)
    expected2 = "https://e-shuushuu.net/search/results/?page=2&tags=76604"
    
    if url1 == expected1 and url2 == expected2:
        print(f"✓ URL construction test PASSED")
        print(f"  Page 1: {url1}")
        print(f"  Page 2: {url2}")
    else:
        print(f"✗ URL construction test FAILED")
        print(f"  Expected page 1: {expected1}")
        print(f"  Got: {url1}")
        print(f"  Expected page 2: {expected2}")
        print(f"  Got: {url2}")


def main():
    """Run all tests"""
    print("E-Shuushuu Scraper Test Suite")
    print("=" * 50)
    
    test_extract_post_ids()
    test_pagination_detection()
    test_task_folder_creation()
    test_url_construction()
    
    print("\n" + "=" * 50)
    print("Test suite complete")


if __name__ == '__main__':
    main()
