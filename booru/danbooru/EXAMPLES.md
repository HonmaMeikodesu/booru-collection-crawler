# Danbooru Scraper - Quick Start Examples

## Example 1: Download a Small Set (New Task)

Download posts with a specific character tag:

```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "honma_meiko" --storage-path "E:\danbooru_downloads"
```

Expected output:
```
[INFO] Danbooru Scraper v1.0
[INFO] Mode: new
[INFO] Tags: honma_meiko
[INFO] Storage: E:\danbooru_downloads
[INFO] Creating task folder: E:\danbooru_downloads\honma_meiko
[INFO] Fetching search results...
[INFO] Total pages found: 65
[INFO] Fetching page 1/65...
...
[INFO] Total posts found: 1282
[PROGRESS] Downloading post 1/1282 (ID: 10337509)
[SUCCESS] Image saved: 10337509.png (11.7 MB)
[SUCCESS] Tags saved: 10337509_tags.json
...
```

## Example 2: Using Proxy

For users in regions where Danbooru is blocked:

```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "landscape" --storage-path "E:\images" --proxy "socks5://127.0.0.1:1080"
```

With authentication:
```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "landscape" --storage-path "E:\images" --proxy "http://proxy.example.com:8080" --proxy-auth "username:password"
```

## Example 3: Resume Interrupted Download

If download was interrupted (network issue, computer restart, etc.):

```bash
python booru\danbooru\danbooru_scraper.py --mode resume --task-path "E:\danbooru_downloads\honma_meiko"
```

Expected output:
```
[INFO] Danbooru Scraper v1.0
[INFO] Mode: resume
[INFO] Task path: E:\danbooru_downloads\honma_meiko
[INFO] Tags: honma_meiko
[INFO] Resume info: 523 posts remaining
[PROGRESS] Downloading post 760/1282 (ID: 8957966)
...
[INFO] Download phase complete: 1282/1282 posts
[INFO] Triggering automatic sync operation...
[INFO] Sync complete: 15 new posts downloaded
[SUCCESS] Task complete. Total posts: 1297
```

## Example 4: Sync for New Posts

Check if new posts were added since you last downloaded:

```bash
python booru\danbooru\danbooru_scraper.py --mode sync --task-path "E:\danbooru_downloads\honma_meiko"
```

Expected output:
```
[INFO] Danbooru Scraper v1.0
[INFO] Mode: sync
[INFO] Task path: E:\danbooru_downloads\honma_meiko
[INFO] Tags: honma_meiko
[INFO] Fetching current post list from server...
[INFO] Total pages found: 66
...
[INFO] Found 23 new posts
[PROGRESS] Downloading post 1/23 (ID: 10500123)
...
[INFO] Sync complete: 23 new posts downloaded
[SUCCESS] Task complete. Total posts: 1305
```

## Example 5: Multiple Tags

Download posts matching multiple tags:

```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "honma_meiko dress" --storage-path "E:\images"
```

## Example 6: Custom Throttle

For slower connections or to be extra polite to the server:

```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "landscape" --storage-path "E:\images" --throttle 5.0
```

This sets a 5-second delay between requests.

## Example 7: High Retry Limit

For unstable network connections:

```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "landscape" --storage-path "E:\images" --max-retries 5
```

## Folder Structure After Download

After running Example 1, your folder structure will look like:

```
E:\danbooru_downloads\
└── honma_meiko\
    ├── task_metadata.json
    ├── post_list.json
    └── posts\
        ├── 10337509.png
        ├── 10337509_tags.json
        ├── 10243316.jpg
        ├── 10243316_tags.json
        ├── 10200019.jpg
        ├── 10200019_tags.json
        └── ... (1282 images + 1282 tag files)
```

## Checking Progress

You can check task progress at any time by viewing the `task_metadata.json` file:

```json
{
  "search_tags": "honma_meiko",
  "storage_path": "E:\\danbooru_downloads",
  "task_folder": "E:\\danbooru_downloads\\honma_meiko",
  "created_at": "2025-12-07T10:30:00.123456",
  "last_updated": "2025-12-07T11:45:23.789012",
  "last_synced": null,
  "status": "IN_PROGRESS",
  "total_posts": 1282,
  "completed_posts": 523,
  "mode_history": ["new"]
}
```

## Handling Errors

### Server Refusal (403/410)

If you see:
```
[ERROR] HTTP 403 - Server refused request
[FATAL] Halting process. Manual intervention required.
[INFO] Task state saved. Resume with: python danbooru_scraper.py --mode resume --task-path "..."
```

This might mean:
1. Too many requests in short time - wait a few hours before resuming
2. IP temporarily blocked - try using a proxy
3. Need to adjust throttle - use `--throttle 5.0` or higher

### Network Errors

The scraper automatically retries network errors. You'll see:
```
[WARNING] Request failed: ... Retrying in 5s... (Attempt 1/3)
```

If it exhausts retries, the post is marked as FAIL and the scraper continues.

## Tips

1. **Start small**: Test with a tag that has few posts first
2. **Use proxy if needed**: Some regions require proxy to access Danbooru
3. **Monitor first few downloads**: Make sure everything works before leaving it unattended
4. **Check disk space**: High-res images can be large (10-50 MB each)
5. **Resume is your friend**: Don't worry about interruptions, just resume later
6. **Sync regularly**: Run sync mode weekly to catch new posts
