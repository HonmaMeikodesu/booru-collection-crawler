# E-Shuushuu Scraper - Usage Examples

## Example 1: Basic Download

**Scenario:** Download all images tagged with "Honma Meiko" (tag ID: 76604)

```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
```

**Expected Output:**
```
[INFO] E-Shuushuu Scraper v1.0
[INFO] Mode: new
[INFO] Tag ID: 76604
[INFO] Storage: ./downloads
[INFO] Creating task folder: ./downloads/tag_76604
[INFO] Fetching page 1...
[INFO] Found 15 posts on page 1
[INFO] Fetching page 2...
[INFO] Found 15 posts on page 2
[INFO] Total pages traversed: 2
[INFO] Total posts found: 30
[INFO] Downloading post 1/30 (ID: 1060480)
[INFO] Image saved: 1060480.jpeg (0.5 MB)
[INFO] Tags saved: 1060480_tags.json
[INFO] Downloading post 2/30 (ID: 1055234)
...
[INFO] Task complete. Total posts: 30
```

**Result:**
```
downloads/
└── tag_76604/
    ├── task_metadata.json
    ├── post_list.json
    └── posts/
        ├── 1060480.jpeg
        ├── 1060480_tags.json
        ├── 1055234.jpeg
        ├── 1055234_tags.json
        └── ... (28 more)
```

## Example 2: Resume After Interruption

**Scenario:** Previous download was interrupted at post 15/30

```bash
python eshuushuu_scraper.py --mode resume --task-path ./downloads/tag_76604
```

**Expected Output:**
```
[INFO] E-Shuushuu Scraper v1.0
[INFO] Mode: resume
[INFO] Task path: ./downloads/tag_76604
[INFO] Tag ID: 76604
[INFO] Resume info: 15 posts remaining
[INFO] Downloading post 16/30 (ID: 982236)
[INFO] Image saved: 982236.jpeg (2.0 MB)
[INFO] Tags saved: 982236_tags.json
...
[INFO] Download phase complete: 30/30 posts
[INFO] Triggering automatic sync operation...
[INFO] Fetching current post list from server...
[INFO] Sync complete: No new posts found
[INFO] Task complete. Total posts: 30
```

## Example 3: Sync for New Content

**Scenario:** Task was completed 1 week ago, check for new posts

```bash
python eshuushuu_scraper.py --mode sync --task-path ./downloads/tag_76604
```

**Expected Output (new posts found):**
```
[INFO] E-Shuushuu Scraper v1.0
[INFO] Mode: sync
[INFO] Task path: ./downloads/tag_76604
[INFO] Tag ID: 76604
[INFO] Fetching current post list from server...
[INFO] Fetching page 1...
[INFO] Found 15 posts on page 1
[INFO] Total pages traversed: 1
[INFO] Total posts found: 32
[INFO] Found 2 new posts
[INFO] Downloading post 1/2 (ID: 1070123)
[INFO] Image saved: 1070123.jpeg (1.2 MB)
[INFO] Tags saved: 1070123_tags.json
[INFO] Downloading post 2/2 (ID: 1070456)
[INFO] Image saved: 1070456.jpeg (0.8 MB)
[INFO] Tags saved: 1070456_tags.json
[INFO] Sync complete: 2 new posts downloaded
[INFO] Task complete. Total posts: 32
```

**Expected Output (no new posts):**
```
[INFO] E-Shuushuu Scraper v1.0
[INFO] Mode: sync
[INFO] Task path: ./downloads/tag_76604
[INFO] Tag ID: 76604
[INFO] Fetching current post list from server...
[INFO] Fetching page 1...
[INFO] Found 15 posts on page 1
[INFO] Total pages traversed: 1
[INFO] Total posts found: 30
[INFO] Sync complete: No new posts found
[INFO] Task complete. Total posts: 30
```

## Example 4: Using a Proxy

**Scenario:** Download through a SOCKS5 proxy

```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --proxy socks5://127.0.0.1:1080
```

**Expected Output:**
```
[INFO] E-Shuushuu Scraper v1.0
[INFO] Mode: new
[INFO] Tag ID: 76604
[INFO] Storage: ./downloads
[INFO] Proxy: socks5://127.0.0.1:1080
[INFO] Testing proxy connection...
[INFO] Proxy connection successful
[INFO] Creating task folder: ./downloads/tag_76604
...
```

## Example 5: Authenticated Proxy

**Scenario:** Download through proxy requiring authentication

```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --proxy http://proxy.company.com:8080 --proxy-auth myuser:mypass
```

**Expected Output:**
```
[INFO] E-Shuushuu Scraper v1.0
[INFO] Mode: new
[INFO] Tag ID: 76604
[INFO] Storage: ./downloads
[INFO] Proxy: http://proxy.company.com:8080 (authenticated)
[INFO] Testing proxy connection...
[INFO] Proxy connection successful
...
```

## Example 6: Custom Throttle Rate

**Scenario:** Use slower throttle to be extra cautious (5 seconds between requests)

```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --throttle 5.0
```

**Expected Output:**
```
[INFO] E-Shuushuu Scraper v1.0
[INFO] Mode: new
[INFO] Tag ID: 76604
[INFO] Storage: ./downloads
[INFO] Creating task folder: ./downloads/tag_76604
[INFO] Fetching page 1...
# (5 second delay)
[INFO] Found 15 posts on page 1
[INFO] Fetching page 2...
# (5 second delay)
...
```

**Note:** Each request now waits 5 seconds instead of the default 2.5 seconds.

## Example 7: Increased Retry Attempts

**Scenario:** Unstable network connection, increase retries to 5

```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --max-retries 5
```

**Expected Output (with network issues):**
```
[INFO] E-Shuushuu Scraper v1.0
[INFO] Mode: new
[INFO] Tag ID: 76604
[INFO] Storage: ./downloads
...
[INFO] Downloading post 5/30 (ID: 1043329)
[WARNING] Request failed: Connection timeout. Retrying in 5s... (Attempt 1/5)
# (5 second delay)
[WARNING] Request failed: Connection timeout. Retrying in 10s... (Attempt 2/5)
# (10 second delay)
[INFO] Image saved: 1043329.jpeg (0.6 MB)
...
```

## Example 8: Server Refused Error

**Scenario:** Server returns 403 Forbidden

```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
```

**Expected Output:**
```
[INFO] E-Shuushuu Scraper v1.0
[INFO] Mode: new
[INFO] Tag ID: 76604
[INFO] Storage: ./downloads
...
[INFO] Downloading post 10/30 (ID: 972750)
[ERROR] HTTP 403 - Server refused request
[ERROR] URL: https://e-shuushuu.net/image/972750/
[ERROR] Headers: {'Server': 'nginx', 'Date': '...', ...}
[ERROR] Server refused request: Server returned 403
[ERROR] Task state saved. Resume with:
[ERROR]   python eshuushuu_scraper.py --mode resume --task-path "./downloads/tag_76604"
```

**Exit Code:** 4 (EXIT_SERVER_REFUSED)

**Action:** Wait 10-15 minutes, then resume:
```bash
python eshuushuu_scraper.py --mode resume --task-path ./downloads/tag_76604
```

## Example 9: Invalid Arguments

**Scenario:** Forgot to specify storage path in new mode

```bash
python eshuushuu_scraper.py --mode new --tag-id 76604
```

**Expected Output:**
```
[ERROR] --tag-id and --storage-path are required for new mode
```

**Exit Code:** 1 (EXIT_INVALID_ARGS)

**Fix:**
```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
```

## Example 10: Examining Task Metadata

**Scenario:** Check task progress without running scraper

```bash
# View task metadata
cat ./downloads/tag_76604/task_metadata.json
```

**Output:**
```json
{
  "search_tag_id": "76604",
  "storage_path": "./downloads",
  "task_folder": "./downloads/tag_76604",
  "created_at": "2023-12-15T10:00:00.000000",
  "last_updated": "2023-12-15T10:30:45.123456",
  "last_synced": "2023-12-15T10:35:00.000000",
  "status": "COMPLETE",
  "total_posts": 30,
  "completed_posts": 30,
  "mode_history": ["new", "sync"]
}
```

**Interpretation:**
- Task completed successfully (status: COMPLETE)
- All 30 posts downloaded (completed_posts: 30)
- Synced once after initial download (mode_history)
- Last sync: 2023-12-15T10:35:00

## Example 11: Examining Post Tags

**Scenario:** View tags for a specific post

```bash
# View tags for post 1060480
cat ./downloads/tag_76604/posts/1060480_tags.json
```

**Output:**
```json
{
  "post_id": 1060480,
  "tag": [
    "dress",
    "green eyes",
    "grey hair",
    "long hair",
    "ribbon"
  ],
  "source": [
    "Anohana: The Flower We Saw That Day"
  ],
  "character": [
    "Honma Meiko"
  ],
  "artist": [
    "Ixy"
  ]
}
```

## Example 12: Duplicate Task Creation

**Scenario:** Create another task for the same tag ID

```bash
# First task
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
# Creates: ./downloads/tag_76604

# Second task (same tag ID)
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
# Creates: ./downloads/tag_76604_20231215_143022
```

**Result:**
```
downloads/
├── tag_76604/              # First task
│   └── ...
└── tag_76604_20231215_143022/  # Second task with timestamp
    └── ...
```

## Example 13: Multiple Characters

**Scenario:** Download images for different characters

```bash
# Character 1: Honma Meiko
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads

# Character 2: Furukawa Nagisa
python eshuushuu_scraper.py --mode new --tag-id 72290 --storage-path ./downloads

# Character 3: Honda Tohru
python eshuushuu_scraper.py --mode new --tag-id 76553 --storage-path ./downloads
```

**Result:**
```
downloads/
├── tag_76604/    # Honma Meiko
├── tag_72290/    # Furukawa Nagisa
└── tag_76553/    # Honda Tohru
```

## Example 14: Checking File Sizes

**Scenario:** Find large images

```bash
# On Unix/Linux/Mac
cd ./downloads/tag_76604/posts
ls -lh *.jpeg | sort -k5 -hr | head -10

# On Windows PowerShell
cd .\downloads\tag_76604\posts
Get-ChildItem *.jpeg | Sort-Object Length -Descending | Select-Object -First 10 Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
```

## Example 15: Counting Posts by Status

**Scenario:** Check how many posts succeeded/failed

```bash
# Using Python
python -c "
import json
with open('./downloads/tag_76604/post_list.json', 'r') as f:
    posts = json.load(f)
complete = sum(1 for p in posts if p['status'] == 'COMPLETE')
fail = sum(1 for p in posts if p['status'] == 'FAIL')
pending = sum(1 for p in posts if p['status'] == 'PENDING')
print(f'Complete: {complete}, Failed: {fail}, Pending: {pending}')
"
```

**Output:**
```
Complete: 28, Failed: 2, Pending: 0
```

## Example 16: Handling Network Interruptions

**Scenario:** Internet connection drops during download

**Initial Command:**
```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
```

**Output (interrupted):**
```
[INFO] Downloading post 15/30 (ID: 972556)
[WARNING] Request failed: Network unreachable. Retrying in 5s... (Attempt 1/3)
[WARNING] Request failed: Network unreachable. Retrying in 10s... (Attempt 2/3)
[WARNING] Request failed: Network unreachable. Retrying in 20s... (Attempt 3/3)
[ERROR] Request failed after 3 retries: Network unreachable
[ERROR] Unexpected error: Network unreachable
```

**Action:** Fix network, then resume:
```bash
python eshuushuu_scraper.py --mode resume --task-path ./downloads/tag_76604
```

**Output (resumed):**
```
[INFO] E-Shuushuu Scraper v1.0
[INFO] Mode: resume
[INFO] Resume info: 16 posts remaining
[INFO] Downloading post 15/30 (ID: 972556)
[INFO] Image saved: 972556.jpeg (1.3 MB)
...
```

## Pro Tips

1. **Always use absolute paths** for storage-path to avoid confusion
2. **Run sync weekly** to keep collections up-to-date
3. **Monitor first 5-10 downloads** to catch issues early
4. **Use resume liberally** - it's safe and efficient
5. **Check task_metadata.json** to verify completion status
6. **Backup task folders** before experimenting
7. **Test with small tag IDs** first to verify setup

## Troubleshooting Examples

### Problem: "Storage path does not exist"
```bash
# Wrong
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./nonexistent

# Fix: Create directory first
mkdir ./downloads
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
```

### Problem: "Task metadata not found"
```bash
# Wrong path
python eshuushuu_scraper.py --mode resume --task-path ./tag_76604

# Fix: Use full path
python eshuushuu_scraper.py --mode resume --task-path ./downloads/tag_76604
```

### Problem: Module import errors
```bash
# Wrong: Running from wrong directory
cd /some/other/directory
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads

# Fix: Run from e-shuushuu directory
cd e:\booru-collection-crawler\booru\e-shuushuu
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
```
