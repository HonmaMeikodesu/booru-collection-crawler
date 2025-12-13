#!/usr/bin/env python3
"""
Test script for Zerochan scraper
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from zerochan_scraper import ZerochanScraper, TaskManager

def test_url_construction():
    """Test URL construction from keywords"""
    print("Testing URL construction...")
    scraper = ZerochanScraper(throttle=1.0)
    
    try:
        # Test various keyword formats
        test_cases = [
            ("Honma Meiko", "https://www.zerochan.net/Honma+Meiko"),
            ("Honma Meiko, Ano Hi Mita Hana no Namae o Bokutachi wa Mada Shiranai.", 
             "https://www.zerochan.net/Honma+Meiko,+Ano+Hi+Mita+Hana+no+Namae+o+Bokutachi+wa+Mada+Shiranai.")
        ]
        
        all_passed = True
        for keywords, expected in test_cases:
            result = scraper._build_search_url(keywords)
            if result == expected:
                print(f"✓ URL construction passed for: {keywords[:30]}...")
            else:
                print(f"✗ URL mismatch:")
                print(f"  Expected: {expected}")
                print(f"  Got: {result}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"✗ Failed URL construction: {e}")
        return False

def test_post_id_extraction():
    """Test extracting post IDs from search results"""
    print("\nTesting post ID extraction...")
    scraper = ZerochanScraper(throttle=2.0)
    
    try:
        # Test with a simple keyword
        post_ids = scraper.get_all_post_ids("Honma Meiko")
        if post_ids:
            print(f"✓ Successfully extracted {len(post_ids)} post IDs")
            print(f"  Sample post IDs: {post_ids[:5]}")
            return True
        else:
            print("✗ No post IDs found")
            return False
    except Exception as e:
        print(f"✗ Failed to extract post IDs: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_post_details():
    """Test fetching post details"""
    print("\nTesting post details extraction...")
    scraper = ZerochanScraper(throttle=2.0)
    
    try:
        # Get a post ID first
        post_ids = scraper.get_all_post_ids("Honma Meiko")
        if not post_ids:
            print("✗ No post IDs to test with")
            return False
        
        test_post_id = post_ids[0]
        image_url = scraper.get_post_details(test_post_id)
        
        if image_url:
            print(f"✓ Successfully fetched post details for ID {test_post_id}")
            print(f"  Image URL: {image_url}")
            return True
        else:
            print("✗ No image URL found")
            return False
    except Exception as e:
        print(f"✗ Failed to fetch post details: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_folder_creation():
    """Test task folder creation"""
    print("\nTesting task folder creation...")
    
    try:
        # Create temporary test folder
        test_storage = Path("test_storage")
        test_storage.mkdir(exist_ok=True)
        
        # Test sanitization
        test_cases = [
            ("Honma Meiko", "honma_meiko"),
            ("Honma Meiko, Test", "honma_meiko_test"),
            ("Test-Tag_123", "test-tag_123"),
            ("A" * 60, "a" * 50 + "_")  # Should truncate with hash
        ]
        
        all_passed = True
        for keywords, expected_prefix in test_cases:
            sanitized = TaskManager.sanitize_keywords(keywords)
            if expected_prefix.endswith("_"):
                # Check truncation case
                if sanitized.startswith(expected_prefix[:-1]) and len(sanitized) <= 57:
                    print(f"✓ Sanitization works for long keywords")
                else:
                    print(f"✗ Sanitization failed for: {keywords}")
                    all_passed = False
            else:
                if sanitized == expected_prefix:
                    print(f"✓ Sanitization works: '{keywords}' -> '{sanitized}'")
                else:
                    print(f"✗ Sanitization mismatch:")
                    print(f"  Expected: {expected_prefix}")
                    print(f"  Got: {sanitized}")
                    all_passed = False
        
        # Cleanup
        if test_storage.exists():
            import shutil
            shutil.rmtree(test_storage)
        
        return all_passed
    except Exception as e:
        print(f"✗ Failed task folder test: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Zerochan Scraper Test Suite")
    print("=" * 60)
    
    tests = [
        test_url_construction,
        test_task_folder_creation,
        test_post_id_extraction,
        test_post_details,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
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
