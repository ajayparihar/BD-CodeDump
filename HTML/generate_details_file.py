import csv
import json
import re
from collections import defaultdict

csv_path = r'c:\Users\ajays\OneDrive\Desktop\BD-CodeDump\HTML\Untitled spreadsheet - Sheet3.csv'
output_path = r'c:\Users\ajays\OneDrive\Desktop\BD-CodeDump\HTML\source_details.json'

source_data = defaultdict(list)

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    for row in reader:
        if len(row) < 3:
            continue
            
        article_num = row[0]
        content = row[1]
        source_text = row[2]
        
        if not source_text or source_text.strip() == 'N/A':
            continue
            
        cleaned_text = re.sub(r'\(.*?\)', '', source_text)
        sources = cleaned_text.split(',')
        
        for source in sources:
            source = source.strip()
            if source:
                source_data[source].append({
                    "article": article_num,
                    "content": content
                })

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(source_data, f, indent=2)

print(f"Data written to {output_path}")
