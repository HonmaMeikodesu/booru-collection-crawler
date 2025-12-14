# Yande Scraper - Quick Reference

Quick reference guide for common operations.

## Command Patterns

### New Task
```bash
python yande_scraper.py --mode new --tags "TAG" --storage-path "PATH"
```

### Resume Task
```bash
python yande_scraper.py --mode resume --task-path "TASK_PATH"
```

### Sync Task
```bash
python yande_scraper.py --mode sync --task-path "TASK_PATH"
```

## Common Options

| Option | Default | Description |
|--------|---------|-------------|
| `--throttle 3.0` | 2.5 | Delay between requests (seconds) |
| `--max-retries 5` | 3 | Max retry attempts |
| `--proxy "socks5://HOST:PORT"` | None | SOCKS5 proxy |
| `--proxy "http://HOST:PORT"` | None | HTTP proxy |
| `--proxy-auth "USER:PASS"` | None | Proxy credentials |

## Tag Syntax

### Single Tag
```bash
--tags "honma_meiko"
```

### Multiple Tags (AND)
```bash
--tags "honma_meiko dress"
```

### Tags with Underscores
```bash
--tags "ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai"
```

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | None |
| 1 | Invalid args | Fix command |
| 2 | Task invalid | Check folder |
| 3 | Network error | Check connection |
| 4 | Server refused | Wait/use proxy |
| 5 | Storage error | Check path |
| 6 | Proxy failed | Check proxy |
| 7 | Proxy auth failed | Check credentials |

## File Structure

```
task_folder/
├── task_metadata.json    # Task info
├── post_list.json        # Post list
└── posts/
    ├── {ID}.{ext}        # Image
    └── {ID}_tags.json    # Tags
```

## Common Workflows

### 1. Basic Download
```bash
python yande_scraper.py --mode new \
  --tags "character_name" \
  --storage-path "E:\downloads"
```

### 2. Resume After Error
```bash
# Check error message for task path
python yande_scraper.py --mode resume \
  --task-path "E:\downloads\character_name"
```

### 3. Daily Sync
```bash
python yande_scraper.py --mode sync \
  --task-path "E:\downloads\my_collection"
```

### 4. Download via Proxy
```bash
python yande_scraper.py --mode new \
  --tags "tag" \
  --storage-path "E:\downloads" \
  --proxy "socks5://127.0.0.1:1080"
```

### 5. Slow Connection
```bash
python yande_scraper.py --mode new \
  --tags "tag" \
  --storage-path "E:\downloads" \
  --throttle 5.0 \
  --max-retries 5
```

## Error Recovery

### Server Refused (403/410)
```bash
# Wait 30-60 minutes, then:
python yande_scraper.py --mode resume \
  --task-path "TASK_PATH" \
  --proxy "socks5://127.0.0.1:1080"
```

### Network Timeout
```bash
# Increase retries and throttle:
python yande_scraper.py --mode resume \
  --task-path "TASK_PATH" \
  --max-retries 5 \
  --throttle 5.0
```

### Proxy Connection Failed
```bash
# Test proxy first
curl --proxy socks5://127.0.0.1:1080 https://yande.re

# Then retry with working proxy
python yande_scraper.py --mode resume \
  --task-path "TASK_PATH" \
  --proxy "socks5://127.0.0.1:1080"
```

## Testing

### Run Tests
```bash
cd booru/yande
python test_scraper.py
```

### Check Installation
```bash
python yande_scraper.py --help
```

## Monitoring Progress

### Check Task Status
```bash
# View task_metadata.json
cat "TASK_PATH\task_metadata.json"
```

### Count Downloaded Posts
```bash
# Windows PowerShell
(Get-ChildItem "TASK_PATH\posts" -Filter "*.jpg").Count
```

### Check Failed Posts
```bash
# Search for "FAIL" status in post_list.json
python -c "import json; posts = json.load(open('TASK_PATH/post_list.json')); print(len([p for p in posts if p['status'] == 'FAIL']))"
```

## Tips

1. **Start Small**: Test with specific tags first
2. **Monitor First Run**: Watch first 5-10 downloads
3. **Use Appropriate Throttle**: Higher for popular tags
4. **Regular Syncs**: Run weekly/monthly to stay updated
5. **Backup Metadata**: Keep copies of JSON files
6. **Check Disk Space**: Large collections need space
7. **Rotate Proxies**: Have backup proxies ready
8. **Log Output**: Redirect to file for debugging

## Logging Output to File

### Windows CMD
```bash
python yande_scraper.py --mode new --tags "tag" --storage-path "E:\downloads" > log.txt 2>&1
```

### Windows PowerShell
```powershell
python yande_scraper.py --mode new --tags "tag" --storage-path "E:\downloads" | Tee-Object -FilePath log.txt
```

## Scheduling Tasks

### Windows Task Scheduler

1. Create a batch file `sync.bat`:
```batch
@echo off
cd E:\booru-collection-crawler\booru\yande
python yande_scraper.py --mode sync --task-path "E:\downloads\collection"
```

2. Schedule in Task Scheduler:
   - Action: Start a program
   - Program: `E:\path\to\sync.bat`
   - Trigger: Daily at preferred time

## Troubleshooting Quick Checks

| Issue | Check | Fix |
|-------|-------|-----|
| Can't find command | PATH | Use full python path |
| Import errors | Dependencies | `pip install -r requirements.txt` |
| Permission denied | Storage path | Check write permissions |
| Proxy not working | Connection | Test with curl/browser |
| Slow downloads | Network | Increase --throttle |
| Many 404 errors | Posts deleted | Normal, scraper continues |
| JSON parse error | Corrupt file | Delete and re-run |

## Performance Tuning

### Fast Network
```bash
--throttle 1.5 --max-retries 2
```

### Slow Network
```bash
--throttle 5.0 --max-retries 5
```

### Unreliable Network
```bash
--throttle 3.0 --max-retries 10
```

### Behind Strict Firewall
```bash
--throttle 10.0 --proxy "socks5://127.0.0.1:1080"
```

## Quick Validation

### Validate Downloaded Images
```python
# Check if images are valid
from PIL import Image
import os

posts_dir = "TASK_PATH/posts"
for file in os.listdir(posts_dir):
    if file.endswith(('.jpg', '.png')):
        try:
            img = Image.open(os.path.join(posts_dir, file))
            img.verify()
        except:
            print(f"Corrupt: {file}")
```

### Count Total File Size
```bash
# Windows PowerShell
Get-ChildItem "TASK_PATH\posts" -Recurse | Measure-Object -Property Length -Sum
```

## Best Practices

1. ✓ Always use absolute paths
2. ✓ Start with --throttle 2.5 or higher
3. ✓ Keep task_metadata.json and post_list.json safe
4. ✓ Test proxy connection before large downloads
5. ✓ Monitor first page of results
6. ✓ Use resume mode after interruptions
7. ✓ Run sync regularly to stay updated
8. ✗ Don't use --throttle < 1.0 (risk ban)
9. ✗ Don't delete post_list.json (lose progress)
10. ✗ Don't modify JSON files manually
