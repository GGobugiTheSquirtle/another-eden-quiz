import requests
from bs4 import BeautifulSoup

# 다른 캐릭터들도 확인해보기
test_urls = [
    'https://anothereden.wiki/w/Aldo',
    'https://anothereden.wiki/w/Feinne',
    'https://anothereden.wiki/w/Amy',
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for url in test_urls:
    char_name = url.split('/')[-1]
    print(f'\n=== {char_name} ===')
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        tables = soup.find_all('table', class_=['anotherTable', 'wikitable', 'infobox'])
        
        icon_count = 0
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            
            for row_idx, row in enumerate(rows):
                cells = row.find_all(['th', 'td'])
                
                if len(cells) >= 3:
                    element_equipment_cell = cells[2]
                    ee_icon_tags = element_equipment_cell.find_all('img')
                    
                    if ee_icon_tags:
                        for img in ee_icon_tags:
                            src = img.get('src', '')
                            alt = img.get('alt', '')
                            filename = src.split('/')[-1] if '/' in src else src
                            print(f'  파일명: {filename}')
                            print(f'  ALT: "{alt}"')
                            icon_count += 1
                            if icon_count >= 5:  # 너무 많으면 5개만
                                break
                    if icon_count >= 5:
                        break
                if icon_count >= 5:
                    break
            if icon_count >= 5:
                break

    except Exception as e:
        print(f'오류: {e}') 