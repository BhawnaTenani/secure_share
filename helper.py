def reverse_token(text):
    return text[::-1]  # Just a simple reversible "encryption"

def allowed_file(filename):
    return filename.endswith(('.pptx', '.docx', '.xlsx'))
