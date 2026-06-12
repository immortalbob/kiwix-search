#!/usr/bin/env python3

import sys
import requests
from bs4 import BeautifulSoup
import argparse
import yaml
import os
import json

def load_config():
    """Load configuration from config.yaml or use defaults"""
    config_file = 'config.yaml'
    
    # Default configuration
    default_config = {
        'kiwix_server_url': 'http://192.168.3.5:8081',
        'default_book': 'wikipedia_en_all_maxi_2026-02',
        'books': [
            'ai.stackexchange.com_en_all_2026-02',
            'arduino.stackexchange.com_en_all_2026-02',
            'cs.stackexchange.com_en_all_2026-02',
            'datascience.stackexchange.com_en_all_2026-02',
            'dba.stackexchange.com_en_all_2026-02',
            'devdocs_en_nginx_2026-04',
            'devdocs_en_python_2026-05',
            'devops.stackexchange.com_en_all_2026-02',
            'electronics.stackexchange.com_en_all_2026-02',
            'freecodecamp_en_all_2026-05',
            'freecodecamp_en_coding-interview-prep_2026-05',
            'freecodecamp_en_rosetta-code_2026-05',
            'ifixit_en_all_2025-12',
            'iot.stackexchange.com_en_all_2026-02',
            'math.stackexchange.com_en_all_2026-02',
            'mathematica.stackexchange.com_en_all_2026-02',
            'movies.stackexchange.com_en_all_2026-02',
            'raspberrypi.stackexchange.com_en_all_2026-02',
            'retrocomputing.stackexchange.com_en_all_2026-02',
            'reverseengineering.stackexchange.com_en_all_2026-02',
            'robotics.stackexchange.com_en_all_2026-02',
            'scicomp.stackexchange.com_en_all_2026-02',
            'scifi.stackexchange.com_en_all_2026-02',
            'space.stackexchange.com_en_all_2026-02',
            'unix.stackexchange.com_en_all_2026-02',
            'wikipedia_en_all_maxi_2026-02',
            'wikivoyage_de_all_maxi_2026-04',
            'wiktionary_en_all_nopic_2025-09'
        ],
        'keyword_mapping': {
            # Hardware/Maker
            'raspberry pi': ['raspberrypi.stackexchange.com_en_all_2026-02', 'ifixit_en_all_2025-12'],
            'esp32': ['iot.stackexchange.com_en_all_2026-02', 'electronics.stackexchange.com_en_all_2026-02'],
            'gpio': ['raspberrypi.stackexchange.com_en_all_2026-02', 'electronics.stackexchange.com_en_all_2026-02'],
            'arduino': ['arduino.stackexchange.com_en_all_2026-02', 'electronics.stackexchange.com_en_all_2026-02'],
            
            # Sysadmin
            'docker': ['devops.stackexchange.com_en_all_2026-02', 'unix.stackexchange.com_en_all_2026-02'],
            'nginx': ['devdocs_en_nginx_2026-04', 'unix.stackexchange.com_en_all_2026-02'],
            'bash': ['unix.stackexchange.com_en_all_2026-02'],
            'unix': ['unix.stackexchange.com_en_all_2026-02'],
            
            # Programming
            'python': ['devdocs_en_python_2026-05', 'freecodecamp_en_all_2026-05', 'cs.stackexchange.com_en_all_2026-02'],
            'coding': ['freecodecamp_en_all_2026-05', 'cs.stackexchange.com_en_all_2026-02'],
            'algorithm': ['cs.stackexchange.com_en_all_2026-02', 'datascience.stackexchange.com_en_all_2026-02'],
            
            # Data Science
            'data science': ['datascience.stackexchange.com_en_all_2026-02'],
            'machine learning': ['ai.stackexchange.com_en_all_2026-02'],
            'artificial intelligence': ['ai.stackexchange.com_en_all_2026-02'],
            
            # Web Development
            'web': ['freecodecamp_en_all_2026-05', 'devdocs_en_python_2026-05'],
            
            # General
            'wiki': ['wikipedia_en_all_maxi_2026-02'],
        },
        'results_per_book': 3,
        'max_total_results': 10,
        'single_book_limit': 5
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Merge defaults with user config
            merged_config = default_config.copy()
            if config:
                merged_config.update(config)
            
            return merged_config
        except Exception as e:
            print(f"Warning: Could not read config file {config_file}: {e}")
            print("Using default configuration.")
            return default_config
    else:
        print(f"Warning: Config file {config_file} not found. Using default configuration.")
        return default_config

def get_relevant_books(query, books, keyword_mapping):
    """
    Score books based on keyword relevance to the query.
    
    Args:
        query (str): The search query string
        books (list): List of all available books
        keyword_mapping (dict): Mapping of keywords to relevant books
        
    Returns:
        list: Prioritized list of books with matched books first
    """
    # Normalize query to lowercase for matching
    query_lower = query.lower()
    
    # Score books based on keyword matches
    book_scores = {}
    matched_books = set()
    
    # Check for keyword matches
    for keyword, relevant_books in keyword_mapping.items():
        if keyword in query_lower:
            for book in relevant_books:
                if book not in book_scores:
                    book_scores[book] = 0
                book_scores[book] += 1
                matched_books.add(book)
    
    # Create prioritized list: matched books first, then others
    prioritized_books = []
    
    # Add matched books first (sorted by score descending)
    matched_sorted = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)
    for book, score in matched_sorted:
        prioritized_books.append(book)
    
    # Add remaining books
    for book in books:
        if book not in matched_books:
            prioritized_books.append(book)
    
    return prioritized_books

def search_kiwix_single_book(query, book_name, server_url, limit=None):
    """Search Kiwix server for a single book and return top results"""
    # Construct the search URL with required parameters
    search_url = f"{server_url}/search"
    params = {
        'pattern': query,
        'books.name': book_name,
        'limit': limit or 5  # Default to 5 if no limit provided
    }
    
    try:
        # Make the request
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        
        # Parse the HTML response
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the results div
        results_div = soup.find('div', class_='results')
        if not results_div:
            return []
        
        # Find all result list items
        result_items = results_div.find_all('li')
        results = []
        
        for item in result_items:
            # Extract title and URL from the <a> tag
            a_tag = item.find('a')
            if not a_tag:
                continue
                
            title = a_tag.get_text(strip=True)
            url_path = a_tag.get('href', '')
            
            # Extract excerpt from the <cite> tag
            cite_tag = item.find('cite')
            excerpt = cite_tag.get_text(strip=True) if cite_tag else 'No excerpt'
            
            results.append({
                'title': title,
                'excerpt': excerpt,
                'url_path': url_path,
                'book': book_name
            })
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Kiwix server for {book_name}: {e}")
        return []
    except Exception as e:
        print(f"Error parsing response for {book_name}: {e}")
        return []

def search_kiwix_all_books(query, books, server_url, keyword_mapping, config):
    """Search all books and merge results"""
    all_results = []
    
    # Use prioritized books list if query has relevant keywords
    prioritized_books = get_relevant_books(query, books, keyword_mapping)
    
    # If we have a prioritized list that's different from the original, use it
    if prioritized_books != books:
        books_to_search = prioritized_books
    else:
        books_to_search = books
    
    # Get config values
    results_per_book = config.get('results_per_book', 3)
    single_book_limit = config.get('single_book_limit', 5)
    
    for book in books_to_search:
        print(f"Searching in {book}...")
        # Use results_per_book for multi-book searches, not single_book_limit
        results = search_kiwix_single_book(query, book, server_url, limit=results_per_book)
        all_results.extend(results)
    
    # Deduplicate by URL path
    seen_urls = set()
    unique_results = []
    
    for result in all_results:
        if result['url_path'] not in seen_urls:
            seen_urls.add(result['url_path'])
            unique_results.append(result)
    
    # Return top results based on max_total_results
    max_total_results = config.get('max_total_results', 10)
    return unique_results[:max_total_results]

def get_tool_definition():
    """Return an OpenAI function calling schema dict for the search() function"""
    return {
        "name": "search",
        "description": "Search Kiwix server for content across books",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string"
                },
                "book": {
                    "type": "string",
                    "description": "Specific book to search. Must be a book name from the books list."
                },
                "all_books": {
                    "type": "boolean",
                    "description": "If True, search all books"
                }
            },
            "required": ["query"]
        }
    }

def print_results(results):
    """Print search results in a clean format"""
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} result(s):")
    print("-" * 60)
    
    for i, result in enumerate(results, 1):
        title = result.get('title', 'No title')
        excerpt = result.get('excerpt', 'No excerpt')
        url_path = result.get('url_path', '')
        book = result.get('book', 'Unknown')
        
        print(f"{i}. {title}")
        print(f"   Source: {book}")
        print(f"   {excerpt}")
        if url_path:
            print(f"   URL: {url_path}")
        print()

def fetch_article(url_path, config=None):
    """
    Fetch full article content from Kiwix server and return clean plain text.
    
    Args:
        url_path (str): The URL path of the article to fetch
        config (dict): Configuration dictionary
    
    Returns:
        str: Clean plain text content of the article
    """
    if config is None:
        config = load_config()
    
    server_url = config['kiwix_server_url']
    
    try:
        # Construct full URL
        full_url = f"{server_url}{url_path}"
        
        # Make the request
        response = requests.get(full_url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Kiwix server: {e}")
        return ""
    except Exception as e:
        print(f"Error fetching article: {e}")
        return ""

def search(query, book=None, all_books=False, config=None):
    """
    Search Kiwix server and return results as a list of dictionaries.
    
    Args:
        query (str): The search query string
        book (str, optional): Specific book to search. If None, searches default book.
        all_books (bool): If True, search all books
        config (dict): Configuration dictionary
    
    Returns:
        list: List of result dictionaries with keys 'title', 'excerpt', 'url_path', 'book'
    """
    if config is None:
        config = load_config()
    
    server_url = config['kiwix_server_url']
    default_book = config['default_book']
    books = config['books']
    keyword_mapping = config['keyword_mapping']
    
    # Perform search based on arguments
    if all_books:
        results = search_kiwix_all_books(query, books, server_url, keyword_mapping, config)
    elif book:
        results = search_kiwix_single_book(query, book, server_url)
    else:
        # Default behavior - search default book
        results = search_kiwix_single_book(query, default_book, server_url)
    
    return results

def main():
    # Load configuration
    config = load_config()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Search Kiwix server')
    parser.add_argument('query', nargs='+', help='Search term(s)')
    parser.add_argument('--book', '-b', help='Specific book to search')
    parser.add_argument('--all', '-a', action='store_true', help='Search all books')
    parser.add_argument('--fetch', '-f', help='Fetch full article content for a given URL path')
    parser.add_argument('--tool-definition', action='store_true', help='Print tool definition as JSON and exit')
    
    args = parser.parse_args()
    
    # If --tool-definition flag is used, print the tool definition and exit
    if args.tool_definition:
        tool_definition = get_tool_definition()
        print(json.dumps(tool_definition, indent=2))
        return
    
    # If --fetch flag is used, fetch the article and exit
    if args.fetch:
        article_text = fetch_article(args.fetch, config)
        if article_text:
            print(article_text)
        else:
            print("Failed to fetch article.")
        return
    
    # Get search term from command line
    search_term = " ".join(args.query)
    
    # Print search term
    print(f"Searching for: '{search_term}'")
    
    # Call the search function with CLI arguments
    results = search(search_term, book=args.book, all_books=args.all, config=config)
    
    # Print results
    print_results(results)

if __name__ == "__main__":
    main()
