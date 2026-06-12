#!/usr/bin/env python3

import sys
import requests
from bs4 import BeautifulSoup
import argparse

def search_kiwix_single_book(query, book_name):
    """Search Kiwix server for a single book and return top 5 results"""
    # Construct the search URL with required parameters
    search_url = f"http://192.168.3.5:8081/search"
    params = {
        'pattern': query,
        'books.name': book_name,
        'limit': 3
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

def search_kiwix_all_books(query, books):
    """Search all books and merge results"""
    all_results = []
    
    for book in books:
        print(f"Searching in {book}...")
        results = search_kiwix_single_book(query, book)
        all_results.extend(results)
    
    # Deduplicate by URL path
    seen_urls = set()
    unique_results = []
    
    for result in all_results:
        if result['url_path'] not in seen_urls:
            seen_urls.add(result['url_path'])
            unique_results.append(result)
    
    # Sort by book name
    unique_results.sort(key=lambda x: x['book'])
    
    # Return top 10
    return unique_results[:10]

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

def search(query, book=None, all_books=False):
    """
    Search Kiwix server and return results as a list of dictionaries.
    
    Args:
        query (str): The search query string
        book (str, optional): Specific book to search. If None, searches default book.
        all_books (bool): If True, search all books
    
    Returns:
        list: List of result dictionaries with keys 'title', 'excerpt', 'url_path', 'book'
    """
    # Define the list of books
    books = [
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
    ]
    
    # Perform search based on arguments
    if all_books:
        results = search_kiwix_all_books(query, books)
    elif book:
        results = search_kiwix_single_book(query, book)
    else:
        # Default behavior - search wikipedia
        results = search_kiwix_single_book(query, 'wikipedia_en_all_maxi_2026-02')
    
    return results

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Search Kiwix server')
    parser.add_argument('query', nargs='+', help='Search term(s)')
    parser.add_argument('--book', '-b', help='Specific book to search')
    parser.add_argument('--all', '-a', action='store_true', help='Search all books')
    
    args = parser.parse_args()
    
    # Get search term from command line
    search_term = " ".join(args.query)
    
    # Print search term
    print(f"Searching for: '{search_term}'")
    
    # Call the search function with CLI arguments
    results = search(search_term, book=args.book, all_books=args.all)
    
    # Print results
    print_results(results)

if __name__ == "__main__":
    main()
