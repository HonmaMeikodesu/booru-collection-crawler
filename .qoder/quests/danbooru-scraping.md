# Danbooru Web Scraper Design

## Purpose

Develop a web scraper for Danbooru to download high-resolution images and associated metadata based on user-specified tags. The system must support initial execution, resumption from breakpoints, and synchronization of completed tasks with updated remote data.

## System Overview

The scraper orchestrates a multi-phase workflow: accepting user search criteria, discovering all matching posts through pagination traversal, and systematically downloading each post's image and tag metadata while maintaining progress state for fault tolerance.

## Core Requirements

### Functional Requirements

| Requirement | Description |
|-------------|-------------|
| Tag-based Search | Accept single or multiple tags from user input to construct search queries |
| Pagination Discovery | Automatically detect total page count from search results |
| Post Identification | Extract unique post identifiers from search result pages |
| Image Download | Download highest resolution image available for each post |
| Metadata Extraction | Capture all tags categorized by type (Artist, Copyright, Character, General, Meta) |
| Task Persistence | Maintain task state and download progress in task-specific directories |
| Resumption Support | Continue from breakpoint after interruption or failure |
| Task Synchronization | Update completed tasks with new posts from remote server |

### Non-Functional Requirements

| Aspect | Constraint |
|--------|------------|
| Rate Limiting | Implement throttling between requests to avoid firewall triggering |
| Reliability | Automatic retry mechanism for transient network failures |
| Data Integrity | Complete image download in memory before disk persistence |
| Error Handling | Graceful degradation for intentional server refusals |

## Workflow Architecture

### Execution Modes

The system operates in three distinct modes based on task state:

```mermaid
flowchart TD
    Start([User Initiates Task]) --> CheckTask{Task Exists?}
    CheckTask -->|No| FirstRun[First Execution Mode]
    CheckTask -->|Yes| CheckComplete{Task Complete?}
    CheckComplete -->|No| Resume[Resume Mode]
    CheckComplete -->|Yes| Sync[Sync Mode]
    
    FirstRun --> CreateFolder[Create Task Folder]
    CreateFolder --> BuildList[Build Post List]
    BuildList --> Download[Download Posts]
    
    Resume --> FindBreakpoint[Find Incomplete Posts]
    FindBreakpoint --> Download
    Download --> AutoSync[Auto-trigger Sync]
    AutoSync --> RefreshList[Refresh Post List]
    
    Sync --> RefreshList
    RefreshList --> DiffCheck[Compare with Local]
    DiffCheck --> DownloadNew[Download New Posts Only]
    
    DownloadNew --> End([Task Complete])
```

### First Execution Mode

When starting from scratch:

1. User provides search tags via command-line argument
2. User provides local storage path via command-line argument for task directory
3. System validates storage path exists and is writable
4. System constructs task folder name from sanitized tag string
5. Task folder created under user-specified storage path
6. Search results page is fetched to determine pagination
7. Post identifier list is built by traversing all pages
8. Each post identifier receives initial status field (PENDING)
9. Post list persisted to task folder as structured data
10. Sequential download process begins from first post
11. Each successful download marks status as COMPLETE
12. Each failed download marks status as FAIL and halts at breakpoint

### Resume Mode

When continuing an incomplete task:

1. User specifies existing task folder path via command-line argument
2. System validates task folder exists and contains valid task metadata
3. System loads persisted post list
4. All posts with non-COMPLETE status identified as breakpoints
5. Download process resumes from first breakpoint
6. Status updates continue as in first execution mode
7. Upon completion of all pending/failed posts, system automatically transitions to Sync Mode
8. Sync operation checks for new posts added to remote server since task creation
9. Any new posts discovered are downloaded using same process

### Sync Mode

When updating a completed task or automatically triggered after resume completion:

1. User specifies existing completed task folder via command-line argument (manual trigger) OR system auto-triggers after resume mode completes all pending posts
2. Fresh post list retrieved from remote server
3. Comparison performed between remote and local post lists
4. New posts identified (present in remote, absent in local)
5. Only new posts downloaded
6. Existing local posts remain unmodified
7. Post list updated to reflect current remote state
8. Task metadata updated with new total count and sync timestamp

## Data Extraction Strategy

### Post List Page Analysis

Target URL pattern:
- Base structure: `https://danbooru.donmai.us/posts?page={page_number}&tags={tag_string}`
- Tags joined with plus signs (spaces encoded as `+`)

HTML extraction points:

| Data Element | Selector Strategy | Example |
|--------------|-------------------|---------|
| Total Pages | Locate `.paginator-next` element, extract `href` from preceding `a` sibling | Page 65 from `href="/posts?page=65&tags=honma_meiko"` |
| Post IDs | Find all elements with class `.post-preview-link`, extract post ID from `href` attribute | Post 10200019 from `href="/posts/10200019?q=honma_meiko"` |

### Post Detail Page Analysis

Target URL pattern:
- Structure: `https://danbooru.donmai.us/posts/{post_id}`

HTML extraction points:

| Data Element | Selector Strategy | Location |
|--------------|-------------------|----------|
| Original Image URL | Locate element with class `.image-view-original-link`, extract `href` attribute | Example: `https://cdn.donmai.us/original/67/7d/__honma_meiko...677d8bf54414fd96d9dac833d2e04585.png` |
| Artist Tags | Within `#tag-list` section, find `ul.artist-tag-list` items, extract tag names from `data-tag-name` attributes |
| Copyright Tags | Within `#tag-list` section, find `ul.copyright-tag-list` items, extract tag names from `data-tag-name` attributes |
| Character Tags | Within `#tag-list` section, find `ul.character-tag-list` items, extract tag names from `data-tag-name` attributes |
| General Tags | Within `#tag-list` section, find `ul.general-tag-list` items, extract tag names from `data-tag-name` attributes |
| Meta Tags | Within `#tag-list` section, find `ul.meta-tag-list` items, extract tag names from `data-tag-name` attributes |

## Task Storage Structure

### Directory Organization

Structure created under user-specified storage path:

```
{user_storage_path}/
└── {sanitized_tag_string}_{hash}/
    ├── task_metadata.json
    ├── post_list.json
    └── posts/
        ├── {post_id_1}.{extension}
        ├── {post_id_1}_tags.json
        ├── {post_id_2}.{extension}
        ├── {post_id_2}_tags.json
        └── ...
```

Example with user-provided storage path `/home/user/danbooru_tasks`:
```
/home/user/danbooru_tasks/
└── honma_meiko_abc123/
    ├── task_metadata.json
    ├── post_list.json
    └── posts/
        └── ...
```

### Task Metadata Schema

| Field | Type | Description |
|-------|------|-------------|
| search_tags | String | Original user-provided tag string |
| storage_path | String | User-specified base storage path |
| task_folder | String | Full path to task folder |
| created_at | Timestamp | Task creation timestamp |
| last_updated | Timestamp | Most recent task update timestamp |
| last_synced | Timestamp | Most recent sync operation timestamp (null if never synced) |
| status | Enum | PENDING / IN_PROGRESS / COMPLETE / FAILED |
| total_posts | Integer | Total number of posts in current list |
| completed_posts | Integer | Number of successfully downloaded posts |
| mode_history | Array[String] | Chronological log of execution modes (new, resume, sync) |

### Post List Schema

| Field | Type | Description |
|-------|------|-------------|
| post_id | Integer | Unique post identifier from Danbooru |
| status | Enum | PENDING / COMPLETE / FAIL |
| image_url | String | Full URL to original image resource |
| file_extension | String | Image file extension (png, jpg, etc.) |
| download_timestamp | Timestamp | When post was successfully downloaded (null if pending/failed) |

### Tag Metadata Schema

Stored per post as separate JSON file:

| Field | Type | Description |
|-------|------|-------------|
| post_id | Integer | Reference to parent post |
| artist | Array[String] | List of artist tags |
| copyright | Array[String] | List of copyright tags |
| character | Array[String] | List of character tags |
| general | Array[String] | List of general descriptive tags |
| meta | Array[String] | List of meta tags |

## Rate Limiting Strategy

### Throttle Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Request Interval | 2-3 seconds | Prevents triggering anti-crawler mechanisms |
| Burst Limit | None | Sequential requests only, no concurrent batching |
| Retry Delay | Exponential backoff starting at 5 seconds | Reduces server load during transient failures |

### Implementation Approach

Between each HTTP request, the system enforces a mandatory delay period. This applies to:
- Pagination navigation requests
- Individual post detail page requests
- Image download requests

The delay is implemented as a blocking sleep operation to ensure strict sequential execution.

## Error Handling Protocol

### Response Status Categories

| Status Code Range | Interpretation | Action |
|-------------------|----------------|--------|
| 410, 403 | Server intentionally refuses request | Halt process, notify user for manual intervention |
| 404 | Resource not found | Mark post as FAIL, continue to next post |
| 5xx | Server-side error | Retry with exponential backoff |
| Timeout / Connection Reset | Network instability | Retry with exponential backoff |

### Retry Mechanism

| Parameter | Value |
|-----------|-------|
| Maximum Retry Attempts | 3 |
| Base Delay | 5 seconds |
| Backoff Multiplier | 2x (5s, 10s, 20s) |
| Final Action on Exhaustion | Mark as FAIL, move to next post |

When encountering status codes 410 or 403:
1. Suspend all download operations
2. Log detailed error information including URL, timestamp, response headers
3. Display notification to user with suggestion for manual resolution
4. Preserve current task state for later resumption
5. Exit process gracefully

## Image Download Strategy

### Download Process

The system must never stream images directly to disk. Instead:

1. Initiate HTTP GET request to original image URL
2. Read entire response body into memory buffer
3. Validate response completeness (content-length match)
4. Verify image file integrity (basic file format validation)
5. Write buffer contents to disk in single atomic operation
6. Only after successful disk write, mark post status as COMPLETE

### File Naming Convention

Images are stored with post ID as filename:
- Format: `{post_id}.{original_extension}`
- Extension determined from image URL or content-type header
- Example: `10337509.png`

This ensures:
- Unique filenames without collisions
- Easy correlation between images and metadata
- Predictable file location for resumption logic

## Command-Line Interface Design

### Invocation Modes

The system operates through command-line invocation without any GUI components.

#### Mode 1: New Task Creation

Command structure:
```
python danbooru_scraper.py --mode new --tags "tag1 tag2" --storage-path "/path/to/storage"
```

Required arguments:

| Argument | Type | Description | Example |
|----------|------|-------------|----------|
| --mode | String | Operation mode (new/resume/sync) | new |
| --tags | String | Space or comma-separated search tags | "honma_meiko ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai." |
| --storage-path | String | Local directory path where task folder will be created | /home/user/danbooru_tasks |

Optional arguments:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| --throttle | Float | 2.5 | Seconds between requests |
| --max-retries | Integer | 3 | Maximum retry attempts per request |
| --proxy | String | None | Proxy server URL (HTTP/HTTPS/SOCKS5) |
| --proxy-auth | String | None | Proxy authentication in format "username:password" |

#### Mode 2: Resume Incomplete Task

Command structure:
```
python danbooru_scraper.py --mode resume --task-path "/path/to/task_folder"
```

Required arguments:

| Argument | Type | Description |
|----------|------|-------------|
| --mode | String | Must be "resume" |
| --task-path | String | Full path to existing incomplete task folder |

Optional arguments:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| --proxy | String | None | Proxy server URL (HTTP/HTTPS/SOCKS5) |
| --proxy-auth | String | None | Proxy authentication in format "username:password" |

Behavior:
- Resumes download from first incomplete post
- Automatically triggers sync operation after all pending posts complete
- Sync operation retrieves and downloads any new posts added since task creation
- Proxy settings apply to all requests during resume and subsequent sync

#### Mode 3: Sync Completed Task

Command structure:
```
python danbooru_scraper.py --mode sync --task-path "/path/to/task_folder"
```

Required arguments:

| Argument | Type | Description |
|----------|------|-------------|
| --mode | String | Must be "sync" |
| --task-path | String | Full path to existing completed task folder |

Optional arguments:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| --proxy | String | None | Proxy server URL (HTTP/HTTPS/SOCKS5) |
| --proxy-auth | String | None | Proxy authentication in format "username:password" |

### Console Output Format

All user feedback delivered through stdout/stderr:

**Initialization Phase:**
```
[INFO] Danbooru Scraper v1.0
[INFO] Mode: new
[INFO] Tags: honma_meiko
[INFO] Storage: /home/user/danbooru_tasks
[INFO] Proxy: http://proxy.example.com:8080 (authenticated)
[INFO] Creating task folder: /home/user/danbooru_tasks/honma_meiko_abc123
[INFO] Fetching search results...
[INFO] Total pages found: 65
[INFO] Total posts found: 1282
```

**Download Phase:**
```
[PROGRESS] Downloading post 1/1282 (ID: 10337509)
[SUCCESS] Image saved: 10337509.png (11.7 MB)
[SUCCESS] Tags saved: 10337509_tags.json
[PROGRESS] Downloading post 2/1282 (ID: 10243316)
...
```

**Error Handling:**
```
[ERROR] Post 10200019: HTTP 403 - Server refused request
[FATAL] Halting process. Manual intervention required.
[INFO] Task state saved. Resume with: python danbooru_scraper.py --mode resume --task-path "/home/user/danbooru_tasks/honma_meiko_abc123"
```

**Completion:**
```
[INFO] Download phase complete: 1282/1282 posts
[INFO] Triggering automatic sync operation...
[INFO] Sync complete: 15 new posts downloaded
[SUCCESS] Task complete. Total posts: 1297
```

### Exit Codes

| Code | Meaning |
|------|--------|
| 0 | Success - task completed normally |
| 1 | Invalid arguments or missing required parameters |
| 2 | Task folder validation failed (not found, corrupted, etc.) |
| 3 | Network error exhausted all retries |
| 4 | Server refusal (403/410) requiring manual intervention |
| 5 | Storage path not writable or insufficient disk space |
| 6 | Proxy connection failed or protocol not supported |
| 7 | Proxy authentication failed |

## User Interaction Flow

### Initial Task Creation

```mermaid
sequenceDiagram
    participant CLI as Command Line
    participant System
    participant Danbooru
    
    CLI->>System: Execute with --mode new --tags "..." --storage-path "..."
    System->>System: Parse and validate arguments
    System->>System: Validate storage path writable
    System->>System: Sanitize tags and create task folder
    System->>CLI: Output: Task folder created
    System->>Danbooru: Fetch first page of results
    Danbooru-->>System: HTML with pagination info
    System->>System: Extract total page count
    System->>CLI: Output: Total pages found
    loop For each page
        System->>Danbooru: Fetch page
        Danbooru-->>System: HTML with post previews
        System->>System: Extract post IDs
    end
    System->>System: Persist post list
    System->>CLI: Output: Total posts found
    loop For each post
        System->>Danbooru: Fetch post detail
        Danbooru-->>System: HTML with image and tags
        System->>System: Extract image URL and tags
        System->>Danbooru: Download image
        Danbooru-->>System: Image binary data
        System->>System: Save image and metadata
        System->>CLI: Output: Progress (X/Y complete)
    end
    System->>CLI: Output: Task complete, exit code 0
```

### Resumption from Breakpoint with Auto-Sync

```mermaid
sequenceDiagram
    participant CLI as Command Line
    participant System
    participant Danbooru
    
    CLI->>System: Execute with --mode resume --task-path "..."
    System->>System: Validate task folder exists
    System->>System: Load task metadata and post list
    System->>System: Identify incomplete posts
    System->>CLI: Output: Resume info (X posts remaining)
    loop From breakpoint to end
        System->>Danbooru: Fetch post detail
        Danbooru-->>System: HTML with image and tags
        System->>Danbooru: Download image
        Danbooru-->>System: Image data
        System->>System: Save and mark COMPLETE
        System->>CLI: Output: Progress update
    end
    System->>CLI: Output: Download phase complete
    System->>CLI: Output: Starting automatic sync
    System->>Danbooru: Fetch current post list
    Danbooru-->>System: All current posts
    System->>System: Compare with local list
    System->>System: Identify new posts
    loop For each new post
        System->>Danbooru: Fetch and download
        System->>CLI: Output: Downloading new post
    end
    System->>CLI: Output: Sync complete, exit code 0
```

## Proxy Configuration

### Proxy Support Strategy

The system must support proxy servers to enable access from regions where Danbooru is blocked or restricted.

### Proxy Protocol Support

| Protocol | Support | Description |
|----------|---------|-------------|
| HTTP | Yes | Standard HTTP proxy |
| HTTPS | Yes | HTTPS proxy with TLS |
| SOCKS5 | Yes | SOCKS5 proxy for TCP connections |
| SOCKS4 | No | Not required for this implementation |

### Proxy URL Format

Expected formats for `--proxy` argument:

| Format | Example | Use Case |
|--------|---------|----------|
| HTTP | `http://proxy.example.com:8080` | Basic HTTP proxy |
| HTTPS | `https://proxy.example.com:8443` | Secure proxy connection |
| SOCKS5 | `socks5://proxy.example.com:1080` | SOCKS5 proxy |
| With embedded auth | `http://user:pass@proxy.example.com:8080` | Proxy with inline credentials |

### Authentication Handling

Two methods for proxy authentication:

1. **Embedded in URL**: Credentials included in proxy URL
   - Format: `protocol://username:password@host:port`
   - Example: `http://john:secret123@proxy.example.com:8080`

2. **Separate argument**: Using `--proxy-auth`
   - Format: `username:password`
   - Example: `--proxy "http://proxy.example.com:8080" --proxy-auth "john:secret123"`

Priority: If both methods provided, embedded credentials take precedence.

### Proxy Application Scope

Proxy settings apply to all HTTP/HTTPS requests:
- Search result page fetching
- Post detail page fetching
- Image downloads
- Pagination traversal

### Proxy Validation

During initialization phase:
1. Parse proxy URL for validity
2. Attempt test connection through proxy to Danbooru homepage
3. If test fails, abort with clear error message
4. Log proxy configuration (without exposing credentials)

### Proxy Error Handling

| Error Type | Action |
|------------|--------|
| Proxy connection refused | Abort with error code 6, display proxy connection failed message |
| Proxy authentication failed | Abort with error code 7, display authentication error |
| Proxy timeout | Retry with exponential backoff (same as network errors) |
| Proxy protocol mismatch | Abort with error code 6, display protocol not supported message |

### Configuration Persistence

Proxy settings are NOT persisted to task metadata for security reasons:
- User must provide proxy settings on each invocation
- This prevents accidental credential exposure in stored files
- Allows changing proxy servers between resume operations

### Example Invocations

**New task with HTTP proxy:**
```
python danbooru_scraper.py --mode new \
  --tags "honma_meiko" \
  --storage-path "/home/user/tasks" \
  --proxy "http://proxy.example.com:8080"
```

**Resume with authenticated SOCKS5 proxy:**
```
python danbooru_scraper.py --mode resume \
  --task-path "/home/user/tasks/honma_meiko_abc123" \
  --proxy "socks5://proxy.example.com:1080" \
  --proxy-auth "username:password"
```

**Sync with HTTPS proxy (embedded auth):**
```
python danbooru_scraper.py --mode sync \
  --task-path "/home/user/tasks/honma_meiko_abc123" \
  --proxy "https://user:pass@proxy.example.com:8443"
```

## Technical Considerations

### HTML Parsing Approach

The system should employ a robust HTML parsing library rather than regular expressions. Recommended strategy:
- Use DOM tree traversal with CSS selectors
- Gracefully handle missing or malformed elements
- Log warnings for unexpected page structure

### Task Folder Naming

Tag string sanitization rules:
- Replace spaces with underscores
- Remove special characters except underscore and hyphen
- Convert to lowercase for consistency
- Truncate to reasonable length (50 characters) to avoid filesystem limitations
- Append hash of full tag string if truncation occurs (to ensure uniqueness)

### Concurrency Constraints

The system operates in strictly sequential mode:
- No parallel page fetching
- No concurrent image downloads
- Single-threaded execution to simplify rate limiting and error handling
- Single proxy connection reused across requests (connection pooling)

This design choice prioritizes reliability and server politeness over raw speed.

### Proxy Connection Management

When proxy is configured:
- Establish persistent connection pool through proxy
- Reuse connections where possible to reduce overhead
- Apply same rate limiting rules regardless of proxy usage
- Close proxy connections gracefully on task completion or error

### Progress Tracking

During execution, the system should provide user feedback:
- Current operation (fetching list, downloading post X of Y)
- Estimated time remaining based on average download time
- Real-time status updates for failures or retries

## Extensibility Considerations

While not implemented in initial version, the design accommodates future enhancements:

| Enhancement | Design Accommodation |
|-------------|---------------------|
| Multi-threading | Post list is independent; download loop can be parallelized with thread-safe status updates |
| Database storage | JSON schemas map cleanly to relational tables |
| Incremental sync | Post list comparison logic already supports differential updates |
| Advanced retry logic | Retry mechanism is isolated and can be enhanced without affecting core workflow |
| Image format conversion | Download-to-memory approach enables pre-persistence processing |

## Success Criteria

The design is considered successful when:

1. User can initiate scraping with arbitrary tag combinations
2. All posts matching search criteria are discovered and downloaded
3. High-resolution original images are preserved locally
4. Complete tag metadata is captured for each post
5. Interrupted tasks can resume without data loss or duplication
6. Completed tasks can be synchronized with new remote posts
7. Server rate limits are respected without manual intervention
8. Transient network errors recover automatically
9. Server refusals are surfaced to user for resolution
10. Task state is transparent and inspectable at any point9. Server refusals are surfaced to user for resolution
