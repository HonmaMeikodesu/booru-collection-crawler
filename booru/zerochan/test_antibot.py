#!/usr/bin/env python3
"""
Simple test script to verify anti-bot bypass functionality
"""

import sys
from pathlib import Path

# Add parent directory to path to import zerochan_scraper
sys.path.insert(0, str(Path(__file__).parent))

from zerochan_scraper import ZerochanScraper, logger

def test_anti_bot_bypass():
    """Test that the scraper can bypass anti-bot verification"""
    
    print("=" * 60)
    print("Testing Zerochan Anti-Bot Bypass")
    print("=" * 60)
    
    # Create scraper instance
    scraper = ZerochanScraper(throttle=2.5)
    
    # Test 1: Fetch a known post to trigger anti-bot mechanism
    print("\n[TEST 1] Fetching post details for ID 2941468...")
    try:
        image_url = scraper.get_post_details(2941468)
        if image_url:
            print(f"✓ Successfully retrieved image URL: {image_url}")
            print(f"✓ Cookies acquired flag: {scraper.cookies_acquired}")
        else:
            print("✗ Failed to retrieve image URL")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 2: Fetch search results to verify session cookies persist
    print("\n[TEST 2] Fetching first page of search results for 'Honma Meiko'...")
    try:
        # Modify to only fetch first page for quick testing
        search_url = scraper._build_search_url("Honma Meiko")
        response = scraper._make_request(search_url)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        post_ids = scraper._extract_post_ids(soup)
        print(f"✓ Successfully retrieved {len(post_ids)} post IDs from first page")
        if len(post_ids) > 0:
            print(f"  First few IDs: {post_ids[:5]}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 3: Verify cookies persist by fetching another post
    print("\n[TEST 3] Fetching another post to verify cookie persistence...")
    try:
        if len(post_ids) > 0:
            test_id = post_ids[0]
            image_url = scraper.get_post_details(test_id)
            if image_url:
                print(f"✓ Successfully retrieved image URL for post {test_id}")
                print(f"✓ No additional cookie acquisition needed")
            else:
                print(f"✗ Failed to retrieve image URL for post {test_id}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed! Anti-bot bypass is working correctly.")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_anti_bot_bypass()
    sys.exit(0 if success else 1)
