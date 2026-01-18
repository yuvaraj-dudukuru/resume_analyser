import re

def clean_text_for_excel(text):
    """
    Remove characters that are illegal in Excel cells.
    Ref: https://openpyxl.readthedocs.io/en/stable/api/openpyxl.cell.cell.html
    """
    if not isinstance(text, str):
        return text
        
    # Remove ASCII control characters (0-31) except tab (9), newline (10), carriage return (13)
    # Also removing 11 (vertical tab) and 12 (form feed) explicitly if they slip through
    # \x00-\x08 is 0-8
    # \x0b is 11 (VT)
    # \x0c is 12 (FF)
    # \x0e-\x1f is 14-31
    illegal_chars = r'[\x00-\x08\x0b\x0c\x0e-\x1f]'
    
    return re.sub(illegal_chars, '', text)

def clean_dataframe_for_excel(df):
    """
    Apply text cleaning to all string columns in the DataFrame.
    """
    # Select object (string) columns
    cols = df.select_dtypes(include=['object']).columns
    for col in cols:
        df[col] = df[col].apply(clean_text_for_excel)
    return df
