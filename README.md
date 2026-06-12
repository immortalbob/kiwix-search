# kiwix-search

A command-line search tool and importable Python module for querying a self-hosted [Kiwix](https://kiwix.org) server across one or multiple ZIM libraries. Built as a homelab utility and designed as connective tissue for local AI agent tool integration.

## Requirements

- Python 3.x
- A running Kiwix server (see [kiwix-serve](https://github.com/kiwix/kiwix-tools))
- Dependencies: `requests`, `beautifulsoup4`

```bash
pip install -r requirements.txt
```

## Configuration

The Kiwix server URL and book list are defined in `kiwix_search.py`. Update the server URL to match your setup:

```python
search_url = "http://192.168.3.5:8081/search"  # your Kiwix server
```

The `books` list reflects the ZIM files available on your server. Book names correspond to ZIM filenames without the `.zim` extension. Update this list to match your installed ZIMs.

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

### Search all configured books
```bash
python kiwix_search.py --all docker networking
python kiwix_search.py -a esp32 wake word detection
```

## Module Usage

`kiwix_search` can be imported directly for use in scripts or agent tool integrations:

```python
from kiwix_search import search

# Search default book (Wikipedia)
results = search("artificial intelligence")

# Search a specific book
results = search("gpio pwm", book="raspberrypi.stackexchange.com_en_all_2026-02")

# Search all configured books
results = search("docker networking", all_books=True)

# Results are a list of dicts
for r in results:
    print(r['title'])
    print(r['book'])
    print(r['excerpt'])
    print(r['url_path'])
```

## How It Works

- Single book searches return up to 5 results
- `--all` / `all_books=True` queries each configured book individually, pulls top 3 results per book, deduplicates by URL path, and returns the top 10 combined results
- Results include title, source book, excerpt, and full article URL path
- The Kiwix `/search` endpoint requires scoping to a specific book — searches without `books.name` will fail if your server hosts ZIMs in multiple languages

## ZIM Library

The default books list includes the following ZIM files. Update to match your server:

- `wikipedia_en_all_maxi_2026-02` — English Wikipedia (full)
- `wiktionary_en_all_nopic_2025-09` — English Wiktionary
- `wikivoyage_de_all_maxi_2026-04` — German Wikivoyage
- `ifixit_en_all_2025-12` — iFixit repair guides
- `freecodecamp_en_all_2026-05` — freeCodeCamp
- `freecodecamp_en_coding-interview-prep_2026-05` — freeCodeCamp interview prep
- `freecodecamp_en_rosetta-code_2026-05` — Rosetta Code
- `devdocs_en_nginx_2026-04` — nginx documentation
- `devdocs_en_python_2026-05` — Python documentation
- Stack Exchange communities: `ai`, `arduino`, `cs`, `datascience`, `dba`, `devops`, `electronics`, `iot`, `math`, `mathematica`, `movies`, `raspberrypi`, `retrocomputing`, `reverseengineering`, `robotics`, `scicomp`, `scifi`, `space`, `unix`

## Roadmap

- [ ] Config file for server URL and book list instead of hardcoded values
- [ ] Relevance-weighted multi-book search (prioritize books by query context)
- [ ] Agent tool definition (OpenAI function calling schema)
- [ ] Fetch and return full article content by URL path

## License

MIT
