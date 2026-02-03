import csv
import json
import re
from collections import defaultdict

csv_path = r'c:\Users\ajays\OneDrive\Desktop\BD-CodeDump\HTML\Untitled spreadsheet - Sheet3.csv'

# Dictionary to store list of articles for each source
# Structure: { "Source": [ {"article": "...", "content": "..."} ] }
source_data = defaultdict(list)

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader) # Skip header
    # Header: Article, Content / Feature, Source / Borrowed From
    
    for row in reader:
        if len(row) < 3:
            continue
            
        article_num = row[0]
        content = row[1]
        source_text = row[2]
        
        if not source_text or source_text.strip() == 'N/A':
            continue
            
        # Clean and split sources similar to previous logic
        cleaned_text = re.sub(r'\(.*?\)', '', source_text)
        sources = cleaned_text.split(',')
        
        for source in sources:
            source = source.strip()
            if source:
                source_data[source].append({
                    "article": article_num,
                    "content": content
                })

print(json.dumps(source_data, indent=2))
