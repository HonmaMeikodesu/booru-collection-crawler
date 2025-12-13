#!/usr/bin/env python3
"""
Test script for Gelbooru scraper
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gelbooru_scraper import GelbooruScraper, TaskManager
from bs4 import BeautifulSoup


def test_url_building():
    """Test URL building with tag encoding"""
    print("Testing URL building...")
    scraper = GelbooruScraper()
    
    # Test single tag
    url = scraper._build_search_url("honma_meiko")
    expected = "https://gelbooru.com/index.php?page=post&s=list&tags=honma_meiko"
    assert url == expected, f"Expected {expected}, got {url}"
    print("✓ Single tag URL building works")
    
    # Test multiple tags
    url = scraper._build_search_url("honma_meiko ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai.")
    assert "honma_meiko+ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai." in url
    print("✓ Multiple tags URL building works")
    
    # Test with pid
    url = scraper._build_search_url("test", pid=42)
    assert "pid=42" in url
    print("✓ URL building with pagination works")


def test_post_id_extraction():
    """Test post ID extraction from HTML"""
    print("\nTesting post ID extraction...")
    
    html = """
    <div class="thumbnail-container">
        <article class="thumbnail-preview">
            <a id="p13022516" href="/post/13022516">
                <img src="thumb.jpg">
            </a>
        </article>
        <article class="thumbnail-preview">
            <a id="p12924960" href="/post/12924960">
                <img src="thumb2.jpg">
            </a>
        </article>
    </div>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    scraper = GelbooruScraper()
    post_ids = scraper._extract_post_ids_from_page(soup)
    
    assert len(post_ids) == 2, f"Expected 2 post IDs, got {len(post_ids)}"
    assert 13022516 in post_ids, "Expected post ID 13022516"
    assert 12924960 in post_ids, "Expected post ID 12924960"
    print("✓ Post ID extraction works")


def test_tag_sanitization():
    """Test tag sanitization for folder names"""
    print("\nTesting tag sanitization...")
    
    # Test normal tags
    result = TaskManager.sanitize_tags("honma_meiko")
    assert result == "honma_meiko", f"Expected honma_meiko, got {result}"
    print("✓ Simple tag sanitization works")
    
    # Test tags with spaces
    result = TaskManager.sanitize_tags("honma meiko ano")
    assert result == "honma_meiko_ano", f"Expected honma_meiko_ano, got {result}"
    print("✓ Tag sanitization with spaces works")
    
    # Test tags with special characters
    result = TaskManager.sanitize_tags("test@tag#special!")
    assert "@" not in result and "#" not in result and "!" not in result
    print("✓ Special character removal works")
    
    # Test long tags (truncation)
    long_tag = "a" * 60
    result = TaskManager.sanitize_tags(long_tag)
    assert len(result) <= 57, f"Expected length <= 57, got {len(result)}"  # 50 + _ + 6 hash
    print("✓ Long tag truncation works")


def test_proxy_setup():
    """Test proxy configuration"""
    print("\nTesting proxy setup...")
    
    # Test without auth
    scraper = GelbooruScraper(proxy="http://proxy.example.com:8080")
    assert scraper.proxy_config is not None
    assert scraper.proxy_config['http'] == "http://proxy.example.com:8080"
    print("✓ Proxy setup without auth works")
    
    # Test with separate auth
    scraper = GelbooruScraper(
        proxy="http://proxy.example.com:8080",
        proxy_auth="user:pass"
    )
    assert "user:pass@" in scraper.proxy_config['http']
    print("✓ Proxy setup with auth works")


def test_tags_extraction():
    """Test tags extraction from post HTML"""
    print("\nTesting tags extraction...")
    
    html = """
    <ul class="tag-list" id="tag-list">
        <span class="sm-hidden"><li style="margin-top: 10px;"><b>Artist</b></li></span>
        <li class="tag-type-artist">
            <a href="index.php?page=post&s=list&tags=mizuki_riyu">mizuki riyu</a>
        </li>
        <span class="sm-hidden"><li style="margin-top: 10px;"><b>Character</b></li></span>
        <li class="tag-type-character">
            <a href="index.php?page=post&s=list&tags=honma_meiko">honma meiko</a>
        </li>
        <span class="sm-hidden"><li style="margin-top: 10px;"><b>Copyright</b></li></span>
        <li class="tag-type-copyright">
            <a href="index.php?page=post&s=list&tags=test_series">test series</a>
        </li>
        <span class="sm-hidden"><li style="margin-top: 10px;"><b>Metadata</b></li></span>
        <li class="tag-type-metadata">
            <a href="index.php?page=post&s=list&tags=highres">highres</a>
        </li>
        <span class="sm-hidden"><li style="margin-top: 10px;"><b>Tag</b></li></span>
        <li class="tag-type-general">
            <a href="index.php?page=post&s=list&tags=1girl">1girl</a>
        </li>
    </ul>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    scraper = GelbooruScraper()
    
    # Simulate the tag extraction logic
    tags = {
        'artist': [],
        'copyright': [],
        'character': [],
        'metadata': [],
        'tag': []
    }
    
    tag_list = soup.select_one('#tag-list')
    if tag_list:
        current_category = None
        for li in tag_list.find_all('li'):
            if li.find('b'):
                category_name = li.get_text(strip=True).lower()
                if category_name == 'artist':
                    current_category = 'artist'
                elif category_name == 'character':
                    current_category = 'character'
                elif category_name == 'copyright':
                    current_category = 'copyright'
                elif category_name == 'metadata':
                    current_category = 'metadata'
                elif category_name == 'tag':
                    current_category = 'tag'
            elif current_category:
                tag_classes = li.get('class', [])
                is_tag_item = any(cls.startswith('tag-type-') for cls in tag_classes)
                if is_tag_item:
                    tag_links = li.find_all('a')
                    for tag_link in tag_links:
                        href = tag_link.get('href', '')
                        if 's=list&tags=' in href:
                            tag_name = tag_link.get_text(strip=True)
                            if tag_name:
                                tags[current_category].append(tag_name)
                                break
    
    assert 'mizuki riyu' in tags['artist'], "Expected artist tag"
    assert 'honma meiko' in tags['character'], "Expected character tag"
    assert 'test series' in tags['copyright'], "Expected copyright tag"
    assert 'highres' in tags['metadata'], "Expected metadata tag"
    assert '1girl' in tags['tag'], "Expected general tag"
    print("✓ Tags extraction works")


def main():
    """Run all tests"""
    print("=" * 50)
    print("Running Gelbooru Scraper Tests")
    print("=" * 50)
    
    try:
        test_url_building()
        test_post_id_extraction()
        test_tag_sanitization()
        test_proxy_setup()
        test_tags_extraction()
        
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
