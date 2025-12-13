# Gelbooru Scraper - Quick Reference

## Common Commands

### New Task
```bash
# Single tag
python gelbooru_scraper.py --mode new --tags "honma_meiko" --storage-path "./downloads"

# Multiple tags
python gelbooru_scraper.py --mode new --tags "tag1 tag2 tag3" --storage-path "./downloads"
```

### Resume Task
```bash
python gelbooru_scraper.py --mode resume --task-path "./downloads/tag_folder"
```

### Sync Task
```bash
python gelbooru_scraper.py --mode sync --task-path "./downloads/tag_folder"
```

### With Proxy
```bash
python gelbooru_scraper.py --mode new --tags "tag" --storage-path "./downloads" \
  --proxy "http://proxy:8080" --proxy-auth "user:pass"
```

## URL Pattern

**Search:** `https://gelbooru.com/index.php?page=post&s=list&tags={encoded_tags}&pid={offset}`
**Post:** `https://gelbooru.com/index.php?page=post&s=view&id={post_id}`

## DOM Selectors

| Element | Selector |
|---------|----------|
| Post container | `.thumbnail-container` |
| Post links | `article > a[id^="p"]` |
| Next page | `#paginator a[alt="next"]` |
| Original image | `li a` with text "Original image" |
| Tag list | `#tag-list` |
| Tag categories | `li > b` (Artist, Character, Copyright, Metadata, Tag) |
| Tag items | `li.tag-type-*` |

## Tag Categories

- **artist** - Content creators
- **copyright** - Series/franchise
- **character** - Character names
- **metadata** - Technical tags (resolution, etc.)
- **tag** - General tags

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Task validation failed |
| 3 | Network error |
| 4 | Server refused (403/410) |
| 5 | Storage error |
| 6 | Proxy connection failed |
| 7 | Proxy auth failed |

## Task Status Values

- `PENDING` - Not yet downloaded
- `IN_PROGRESS` - Task is running
- `COMPLETE` - Successfully downloaded
- `FAILED` - Task failed
- `FAIL` - Individual post failed

## File Structure

```
storage_path/
└── sanitized_tags/
    ├── task_metadata.json      # Task info
    ├── post_list.json          # Post tracking
    └── posts/
        ├── {id}.{ext}          # Image file
        └── {id}_tags.json      # Tag metadata
```

## Pagination Logic

1. Start at page 1 (no `pid` parameter)
2. Extract posts from current page
3. Find `#paginator a[alt="next"]`
4. If found, follow link to next page
5. Repeat until no "next" link exists

## Configuration Defaults

| Setting | Default |
|---------|---------|
| Throttle | 2.5 seconds |
| Max retries | 3 |
| Retry delay | 5 seconds (exponential backoff) |
| Backoff multiplier | 2 |
