# TBIB Scraper Quick Reference

## Command Cheat Sheet

### New Task
```bash
python tbib_scraper.py --mode new --tags "TAG1 TAG2" --storage-path PATH
```

### Resume Task
```bash
python tbib_scraper.py --mode resume --task-path TASK_FOLDER
```

### Sync Task
```bash
python tbib_scraper.py --mode sync --task-path TASK_FOLDER
```

### With Proxy
```bash
--proxy "socks5://localhost:1080" --proxy-auth "user:pass"
```

### Adjust Rate Limiting
```bash
--throttle 5.0 --max-retries 5
```

## Common Workflows

### Download Images by Character
```bash
python tbib_scraper.py --mode new \
  --tags "honma_meiko" \
  --storage-path "./downloads"
```

### Download with Multiple Tags
```bash
python tbib_scraper.py --mode new \
  --tags "honma_meiko ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai." \
  --storage-path "./downloads"
```

### Resume After Network Error
```bash
# The error message will show the exact command
python tbib_scraper.py --mode resume --task-path "./downloads/honma_meiko"
```

### Check for New Posts Daily
```bash
python tbib_scraper.py --mode sync --task-path "./downloads/honma_meiko"
```

### Behind Proxy/VPN
```bash
python tbib_scraper.py --mode new \
  --tags "test_tag" \
  --storage-path "./downloads" \
  --proxy "socks5://127.0.0.1:1080"
```

## Exit Codes Quick Reference

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | None needed |
| 1 | Invalid args | Check command syntax |
| 2 | Task validation failed | Verify task folder exists |
| 3 | Network error | Check connection, retry |
| 4 | Server refused (403/410) | Wait and retry later |
| 5 | Storage error | Check disk space/permissions |
| 6 | Proxy connection failed | Verify proxy settings |
| 7 | Proxy auth failed | Check credentials |

## Task Status Quick Check

### View Task Status
```bash
# Windows
type ".\downloads\honma_meiko\task_metadata.json"

# Linux/Mac
cat ./downloads/honma_meiko/task_metadata.json
```

### Count Downloaded Posts
```bash
# Windows PowerShell
(Get-ChildItem ".\downloads\honma_meiko\posts\*.png").Count

# Linux/Mac
ls ./downloads/honma_meiko/posts/*.* | wc -l
```

### Find Failed Posts
```bash
# Windows PowerShell
Get-Content ".\downloads\honma_meiko\post_list.json" | ConvertFrom-Json | Where-Object {$_.status -eq "FAIL"}

# Linux/Mac (requires jq)
cat ./downloads/honma_meiko/post_list.json | jq '.[] | select(.status=="FAIL")'
```

## Troubleshooting Quick Fixes

### "Storage path is not writable"
```bash
mkdir -p ./downloads
chmod +w ./downloads  # Linux/Mac only
```

### Server returning 403
```bash
# Increase throttle time
python tbib_scraper.py --mode resume \
  --task-path "./downloads/honma_meiko" \
  --throttle 5.0
```

### Proxy not working
```bash
# Test proxy first
curl -x socks5://localhost:1080 https://tbib.org

# Then run scraper
python tbib_scraper.py --mode new \
  --tags "test" \
  --storage-path "./downloads" \
  --proxy "socks5://localhost:1080"
```

### Task seems stuck
```bash
# Check metadata for current status
cat ./downloads/honma_meiko/task_metadata.json

# If status is FAILED, resume
python tbib_scraper.py --mode resume --task-path "./downloads/honma_meiko"
```

## File Locations

### Configuration
- No configuration file (all via command-line)

### Task Data
```
{storage-path}/{sanitized-tags}/
├── task_metadata.json      # Task status
├── post_list.json          # Post inventory
└── posts/                  # Downloaded files
    ├── {id}.{ext}          # Images
    └── {id}_tags.json      # Tag metadata
```

### Logs
- Stdout only (redirect to file if needed)

```bash
# Save logs to file
python tbib_scraper.py --mode new --tags "test" --storage-path "./downloads" > scraper.log 2>&1
```

## Performance Tuning

### Fast Download (Risky)
```bash
--throttle 1.0  # Minimum recommended
```

### Conservative (Safe)
```bash
--throttle 5.0  # Good for avoiding bans
```

### Slow Connection
```bash
--throttle 3.0 --max-retries 5
```

## Batch Operations

### Download Multiple Characters (Windows)
```powershell
@("honma_meiko", "anjou_naruko", "tsurumi_chiriko") | ForEach-Object {
    python tbib_scraper.py --mode new --tags $_ --storage-path "./downloads"
}
```

### Download Multiple Characters (Linux/Mac)
```bash
for tag in "honma_meiko" "anjou_naruko" "tsurumi_chiriko"; do
    python tbib_scraper.py --mode new --tags "$tag" --storage-path "./downloads"
done
```

### Sync All Tasks (Windows)
```powershell
Get-ChildItem ".\downloads" -Directory | ForEach-Object {
    python tbib_scraper.py --mode sync --task-path $_.FullName
}
```

### Sync All Tasks (Linux/Mac)
```bash
for dir in ./downloads/*/; do
    python tbib_scraper.py --mode sync --task-path "$dir"
done
```

## Tag Encoding Examples

| User Input | Encoded URL |
|------------|-------------|
| `honma_meiko` | `honma_meiko` |
| `honma meiko` | `honma+meiko` |
| `tag:special` | `tag%3Aspecial` |
| `tag with spaces` | `tag+with+spaces` |

**Note**: Spaces in tags are automatically converted to `+` for URL encoding.

## Typical Use Cases

### Daily Sync Routine
```bash
# Add to cron/Task Scheduler
python tbib_scraper.py --mode sync --task-path "./downloads/favorite_character"
```

### Archive Complete Series
```bash
python tbib_scraper.py --mode new \
  --tags "ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai." \
  --storage-path "./archive"
```

### Download Artist's Work
```bash
python tbib_scraper.py --mode new \
  --tags "mizuki_riyu" \
  --storage-path "./artists"
```

## Testing Commands

### Run All Tests
```bash
cd booru/tbib
python -m unittest test_scraper.py -v
```

### Run Specific Test
```bash
python -m unittest test_scraper.TestTbibScraper.test_build_search_url -v
```

### Test Coverage
```bash
# Install coverage tool first: pip install coverage
coverage run -m unittest test_scraper.py
coverage report
```

## Integration with Other Tools

### With jq (JSON processor)
```bash
# Count completed posts
cat task_metadata.json | jq '.completed_posts'

# List all failed posts
cat post_list.json | jq '.[] | select(.status=="FAIL") | .post_id'
```

### With cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add daily sync at 3 AM
0 3 * * * cd /path/to/booru-collection-crawler && python booru/tbib/tbib_scraper.py --mode sync --task-path "/path/to/downloads/honma_meiko" >> /var/log/tbib_sync.log 2>&1
```

### With Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 3 AM)
4. Action: Start a program
5. Program: `python`
6. Arguments: `tbib_scraper.py --mode sync --task-path "C:\downloads\honma_meiko"`
7. Start in: `C:\booru-collection-crawler\booru\tbib`

## Memory Aid

### TBIB vs Danbooru Differences

| Feature | Danbooru | TBIB |
|---------|----------|------|
| Pagination | Page count visible | Must traverse to find total |
| Post ID selector | `.post-preview-link` | `#post-list .content div span > a` |
| Image link | `.image-view-original-link` | `li a` with "Original image" text |
| URL format | `danbooru.donmai.us` | `tbib.org` |
| Tag categories | Same 5 categories | Same 5 categories |

## Quick Start for First-Time Users

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create download directory**
   ```bash
   mkdir downloads
   ```

3. **Run first download**
   ```bash
   python tbib_scraper.py --mode new --tags "1girl solo" --storage-path "./downloads"
   ```

4. **Check results**
   ```bash
   ls -R downloads/
   ```

5. **If interrupted, resume**
   ```bash
   python tbib_scraper.py --mode resume --task-path "./downloads/1girl_solo"
   ```

## Emergency Recovery

### Task Corrupted
1. Check `task_metadata.json` is valid JSON
2. Check `post_list.json` is valid JSON
3. If corrupted, restore from backup or delete and restart

### Disk Full During Download
1. Free up space
2. Resume task: `--mode resume --task-path ...`
3. Scraper will continue from last successful post

### Network Disconnected
1. Restore connection
2. Resume task: `--mode resume --task-path ...`
3. Failed posts will be retried

## Pro Tips

- 💡 Use `--throttle 2.5` to balance speed and safety
- 💡 Always use `--mode sync` to check for new content
- 💡 Save proxy settings in a shell script for reuse
- 💡 Monitor first few posts to ensure scraper works
- 💡 Use descriptive tags to organize downloads
- 💡 Check disk space before large downloads
- 💡 Resume mode auto-syncs after completion
