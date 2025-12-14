# E-Shuushuu Scraper Quick Reference

## Basic Commands

### New Task
```bash
python eshuushuu_scraper.py --mode new --tag-id <TAG_ID> --storage-path <PATH>
```

### Resume Task
```bash
python eshuushuu_scraper.py --mode resume --task-path <TASK_PATH>
```

### Sync Task
```bash
python eshuushuu_scraper.py --mode sync --task-path <TASK_PATH>
```

## Common Options

| Option | Default | Description |
|--------|---------|-------------|
| `--throttle` | 2.5 | Seconds between requests |
| `--max-retries` | 3 | Maximum retry attempts |
| `--proxy` | None | Proxy server URL |
| `--proxy-auth` | None | Proxy credentials (user:pass) |

## Examples

### Download Honma Meiko images (tag 76604)
```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
```

### Resume interrupted download
```bash
python eshuushuu_scraper.py --mode resume --task-path ./downloads/tag_76604
```

### Sync to get new posts
```bash
python eshuushuu_scraper.py --mode sync --task-path ./downloads/tag_76604
```

### With slower throttle (safer)
```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --throttle 5.0
```

### With SOCKS5 proxy
```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --proxy socks5://127.0.0.1:1080
```

### With authenticated HTTP proxy
```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --proxy http://proxy.com:8080 --proxy-auth user:pass
```

## Finding Tag IDs

1. Go to https://e-shuushuu.net
2. Search for your character/theme
3. Check the URL: `https://e-shuushuu.net/search/results/?tags=76604`
4. The number after `tags=` is the tag ID

## Output Structure

```
tag_76604/
├── task_metadata.json     # Task info
├── post_list.json         # All posts status
└── posts/
    ├── 1060480.jpeg       # Image
    ├── 1060480_tags.json  # Tags
    └── ...
```

## Status Codes

| Post Status | Meaning |
|-------------|---------|
| PENDING | Not yet downloaded |
| COMPLETE | Successfully downloaded |
| FAIL | Download failed |

| Task Status | Meaning |
|-------------|---------|
| IN_PROGRESS | Currently running |
| COMPLETE | All posts downloaded |
| FAILED | Error occurred, can resume |

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | None |
| 1 | Invalid args | Check command syntax |
| 2 | Task corrupted | Verify task files |
| 3 | Network error | Check connection |
| 4 | Server refused | Wait and resume |
| 5 | Storage error | Check path permissions |
| 6 | Proxy failed | Verify proxy settings |
| 7 | Proxy auth failed | Check credentials |

## Quick Troubleshooting

### "Server refused request"
- Wait 5-10 minutes
- Increase throttle: `--throttle 5.0`
- Resume with `--mode resume`

### "Module not found"
- Run from correct directory
- Check Python path

### "Storage path not writable"
- Check directory permissions
- Create directory first

### "Proxy connection failed"
- Test proxy separately
- Install PySocks: `pip install PySocks`

## Testing

Run tests to verify installation:
```bash
python test_scraper.py
```

Expected output: ✓ All tests PASSED

## Log Interpretation

```
[INFO] Fetching page 1...           # Pagination progress
[INFO] Found 15 posts on page 1     # Posts per page
[INFO] Downloading post 1/15        # Download progress
[INFO] Image saved: 1060480.jpeg    # Success
[WARNING] Request failed: timeout    # Retry happening
[ERROR] Server refused request       # Manual action needed
```

## Performance Tips

1. **Adjust throttle for your network:**
   - Fast/local: `--throttle 1.0`
   - Safe default: `--throttle 2.5`
   - Conservative: `--throttle 5.0`

2. **Use resume mode liberally:**
   - Save progress automatically
   - Safe to interrupt anytime
   - Resume from last success

3. **Monitor server responses:**
   - Watch for 403/410 errors
   - Increase throttle if needed
   - Use proxy if blocked

## Tag Metadata Categories

| Category | Description | Example |
|----------|-------------|---------|
| tag | General descriptive tags | "dress", "long hair" |
| source | Anime/media source | "Anohana" |
| character | Character names | "Honma Meiko" |
| artist | Artist names | "Ixy" |

## Best Practices

1. **Start with small tag IDs** to test
2. **Use reasonable throttle** (2.5-5.0 seconds)
3. **Monitor first few downloads** for errors
4. **Resume if interrupted** - state is saved
5. **Sync periodically** for new content
6. **Respect rate limits** - avoid bans

## Common Workflows

### First-time download
```bash
# 1. Create new task
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads

# Task runs to completion or interruption
```

### After interruption
```bash
# 2. Resume from last success
python eshuushuu_scraper.py --mode resume --task-path ./downloads/tag_76604
```

### Update existing collection
```bash
# 3. Sync for new posts
python eshuushuu_scraper.py --mode sync --task-path ./downloads/tag_76604

# Recommended: Run sync weekly/monthly
```

## File Extensions

Automatically detected from image URL:
- `.jpeg` / `.jpg` - JPEG images
- `.png` - PNG images
- `.gif` - GIF images

## Rate Limiting

Default throttle prevents:
- IP bans
- Rate limit errors
- Server overload
- Anti-crawler triggers

Formula: **Wait {throttle} seconds between each request**

## Memory Usage

- Downloads one image at a time
- No concurrent operations
- Low memory footprint
- Suitable for large collections

## State Persistence

Progress saved after each post:
- Can interrupt anytime (Ctrl+C)
- Resume exactly where left off
- No duplicate downloads
- Safe for long-running tasks

## Requirements

Minimum:
- Python 3.6+
- requests library
- beautifulsoup4

Optional:
- PySocks (for SOCKS proxy)

Install: `pip install requests beautifulsoup4`

## Support

For issues or questions:
1. Check README.md for detailed documentation
2. Run test_scraper.py to validate setup
3. Check IMPLEMENTATION_SUMMARY.md for technical details
