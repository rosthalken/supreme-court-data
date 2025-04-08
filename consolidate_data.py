# %%
import os
import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup
from collections import Counter
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from bs4 import BeautifulSoup
from thefuzz import process
from collections import defaultdict

def parse_json(data):
    case_l = []
    for case in data:
        case = json.loads(case)

        case_id = case["id"]
        case_url = case["url"]
        case_name = case["name"]
        date = case["decision_date"]
        court_url = case["court"]["url"]
        citation = case["citations"]
        docket = case["docket_number"]

        soup = BeautifulSoup(case["casebody"]["data"], "html.parser")
        opinions = soup.find_all("opinion") 

        for opinion in opinions:
            opinion_type = opinion["type"]
            opinion_text = opinion.text
            author_names = []
            author_ids = []
            authors = opinion.find_all("author")

            for author in authors:
                author_name = author.text
                author_id = author["id"]
                author_names.append(author_name)
                author_ids.append(author_id)
            
            authors = "".join([str(author) for author in authors])
            author_names = " ".join(author_names)
            author_ids = " ".join(author_ids)

            opinion_dict = {   
                "source": "hclap",
                "docket": docket,
                "case_id":case_id,
                "case_url":case_url,
                "case_name":case_name,
                "citations": citation,
                "date":date,
                "court_url":court_url,
                "opinion_type":opinion_type,
                "opinion_text":opinion_text,
                "authors_raw":authors,
                "author_names":author_names,
                "author_ids":author_ids
            }

            case_l.append(opinion_dict)
    return case_l


def parse_date(date_str):
    try:
        return pd.to_datetime(date_str, format="%Y-%m-%d", errors='raise')
    except ValueError:
        try:
            return pd.to_datetime(date_str, format="%B %d, %Y", errors='raise')
        except ValueError:
            try:
                return pd.to_datetime(date_str, format="%Y-%m", errors='raise') 
            except ValueError:
                try:
                    return pd.to_datetime(date_str, format="%Y", errors='raise')
                except ValueError:
                    return pd.NaT 
                
def get_official_cite(row):
    # for older cases
    citation = [cite['cite'] for cite in row["citations"] if cite['type'] == 'official'][0]
    return citation

def format_citation(row):
    # for newer cases
    citation = row["citations"]
    match = re.search(r'(\d+)\s+U\.?\s*S\.?\s*(_{2,}|\d+)', citation)
    if match:
        volume, page = match.groups()
        return f"{volume} U.S. {page}"
    
    return "Invalid citation format"

def update_percuriam(row):
    if row['opinion_type'] == 'majority':
        if "per curiam" in row["opinion_text"][:100].lower():
            opinion_type = "per_curiam"
        else:
            opinion_type = 'majority'
    else:
        opinion_type = row['opinion_type']
    return opinion_type

def clean_scraped_text(row):
    text = re.sub(r"NOTICE:.*?press\.\s*", "", row["opinion_text"], flags=re.DOTALL)
    text = re.sub(r"NOTICE:.*?errors\.\s*", "", text, flags=re.DOTALL)
    return text

def load_scdb(legacy_path, modern_path):
    legacy_df = pd.read_csv(legacy_path, encoding='ISO-8859-1')
    modern_df = pd.read_csv(modern_path)
    scdb_df = pd.concat([legacy_df, modern_df])
    scdb_df['year'] = pd.to_datetime(scdb_df['dateDecision']).dt.year
    scdb_df = scdb_df[scdb_df['year']>=1870]
    return scdb_df


def compare_scdb(scdb_df, big_df):

    scdb_data = scdb_df[['usCite', 'docket', 'caseId', 'year']].to_dict(orient='records')
    opinion_data = big_df[['citations', 'docket', 'index', 'scdbCaseId']].to_dict(orient='records')

    cite_dict = defaultdict(list)
    docket_dict = defaultdict(list)
    case_dict = defaultdict(list)

    for row in opinion_data:
        if pd.notna(row.get("citations")):
            cite_dict[row["citations"]].append(row)
        if pd.notna(row.get("docket")):
            docket_dict[row["docket"]].append(row)
        if pd.notna(row.get("scdbCaseId")):
            case_dict[row["scdbCaseId"]].append(row)

    merged_data = []

    for row in scdb_data:
        usCite = row.get("usCite")
        docket = row.get("docket")
        caseId = row.get("caseId")

        matched_rows = []
        match_type = "none"

        if pd.notna(caseId) and caseId in case_dict:
            matched_rows = case_dict[caseId]
            match_type = "caseId"
        elif pd.notna(usCite) and usCite in cite_dict:
            matched_rows = cite_dict[usCite]
            match_type = "usCite"
        elif pd.notna(docket) and docket in docket_dict:
            matched_rows = docket_dict[docket]
            match_type = "docket"
        
        if matched_rows:
            for match in matched_rows:
                merged_data.append({**row, **match, "match_type": match_type})
        else:
            merged_data.append({**row, "match_type": "none"})

    merged_df = pd.DataFrame(merged_data).dropna(subset = "index")
    keep_idxs = merged_df["index"].tolist()

    big_df = big_df[big_df["index"].isin(keep_idxs)]
    add_cols = merged_df[["index", "caseId"]]
    big_df = big_df.merge(add_cols, on = "index").drop(columns = ["scdbCaseId", "index"])

    return big_df


def main():

    data_dir = os.path.join(os.getcwd(), 'data')
    json_path = os.path.join(data_dir, 'filtered_data.jsonl')
    recent_court_path = os.path.join(data_dir, 'recent_court_data.csv')
    missing_path = os.path.join(data_dir, 'located_data.csv')
    legacy_path = os.path.join(data_dir, 'connected-metadata', 'SCDB_Legacy_07_caseCentered_Citation.csv')
    modern_path = os.path.join(data_dir, 'connected-metadata', 'SCDB_2024_01_caseCentered_Citation.csv')

    # Parse Data (1870 to 2014)
    data = []
    with open(json_path, 'r') as f:
        for line in f:
            data.append(line)
    case_l = parse_json(data)
    df = pd.DataFrame(case_l)        
    df['date'] = df['date'].apply(parse_date)
    df['year'] = df['date'].dt.year
    df["citations"] = df.apply(get_official_cite, axis = 1)
    df["opinion_type"] = df.apply(update_percuriam, axis = 1)
    df = df[df['year']<2014]
    df["caseId"] = None


    # Parse Recent Cases (2014-2024)
    new_df = pd.read_csv(recent_court_path).drop(columns = 'Unnamed: 0')
    new_df["citations"] = new_df.apply(format_citation, axis = 1)
    new_df["opinion_text"] = new_df.apply(clean_scraped_text, axis = 1)
    new_df['date'] = new_df['date'].apply(parse_date)
    new_df['year'] = new_df['date'].dt.year
    new_df = new_df[new_df['year']>=2014]
    new_df["caseId"] = None

    # Load Missing Cases
    missing_df = pd.read_csv(missing_path).drop(columns = "Unnamed: 0")

    # Combine Data
    big_df = pd.concat([df, new_df, missing_df])
    big_df = big_df.reset_index(drop = True)
    big_df = big_df[~big_df["case_name"].isna()]
    big_df = big_df.rename(columns = {"caseId":"scdbCaseId"})
    big_df = big_df.reset_index()

    # Drop cases that we collect but that are not in SCDB
    scdb_df = load_scdb(legacy_path, modern_path)
    big_df = compare_scdb(scdb_df, big_df)

    big_df.to_csv(os.path.join(data_dir, 'consolidated_data.csv'))


if __name__ == "__main__":
    main()
