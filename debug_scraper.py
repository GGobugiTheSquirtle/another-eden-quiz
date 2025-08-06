#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

def debug_scraper():
    url = 'https://anothereden.wiki/w/Characters'
    response = requests.get(url, timeout=30)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    
    char_links = []
    for link in links:
        href = link['href']
        if ('/w/' in href and 
            'Character' not in href and 
            'Special:' not in href and
            'Category:' not in href and
            'Template:' not in href and
            'User:' not in href and
            'Talk:' not in href and
            'Help:' not in href and
            'File:' not in href and
            'MediaWiki:' not in href):
            
            title = link.get('title', '') or link.get_text(strip=True)
            if title and len(title) > 2 and len(title) < 50:
                char_links.append({
                    'title': title,
                    'href': href
                })
    
    # 중복 제거
    unique_chars = []
    seen = set()
    for char in char_links:
        if char['title'] not in seen:
            unique_chars.append(char)
            seen.add(char['title'])
    
    print(f"Found {len(unique_chars)} unique characters")
    for i, char in enumerate(unique_chars[:10]):
        print(f"  {i+1}. {char['title']}")

if __name__ == "__main__":
    debug_scraper() 