# Gelbooru Scraper - Usage Examples

## Basic Examples

### Example 1: Download Single Character Tag

Download all posts tagged with a specific character:

```bash
python gelbooru_scraper.py --mode new --tags "honma_meiko" --storage-path "./downloads"
```

**Output:**
```
[INFO] Gelbooru Scraper v1.0
[INFO] Mode: new
[INFO] Tags: honma_meiko
[INFO] Storage: ./downloads
[INFO] Creating task folder: ./downloads/honma_meiko
[INFO] Fetching page 1...
[INFO] Found 42 posts on page 1
[INFO] Fetching page 2...
[INFO] Found 42 posts on page 2
...
[INFO] Total pages traversed: 32
[INFO] Total posts found: 1350
[INFO] Downloading post 1/1350 (ID: 13022516)
[INFO] Image saved: 13022516.png (1.2 MB)
[INFO] Tags saved: 13022516_tags.json
...
[INFO] Task complete. Total posts: 1350
```

**Folder Structure:**
```
downloads/
└── honma_meiko/
    ├── task_metadata.json
    ├── post_list.json
    └── posts/
        ├── 13022516.png
        ├── 13022516_tags.json
        ├── 12924960.jpg
        ├── 12924960_tags.json
        └── ...
```

### Example 2: Download Multiple Tags

Search with multiple tags (intersection):

```bash
python gelbooru_scraper.py --mode new \
  --tags "honma_meiko ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai." \
  --storage-path "./downloads"
```

This creates a folder `honma_meiko_ano_hi_mita_hana_no_namae_wo_bokutachi_w_3a5f2d` (truncated with hash).

### Example 3: Resume Interrupted Download

If download is interrupted by network error or server refusal:

```bash
python gelbooru_scraper.py --mode resume --task-path "./downloads/honma_meiko"
```

**Output:**
```
[INFO] Gelbooru Scraper v1.0
[INFO] Mode: resume
[INFO] Task path: ./downloads/honma_meiko
[INFO] Tags: honma_meiko
[INFO] Resume info: 523 posts remaining
[INFO] Downloading post 828/1350 (ID: 11692338)
[INFO] Image saved: 11692338.jpg (0.8 MB)
[INFO] Tags saved: 11692338_tags.json
...
[INFO] Download phase complete: 1350/1350 posts
[INFO] Triggering automatic sync operation...
[INFO] Fetching current post list from server...
[INFO] Sync complete: No new posts found
[INFO] Task complete. Total posts: 1350
```

### Example 4: Sync Completed Task

Check for new posts and download them:

```bash
python gelbooru_scraper.py --mode sync --task-path "./downloads/honma_meiko"
```

**Output:**
```
[INFO] Gelbooru Scraper v1.0
[INFO] Mode: sync
[INFO] Task path: ./downloads/honma_meiko
[INFO] Tags: honma_meiko
[INFO] Fetching current post list from server...
[INFO] Fetching page 1...
[INFO] Found 42 posts on page 1
...
[INFO] Found 5 new posts
[INFO] Downloading post 1/5 (ID: 13100234)
[INFO] Image saved: 13100234.png (1.5 MB)
[INFO] Tags saved: 13100234_tags.json
...
[INFO] Sync complete: 5 new posts downloaded
[INFO] Task complete. Total posts: 1355
```

## Advanced Examples

### Example 5: Using Proxy

Download through HTTP proxy:

```bash
python gelbooru_scraper.py --mode new \
  --tags "tag1 tag2" \
  --storage-path "./downloads" \
  --proxy "http://proxy.example.com:8080"
```

With authentication:

```bash
python gelbooru_scraper.py --mode new \
  --tags "tag1 tag2" \
  --storage-path "./downloads" \
  --proxy "http://proxy.example.com:8080" \
  --proxy-auth "username:password"
```

**Output:**
```
[INFO] Gelbooru Scraper v1.0
[INFO] Mode: new
[INFO] Tags: tag1 tag2
[INFO] Storage: ./downloads
[INFO] Proxy: http://proxy.example.com:8080 (authenticated)
[INFO] Testing proxy connection...
[INFO] Proxy connection successful
[INFO] Creating task folder: ./downloads/tag1_tag2
...
```

### Example 6: Custom Throttling

Slow down requests to 5 seconds between each:

```bash
python gelbooru_scraper.py --mode new \
  --tags "popular_tag" \
  --storage-path "./downloads" \
  --throttle 5.0
```

Speed up for trusted proxy:

```bash
python gelbooru_scraper.py --mode new \
  --tags "tag" \
  --storage-path "./downloads" \
  --throttle 1.0 \
  --proxy "socks5://localhost:1080"
```

### Example 7: Increase Retry Attempts

For unstable networks:

```bash
python gelbooru_scraper.py --mode new \
  --tags "tag" \
  --storage-path "./downloads" \
  --max-retries 10
```

## Error Handling Examples

### Example 8: Server Refusal (403/410)

```bash
python gelbooru_scraper.py --mode new --tags "tag" --storage-path "./downloads"
```

**Output:**
```
[INFO] Gelbooru Scraper v1.0
[INFO] Mode: new
...
[INFO] Downloading post 523/1000 (ID: 12345678)
[ERROR] HTTP 403 - Server refused request
[ERROR] URL: https://gelbooru.com/index.php?page=post&s=view&id=12345678
[ERROR] Headers: {...}
[ERROR] Server refused request: Server returned 403
[ERROR] Task state saved. Resume with:
[ERROR]   python gelbooru_scraper.py --mode resume --task-path "./downloads/tag"
```

**Solution:** Wait a few minutes, then resume.

### Example 9: Network Timeout with Retry

```bash
python gelbooru_scraper.py --mode new --tags "tag" --storage-path "./downloads"
```

**Output:**
```
[INFO] Downloading post 100/500 (ID: 11111111)
[WARNING] Request failed: Connection timeout. Retrying in 5s... (Attempt 1/3)
[WARNING] Request failed: Connection timeout. Retrying in 10s... (Attempt 2/3)
[INFO] Image saved: 11111111.jpg (2.1 MB)
```

### Example 10: Missing Original Image

```bash
python gelbooru_scraper.py --mode new --tags "tag" --storage-path "./downloads"
```

**Output:**
```
[INFO] Downloading post 42/100 (ID: 98765432)
[ERROR] Post 98765432: Original image link not found for post 98765432
[INFO] Downloading post 43/100 (ID: 98765433)
...
```

Post 98765432 is marked as FAIL in post_list.json.

## Tag Metadata Examples

### Example 11: Examining Downloaded Tags

After downloading post 13022516, check its tags:

```bash
cat ./downloads/honma_meiko/posts/13022516_tags.json
```

**Output:**
```json
{
  "post_id": 13022516,
  "artist": [
    "mizuki riyu"
  ],
  "copyright": [
    "ano hi mita hana no namae wo bokutachi wa mada shiranai."
  ],
  "character": [
    "honma meiko"
  ],
  "metadata": [
    "absurdres",
    "commentary request",
    "highres",
    "painting (medium)",
    "traditional media",
    "watercolor (medium)"
  ],
  "tag": [
    "1girl",
    "blue eyes",
    "blush",
    "dress",
    "flat chest",
    "long hair",
    "looking at viewer",
    "open mouth",
    "outstretched arms",
    "smile",
    "solo",
    "spread arms",
    "white dress",
    "white hair"
  ]
}
```

### Example 12: Checking Task Metadata

View task progress:

```bash
cat ./downloads/honma_meiko/task_metadata.json
```

**Output:**
```json
{
  "search_tags": "honma_meiko",
  "storage_path": "./downloads",
  "task_folder": "./downloads/honma_meiko",
  "created_at": "2025-12-12T23:30:00.123456",
  "last_updated": "2025-12-12T23:45:30.789012",
  "last_synced": "2025-12-13T10:15:22.345678",
  "status": "COMPLETE",
  "total_posts": 1350,
  "completed_posts": 1350,
  "mode_history": [
    "new",
    "sync"
  ]
}
```

### Example 13: Checking Post List

View download status of all posts:

```bash
head -n 20 ./downloads/honma_meiko/post_list.json
```

**Output:**
```json
[
  {
    "post_id": 13022516,
    "status": "COMPLETE",
    "image_url": "https://img2.gelbooru.com/images/67/7d/677d8bf54414fd96d9dac833d2e04585.png",
    "file_extension": "png",
    "download_timestamp": "2025-12-12T23:31:15.123456"
  },
  {
    "post_id": 12924960,
    "status": "COMPLETE",
    "image_url": "https://img2.gelbooru.com/images/ec/9d/ec9d0870d6c15645ea310d4cfba527cc.jpg",
    "file_extension": "jpg",
    "download_timestamp": "2025-12-12T23:31:18.234567"
  },
  {
    "post_id": 12880290,
    "status": "FAIL",
    "image_url": null,
    "file_extension": null,
    "download_timestamp": null
  }
]
```

## Workflow Examples

### Example 14: Complete Workflow

**Day 1: Initial Download**
```bash
# Download all posts for tag "honma_meiko"
python gelbooru_scraper.py --mode new --tags "honma_meiko" --storage-path "./downloads"
# Result: 1350 posts downloaded
```

**Day 5: Check for Updates**
```bash
# Sync to get new posts
python gelbooru_scraper.py --mode sync --task-path "./downloads/honma_meiko"
# Result: 5 new posts downloaded (total: 1355)
```

**Day 10: Another Sync**
```bash
python gelbooru_scraper.py --mode sync --task-path "./downloads/honma_meiko"
# Result: 12 new posts downloaded (total: 1367)
```

### Example 15: Recovery from Interruption

**Step 1: Start Download (interrupted at 40%)**
```bash
python gelbooru_scraper.py --mode new --tags "popular_series" --storage-path "./downloads"
# ^C (Ctrl+C pressed, or network failure)
# Progress: 400/1000 posts downloaded
```

**Step 2: Resume Later**
```bash
python gelbooru_scraper.py --mode resume --task-path "./downloads/popular_series"
# Continues from post 401
# Result: All 1000 posts completed
```

### Example 16: Batch Processing Multiple Tags

Create a shell script `download_all.sh`:

```bash
#!/bin/bash

tags=(
  "character1"
  "character2 series1"
  "character3"
)

for tag in "${tags[@]}"; do
  echo "Processing: $tag"
  python gelbooru_scraper.py --mode new --tags "$tag" --storage-path "./batch_downloads"
  sleep 60  # Wait 1 minute between tasks
done
```

Run:
```bash
bash download_all.sh
```

## Performance Examples

### Example 17: Large Dataset Download

Downloading 5000+ posts:

```bash
python gelbooru_scraper.py --mode new \
  --tags "1girl" \
  --storage-path "./downloads" \
  --throttle 3.0
```

**Performance Notes:**
- Estimated time: ~4 hours (3s per post)
- Disk space: ~10-15GB (assuming 2MB average per image)
- Network bandwidth: ~7MB/min average

### Example 18: Small Dataset Quick Download

For small tag sets (<100 posts):

```bash
python gelbooru_scraper.py --mode new \
  --tags "rare_character rare_series" \
  --storage-path "./downloads" \
  --throttle 1.5
```

**Performance Notes:**
- Estimated time: ~5 minutes for 50 posts
- More aggressive throttling acceptable for small datasets

## Troubleshooting Examples

### Example 19: Verify Installation

Test without actually downloading:

```bash
python test_scraper.py
```

**Expected Output:**
```
==================================================
Running Gelbooru Scraper Tests
==================================================
Testing URL building...
✓ Single tag URL building works
✓ Multiple tags URL building works
✓ URL building with pagination works

Testing post ID extraction...
✓ Post ID extraction works

Testing tag sanitization...
✓ Simple tag sanitization works
✓ Tag sanitization with spaces works
✓ Special character removal works
✓ Long tag truncation works

Testing proxy setup...
✓ Proxy setup without auth works
✓ Proxy setup with auth works

Testing tags extraction...
✓ Tags extraction works

==================================================
All tests passed! ✓
==================================================
```

### Example 20: Debug Mode

For development/debugging, modify logging level:

Edit `gelbooru_scraper.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
```

Then run:
```bash
python gelbooru_scraper.py --mode new --tags "test" --storage-path "./debug"
```

This provides detailed request/response information.
