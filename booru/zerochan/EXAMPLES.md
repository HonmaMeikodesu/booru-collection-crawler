# Zerochan Scraper - Usage Examples

## Table of Contents

1. [Basic Downloads](#basic-downloads)
2. [Working with Proxies](#working-with-proxies)
3. [Task Management](#task-management)
4. [Advanced Scenarios](#advanced-scenarios)

## Basic Downloads

### Simple Keyword Search

Download all images for "Honma Meiko":

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./downloads
```

Output:
```
[INFO] Zerochan Scraper v1.0
[INFO] Mode: new
[INFO] Keywords: Honma Meiko
[INFO] Storage: ./downloads
[INFO] Creating task folder: ./downloads/honma_meiko
[INFO] Fetching search results...
[INFO] Fetching page 1...
[INFO] Found 20 posts on page 1
[INFO] Fetching page 2...
[INFO] Found 18 posts on page 2
[INFO] Total pages found: 2
[INFO] Total posts found: 38
[INFO] Downloading post 1/38 (ID: 2941468)
[INFO] Image saved: 2941468.jpg (2.3 MB)
...
[INFO] Task complete. Total posts: 38
```

### Complex Keywords with Multiple Terms

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko, Ano Hi Mita Hana no Namae o Bokutachi wa Mada Shiranai." \
  --storage-path ./anime_collection
```

The scraper will:
- Sanitize keywords to `honma_meiko_ano_hi_mita_hana_no_namae_o_bokutachi_wa_m_abc123`
- Create task folder with sanitized name
- Download all matching posts

## Working with Proxies

### HTTP Proxy

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./downloads \
  --proxy http://proxy.example.com:8080
```

### SOCKS5 Proxy

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./downloads \
  --proxy socks5://127.0.0.1:1080
```

### Authenticated Proxy

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./downloads \
  --proxy http://proxy.example.com:8080 \
  --proxy-auth myusername:mypassword
```

Output with proxy:
```
[INFO] Zerochan Scraper v1.0
[INFO] Proxy: http://proxy.example.com:8080 (authenticated)
[INFO] Testing proxy connection...
[INFO] Proxy connection successful
...
```

## Task Management

### Resume After Network Interruption

If download stops due to network error:

```bash
python zerochan_scraper.py --mode resume \
  --task-path ./downloads/honma_meiko
```

Output:
```
[INFO] Zerochan Scraper v1.0
[INFO] Mode: resume
[INFO] Task path: ./downloads/honma_meiko
[INFO] Keywords: Honma Meiko
[INFO] Resume info: 15 posts remaining
[INFO] Downloading post 24/38 (ID: 2941491)
...
[INFO] Download phase complete: 38/38 posts
[INFO] Triggering automatic sync operation...
[INFO] Fetching current post list from server...
[INFO] Found 2 new posts
[INFO] Sync complete: 2 new posts downloaded
[INFO] Task complete. Total posts: 40
```

### Sync to Get New Posts

Update an existing collection with newly published posts:

```bash
python zerochan_scraper.py --mode sync \
  --task-path ./downloads/honma_meiko
```

Output when new posts exist:
```
[INFO] Zerochan Scraper v1.0
[INFO] Mode: sync
[INFO] Keywords: Honma Meiko
[INFO] Fetching current post list from server...
[INFO] Fetching page 1...
[INFO] Total pages found: 3
[INFO] Found 5 new posts
[INFO] Downloading post 1/5 (ID: 2941500)
...
[INFO] Sync complete: 5 new posts downloaded
```

Output when no new posts:
```
[INFO] Zerochan Scraper v1.0
[INFO] Mode: sync
[INFO] Keywords: Honma Meiko
[INFO] Fetching current post list from server...
[INFO] Sync complete: No new posts found
```

## Advanced Scenarios

### Slow Down Requests to Avoid Rate Limiting

If you encounter server refusal errors, increase throttle:

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./downloads \
  --throttle 5.0
```

This waits 5 seconds between each request (default is 2.5 seconds).

### Increase Retry Attempts

For unreliable network connections:

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./downloads \
  --max-retries 5
```

### Recovering from Server Refusal

If you see this error:
```
[ERROR] HTTP 403 - Server refused request
[ERROR] URL: https://www.zerochan.net/Honma+Meiko
[ERROR] Task state saved. Resume with:
[ERROR]   python zerochan_scraper.py --mode resume --task-path "./downloads/honma_meiko"
```

Wait a few hours, then resume with higher throttle:
```bash
python zerochan_scraper.py --mode resume \
  --task-path ./downloads/honma_meiko \
  --throttle 10.0
```

### Download Multiple Collections

Create separate tasks for different keywords:

```bash
# Collection 1
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./anime_collection

# Collection 2
python zerochan_scraper.py --mode new \
  --keywords "Menma" \
  --storage-path ./anime_collection

# Collection 3
python zerochan_scraper.py --mode new \
  --keywords "AnoHana" \
  --storage-path ./anime_collection
```

Resulting structure:
```
anime_collection/
├── honma_meiko/
│   ├── task_metadata.json
│   ├── post_list.json
│   └── posts/
├── menma/
│   ├── task_metadata.json
│   ├── post_list.json
│   └── posts/
└── anohana/
    ├── task_metadata.json
    ├── post_list.json
    └── posts/
```

### Batch Sync Multiple Tasks

Sync all tasks in a directory using a shell script:

**sync_all.sh** (Linux/Mac):
```bash
#!/bin/bash
for task_dir in ./downloads/*/; do
    echo "Syncing $task_dir..."
    python zerochan_scraper.py --mode sync --task-path "$task_dir"
done
```

**sync_all.ps1** (Windows PowerShell):
```powershell
Get-ChildItem -Path ./downloads -Directory | ForEach-Object {
    Write-Host "Syncing $($_.FullName)..."
    python zerochan_scraper.py --mode sync --task-path $_.FullName
}
```

## Error Examples

### Invalid Arguments

```bash
python zerochan_scraper.py --mode new --keywords "Honma Meiko"
# Missing --storage-path
```

Output:
```
[ERROR] --keywords and --storage-path are required for new mode
```
Exit code: 1

### Storage Path Not Writable

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path /root/downloads
# Non-writable directory
```

Output:
```
[ERROR] Storage path is not writable: /root/downloads
```
Exit code: 5

### Proxy Authentication Failed

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./downloads \
  --proxy http://proxy.example.com:8080 \
  --proxy-auth wrong:credentials
```

Output:
```
[INFO] Proxy: http://proxy.example.com:8080 (authenticated)
[INFO] Testing proxy connection...
[ERROR] Proxy authentication failed
```
Exit code: 7

## Monitoring Progress

### Check Task Metadata

```bash
# Linux/Mac
cat ./downloads/honma_meiko/task_metadata.json | python -m json.tool

# Windows PowerShell
Get-Content ./downloads/honma_meiko/task_metadata.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Count Downloaded Images

```bash
# Linux/Mac
ls -1 ./downloads/honma_meiko/posts/*.jpg | wc -l

# Windows PowerShell
(Get-ChildItem -Path ./downloads/honma_meiko/posts -Filter *.jpg).Count
```

### View Failed Posts

```bash
# Extract failed post IDs using jq
cat ./downloads/honma_meiko/post_list.json | jq '.[] | select(.status == "FAIL") | .post_id'
```
