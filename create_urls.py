import pandas as pd
import os
import numpy as np
import roman
from roman import InvalidRomanNumeralError

df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'missing_data.csv'))
def change_roman_nums(cite):
    split_cite = str(cite).split(" U.S. ")
    if len(split_cite)>1:
        if not any(i.isdigit() for i in split_cite[1]):
            try:
                arabic = roman.fromRoman(split_cite[1])
                new_cite = f"{split_cite[0]} U.S. {arabic}"
                return new_cite
            except InvalidRomanNumeralError:

                return f"{cite} (Invalid Roman Numeral)"
        else:
            return cite
    else:
        return cite

def create_link(row):
    citation = row["cleaned_usCite"]
    docket = row["docket"]

    if not pd.isna(citation):
        split_cite = citation.split(" U.S. ")
        if any(i.isdigit() for i in split_cite[1]):
            url = f"https://supreme.justia.com/cases/federal/us/{split_cite[0]}/{split_cite[1]}/"
        else:
            print(citation)
            url = "unknown"
    elif pd.isna(citation) or pd.isna(docket): 
        url = "unknown"
    
    else:
        citation_volume = str(citation).split(" ")[0]
        url = f"https://supreme.justia.com/cases/federal/us/{citation_volume}/{docket}/"
    return url

df["cleaned_usCite"] = df["usCite"].apply(change_roman_nums)
df["url"] = df.apply(create_link, axis = 1)
df.to_csv(os.path.join(os.getcwd(), 'data', 'missing_data.csv'))
