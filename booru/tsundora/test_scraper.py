#!/usr/bin/env python3
"""
Test script for Tsundora scraper
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tsundora_scraper import TsundoraScraper

def test_search_url_building():
    """Test search URL construction"""
    scraper = TsundoraScraper()
    
    # Test page 1
    url1 = scraper._build_search_url("本間芽衣子", 1)
    print(f"Page 1 URL: {url1}")
    assert "/?s=" in url1
    assert "%E6" in url1  # URL encoded Japanese
    
    # Test page 2
    url2 = scraper._build_search_url("本間芽衣子", 2)
    print(f"Page 2 URL: {url2}")
    assert "/page/2?s=" in url2
    
    print("✓ Search URL building test passed")

def test_post_id_extraction():
    """Test post ID extraction from HTML"""
    from bs4 import BeautifulSoup
    
    scraper = TsundoraScraper()
    
    # Sample HTML from postList.html
    html = '''
    <div class="article_content">
        <article class="article-box">
            <a href="https://tsundora.com/236664" class="clear article-item"></a>
        </article>
        <article class="article-box">
            <a href="https://tsundora.com/165101" class="clear article-item"></a>
        </article>
        <article class="article-box">
            <a href="https://tsundora.com/165099" class="clear article-item"></a>
        </article>
    </div>
    '''
    
    soup = BeautifulSoup(html, 'html.parser')
    post_ids = scraper._extract_post_ids_from_page(soup)
    
    print(f"Extracted post IDs: {post_ids}")
    assert post_ids == [236664, 165101, 165099]
    
    print("✓ Post ID extraction test passed")

def test_image_url_pattern():
    """Test image URL pattern removal"""
    import re
    
    test_cases = [
        (
            "https://tsundora.com/image/2015/04/ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai-132-960x1024.jpg",
            "https://tsundora.com/image/2015/04/ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai-132.jpg"
        ),
        (
            "https://tsundora.com/image/2016/08/kantoku-668-300x214.jpg",
            "https://tsundora.com/image/2016/08/kantoku-668.jpg"
        ),
        (
            "https://tsundora.com/image/test-150x107.png",
            "https://tsundora.com/image/test.png"
        )
    ]
    
    for src, expected in test_cases:
        result = re.sub(r'-\d+x\d+(\.[a-z]+)$', r'\1', src)
        print(f"Input:    {src}")
        print(f"Expected: {expected}")
        print(f"Result:   {result}")
        assert result == expected, f"Mismatch: {result} != {expected}"
        print()
    
    print("✓ Image URL pattern test passed")

if __name__ == '__main__':
    print("Running Tsundora scraper tests...\n")
    
    try:
        test_search_url_building()
        print()
        test_post_id_extraction()
        print()
        test_image_url_pattern()
        print()
        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
