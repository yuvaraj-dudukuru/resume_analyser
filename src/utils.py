import re
import pandas as pd
from datetime import datetime

def clean_text_for_excel(text):
    """
    Remove characters that are illegal in Excel cells.
    Ref: https://openpyxl.readthedocs.io/en/stable/api/openpyxl.cell.cell.html
    """
    if not isinstance(text, str):
        return text
        
    # Remove ASCII control characters (0-31) except tab (9), newline (10), carriage return (13)
    illegal_chars = r'[\x00-\x08\x0b\x0c\x0e-\x1f]'
    return re.sub(illegal_chars, '', text)

def clean_dataframe_for_excel(df):
    """
    Apply text cleaning to all string columns in the DataFrame.
    """
    cols = df.select_dtypes(include=['object']).columns
    for col in cols:
        df[col] = df[col].apply(clean_text_for_excel)
    return df

def detect_duplicates(df):
    """
    Detect duplicate candidates by email.
    Keep the one with higher score, mark others as Duplicate.
    """
    if "email" not in df.columns or df.empty:
        return df
        
    # Sort by score descending so we keep the best one
    if "score" in df.columns:
        df = df.sort_values(by="score", ascending=False)
        
    # Create a mask for duplicates
    # keep='first' means the first occurrence (highest score) is NOT a duplicate
    duplicates_mask = df.duplicated(subset=["email"], keep='first')
    
    # We only care about emails that are not empty
    has_email = df["email"].str.len() > 0
    
    # Mark duplicates
    # using loc to avoid SettingWithCopyWarning
    
    # If notes column doesn't exist, create it
    if "notes" not in df.columns:
        df["notes"] = ""
        
    duplicate_rows = duplicates_mask & has_email
    
    if duplicate_rows.any():
        print(f"Detected {duplicate_rows.sum()} duplicate candidates.")
        df.loc[duplicate_rows, "status"] = "Duplicate"
        df.loc[duplicate_rows, "notes"] = df.loc[duplicate_rows, "notes"] + " [Duplicate Email]"
        
    return df

def generate_summary_stats(df):
    """
    Generate dictionary of summary statistics.
    """
    if df.empty:
        return {}
        
    total = len(df)
    
    # Filter out Duplicates/Errors for accurate stats? 
    # Or count them separately. Let's count valid candidates.
    valid_df = df[~df["status"].isin(["Duplicate", "Error"])]
    
    stats = {
        "Total processed": total,
        "Valid Candidates": len(valid_df),
        "Green": len(df[df["status"] == "Green"]),
        "Yellow": len(df[df["status"] == "Yellow"]),
        "Red": len(df[df["status"] == "Red"]),
        "Avg Score": df["score"].mean() if "score" in df.columns else 0,
        "Duplicates": len(df[df["status"] == "Duplicate"]),
        "Errors": len(df[df["status"] == "Error"])
    }
    
    return stats
