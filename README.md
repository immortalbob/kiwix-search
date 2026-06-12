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

```yaml
kiwix_server_url: "http://192.168.3.5:8081"
default_book: "wikipedia_en_all_maxi_2026-02"
books:
  - "wikipedia_en_all_maxi_2026-02"
  - "raspberrypi.stackexchange.com_en_all_2026-02"
  # ... add your ZIM files here
```

If `config.yaml` is not found, the script falls back to built-in defaults with a warning. Book names correspond to ZIM filenames without the `.zim` extension.

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

## Module Usage

`kiwix_search` can be imported directly for use in scripts or agent tool integrations:

```python
from kiwix_search import search, fetch_article

# Search default book (Wikipedia)
results = search("artificial intelligence")

# Search a specific book
results = search("gpio pwm", book="raspberrypi.stackexchange.com_en_all_2026-02")

# Search all configured books with relevance weighting
results = search("raspberry pi gpio", all_books=True)

# Fetch full article text from a result URL path
article = fetch_article(results[0]['url_path'])

# Results are a list of dicts
for r in results:
    print(r['title'])
    print(r['book'])
    print(r['excerpt'])
    print(r['url_path'])
```

## How It Works

- Single book searches return up to 5 results
- `--all` / `all_books=True` uses keyword-based relevance weighting to prioritize the most relevant books for the query, then searches all configured books in that order
- Results are deduplicated by URL path and the top 10 are returned
- `fetch_article()` retrieves the full plain text of any article by URL path — enables a complete search → read loop for agent use
- The Kiwix `/search` endpoint requires scoping to a specific book — searches without `books.name` will fail if your server hosts ZIMs in multiple languages

## Relevance Weighting

When using `--all`, the query is matched against a keyword map to prioritize relevant books. For example:

- `raspberry pi`, `gpio` → raspberrypi, electronics books searched first
- `docker`, `nginx`, `bash` → devops, unix books searched first
- `python`, `algorithm` → devdocs-python, freecodecamp, cs books searched first
- `machine learning`, `artificial intelligence` → ai books searched first

Unmatched books are appended after matched ones and still searched.

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

## Roadmap

- [ ] Agent tool definition (OpenAI function calling schema)
- [ ] Expand keyword mapping for relevance weighting (open for contributions)

## License

MIT
