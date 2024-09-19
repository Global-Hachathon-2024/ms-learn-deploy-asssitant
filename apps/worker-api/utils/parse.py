import re

def extract_code_blocks(text):
    code_block_pattern = re.compile(r'```(main\.bicep|main\.parameters\.json)\n(.*?)\n```', re.DOTALL)
    matches = code_block_pattern.findall(text)

    extracted_files = {}
    for filename, code in matches:
        # Duplicate filenames may occur but will be overwritten
        extracted_files[filename] = code

    return extracted_files

def convert_to_en_us_url(url):
    converted_url = re.sub(r'(https://learn\.microsoft\.com/)([^/]+/)', r'\1en-us/', url)
    return converted_url