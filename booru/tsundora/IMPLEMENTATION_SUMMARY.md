# Tsundora Scraper Implementation Summary

## Overview

The Tsundora scraper is adapted from the Safebooru scraper to work with [tsundora.com](https://tsundora.com), a Japanese anime wallpaper site. The core workflow remains the same (fetch post list → download each post), but with key adaptations for Tsundora's specific structure.

## Key Adaptations

### 1. Search Method
- **From**: Tag-based search (`&tags=tag1+tag2`)
- **To**: Keyword search (`?s={keyword}`)
- Keywords are URL-encoded to support Japanese characters

### 2. URL Structure
- **Base URL**: `https://tsundora.com`
- **Search Page 1**: `/?s={keyword}`
- **Search Page N**: `/page/{N}?s={keyword}`
- **Post Page**: `/{post_id}`

### 3. DOM Selectors

#### Post List Page
```python
# Post links
post_links = soup.select('.article_content .article-box a')

# Next page button
next_link = soup.select_one('.next.page-numbers')
```

#### Post Detail Page
```python
# Image element
img_tag = soup.select_one('#main .entry-content img')
```

### 4. Post ID Extraction
- **From**: `id="p{post_id}"` attribute
- **To**: Extract from href URL path
```python
# Example: https://tsundora.com/165099 → 165099
post_id = int(href.rstrip('/').split('/')[-1])
```

### 5. Image URL Processing
Tsundora serves thumbnail images with size suffixes that need to be removed:

```python
# Input:  https://tsundora.com/image/2015/04/file-960x1024.jpg
# Output: https://tsundora.com/image/2015/04/file.jpg

image_url = re.sub(r'-\d+x\d+(\.[a-z]+)$', r'\1', src)
```

### 6. Tags Handling
- **Change**: Tsundora doesn't provide tag categorization
- **Implementation**: Return empty dict, skip tag saving

## Class Structure

### TsundoraScraper
Main scraper class with methods:

- `_build_search_url(keyword, page)` - Build search URL
- `get_all_post_ids(keyword)` - Fetch all post IDs via pagination
- `_extract_post_ids_from_page(soup)` - Extract IDs from page HTML
- `get_post_details(post_id)` - Get image URL (no tags)
- `download_image(url)` - Download image to memory

### TaskManager
Unchanged from original, manages:
- Task folder creation
- Metadata persistence
- Post list tracking
- Image/tags storage

## Workflow

### Mode: new
1. Validate arguments (`--keyword`, `--storage-path`)
2. Create scraper instance with rate limiting
3. Create task folder named from sanitized keyword
4. Initialize metadata with `search_keyword` field
5. Fetch all post IDs by paginating search results
6. Download each post (image only, no tags)
7. Mark task as complete

### Mode: resume
1. Load task metadata and post list
2. Find incomplete posts
3. Resume downloading from breakpoints
4. Auto-trigger sync after completion

### Mode: sync
1. Load existing task
2. Fetch current post list from server
3. Compare with local list
4. Download only new posts
5. Update metadata

## Testing

Unit tests cover:
- Search URL construction
- Post ID extraction from HTML
- Image URL pattern removal (size suffix)

All tests pass successfully.

## Files

- `tsundora_scraper.py` - Main scraper implementation
- `index.py` - Entry point wrapper
- `test_scraper.py` - Unit tests
- `README.md` - User documentation
- `QUICK_REFERENCE.md` - Quick command reference
- `docs/` - HTML samples and specification

## Compatibility

- Python 3.7+
- Dependencies: requests, beautifulsoup4, PySocks (for SOCKS proxy)
- Works on Windows/Linux/macOS
