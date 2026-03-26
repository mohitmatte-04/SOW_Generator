import json

def extract_text(element):
    text = ""
    if 'paragraph' in element:
        for p_elem in element['paragraph'].get('elements', []):
            if 'textRun' in p_elem:
                text += p_elem['textRun'].get('content', '')
    elif 'table' in element:
        for row in element['table'].get('tableRows', []):
            for cell in row.get('tableCells', []):
                for nested_elem in cell.get('content', []):
                    text += extract_text(nested_elem)
    return text

def main():
    try:
        with open('template.json', 'r') as f:
            data = json.load(f)
        
        full_text = ""
        for elem in data.get('body', {}).get('content', []):
            full_text += extract_text(elem)
            
        with open('template_text.txt', 'w') as f:
            f.write(full_text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
