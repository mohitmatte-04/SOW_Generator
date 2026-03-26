import json
import sys

def extract_text_from_elements(elements):
    text = ""
    for elem in elements:
        if elem.get('type') == 'shape':
            for content_item in elem.get('content', []):
                if 'text' in content_item:
                    text += content_item['text'] + "\n"
                if 'children' in content_item:
                    for child in content_item['children']:
                        if 'text' in child:
                            text += child['text'] + "\n"
        elif elem.get('type') == 'table':
            for row in elem.get('content', []):
                for cell in row:
                    for content_item in cell:
                        if 'text' in content_item:
                            text += content_item['text'] + "\n"
    return text

def main():
    try:
        with open('presentation.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"data loaded {data}")
        
        slides = data.get('slides', [])
        for i, slide in enumerate(slides):
            print(f"--- Slide {i+1} ---")
            elements = slide.get('elements', [])
            text = extract_text_from_elements(elements)
            print(text.strip())
            print("\n")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
