# kiwix-search

A command-line search tool and importable Python module for querying a self-hosted [Kiwix](https://kiwix.org) server across one or multiple ZIM libraries. Built as a homelab utility and designed as connective tissue for local AI agent tool integration.

## Requirements

- Python 3.x
- A running Kiwix server (see [kiwix-serve](https://github.com/kiwix/kiwix-tools))
- Dependencies: `requests`, `beautifulsoup4`, `PyYAML`

```bash
pip install -r requirements.txt
```

## Configuration

Copy `config.example.yaml` to `config.yaml` and update to match your setup:

```bash
cp config.example.yaml config.yaml
```

Key config options:

```yaml
kiwix_server_url: "http://192.168.3.5:8081"   # your Kiwix server
default_book: "wikipedia_en_all_maxi_2026-02"  # default book for unscoped searches
results_per_book: 3       # results fetched per book in --all mode
max_total_results: 10     # total results returned in --all mode
single_book_limit: 5      # results returned for single book searches
books:                    # list of ZIM files on your server
  - "wikipedia_en_all_maxi_2026-02"
  - ...
keyword_mapping:          # maps query keywords to relevant books for relevance weighting
  raspberry pi:
    - "raspberrypi.stackexchange.com_en_all_2026-02"
  ...
```

If `config.yaml` is not found the script falls back to built-in defaults with a warning. Book names correspond to ZIM filenames without the `.zim` extension.

## CLI Usage

### Search default book (Wikipedia)
```bash
python kiwix_search.py artificial intelligence
```

### Search a specific book
```bash
python kiwix_search.py --book unix.stackexchange.com_en_all_2026-02 bash scripting
python kiwix_search.py -b raspberrypi.stackexchange.com_en_all_2026-02 gpio pwm
```

### Search all configured books (relevance-weighted)
```bash
python kiwix_search.py --all docker networking
python kiwix_search.py -a raspberry pi gpio
```

### Fetch full article content
```bash
python kiwix_search.py --fetch /content/wikipedia_en_all_maxi_2026-02/Python_(programming_language)
python kiwix_search.py -f /content/raspberrypi.stackexchange.com_en_all_2026-02/questions/117591/controlling-raspberry-pi-gpio-with-c-and-python
```

### Print OpenAI function calling schema
```bash
python kiwix_search.py --tool-definition
```

## Module Usage

`kiwix_search` can be imported directly for use in scripts or agent tool integrations:

```python
from kiwix_search import search, fetch_article, get_tool_definition

# Search default book (Wikipedia)
results = search("artificial intelligence")

# Search a specific book
results = search("gpio pwm", book="raspberrypi.stackexchange.com_en_all_2026-02")

# Search all configured books with relevance weighting
results = search("raspberry pi gpio", all_books=True)

# Fetch full article text from a result URL path
article = fetch_article(results[0]['url_path'])

# Get OpenAI function calling schema for agent integration
schema = get_tool_definition()

# Results are a list of dicts
for r in results:
    print(r['title'])
    print(r['book'])
    print(r['excerpt'])
    print(r['url_path'])
```

## How It Works

- Single book searches return up to `single_book_limit` results (default 5)
- `--all` / `all_books=True` uses keyword-based relevance weighting to prioritize the most relevant books for the query, fetches `results_per_book` results per book (default 3), deduplicates by URL path, and returns up to `max_total_results` (default 10)
- `fetch_article()` retrieves the full plain text of any article by URL path — enables a complete search → read loop for agent use
- `get_tool_definition()` returns the OpenAI function calling schema for drop-in agent integration
- The Kiwix `/search` endpoint requires scoping to a specific book — searches without `books.name` will fail if your server hosts ZIMs in multiple languages

## Relevance Weighting

When using `--all`, the query is matched against `keyword_mapping` in `config.yaml` to prioritize relevant books. Matched books are searched first in order of relevance score; unmatched books follow. The mapping is fully user-configurable — add new keywords and books as your ZIM library grows.

## ZIM Library

The default books list includes the following ZIM files. Update `config.yaml` to match your server:

- `wikipedia_en_all_maxi_2026-02` — English Wikipedia (full)
- `wiktionary_en_all_nopic_2025-09` — English Wiktionary
- `ifixit_en_all_2025-12` — iFixit repair guides
- `freecodecamp_en_all_2026-05` — freeCodeCamp
- `freecodecamp_en_coding-interview-prep_2026-05` — freeCodeCamp interview prep
- `freecodecamp_en_rosetta-code_2026-05` — Rosetta Code
- `devdocs_en_nginx_2026-04` — nginx documentation
- `devdocs_en_python_2026-05` — Python documentation
- Stack Exchange communities: `ai`, `arduino`, `cs`, `datascience`, `dba`, `devops`, `electronics`, `iot`, `math`, `mathematica`, `movies`, `raspberrypi`, `retrocomputing`, `reverseengineering`, `robotics`, `scicomp`, `scifi`, `space`, `unix`

## Tools

### Open WebUI

`tools/kiwix_openwebui_tool.py` is a native Open WebUI tool that exposes Kiwix search directly to any model running in Open WebUI.

**Install:** Workspace → Tools → Create Tool → paste file contents → save.

The tool uses the same relevance-weighted book prioritization as the core library. Tag index pages are filtered from results automatically. Update `kiwix_url` and `books` in the `__init__` method to match your server.

## Roadmap

- [ ] Expand keyword mapping (open for contributions)

## License

MIT
