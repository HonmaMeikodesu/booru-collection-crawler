# Tsundora Scraper Quick Reference

## Command Examples

### Start New Task
```bash
python tsundora_scraper.py --mode new --keyword "本間芽衣子" --storage-path "./downloads"
```

### Resume Interrupted Task
```bash
python tsundora_scraper.py --mode resume --task-path "./downloads/keyword_folder"
```

### Sync Existing Task
```bash
python tsundora_scraper.py --mode sync --task-path "./downloads/keyword_folder"
```

## Key Implementation Details

### Search URL Format
- Page 1: `https://tsundora.com/?s={url_encoded_keyword}`
- Page N: `https://tsundora.com/page/{N}?s={url_encoded_keyword}`

### DOM Selectors

**Post List Page:**
- Post links: `.article_content .article-box a`
- Next page: `.next.page-numbers`

**Post Detail Page:**
- Image: `#main .entry-content img`
- Image src pattern: Removes `-WIDTHxHEIGHT` before extension

### Data Flow

1. **Build search URL** → URL encode keyword
2. **Fetch post list** → Extract post IDs from hrefs
3. **Follow pagination** → Until no `.next.page-numbers` found
4. **For each post:**
   - Request: `https://tsundora.com/{post_id}`
   - Extract: `#main .entry-content img[src]`
   - Transform: Remove size suffix via regex
   - Download: Full-resolution image
   - Save: `{post_id}.{ext}`

## Special Notes

- **No Tags**: Tsundora doesn't categorize posts with tags
- **Image URL Pattern**: `-960x1024.jpg` → `.jpg`
- **Pagination**: Different from other booru sites (uses WordPress pagination)
- **Post ID**: Extracted from URL path, not DOM attributes
