import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import time
import random
from tqdm import tqdm
import numpy as np

def get_case_meta(url):
    title = np.nan
    citation = np.nan
    year = np.nan
    decided_date = np.nan
    docket_num = np.nan
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    heading = soup.title.text.split(" | ")
    if len(heading) >= 2:
        title = heading[0].strip()
        if "(" in heading[1] and ")" in heading[1]:
            citation = heading[1].split("(")[0].strip()
            year = heading[1].split("(")[1].split(")")[0].strip()
        else:
            citation = heading[1].strip()
            if citation == "Justia U.S. Supreme Court Center":
                citation = np.nan
            year = np.nan
    else:
        title = heading[0].strip()
        citation = np.nan
        year = np.nan


    case_details = soup.find('div', class_='case-details')
    for div in case_details.find_all('div', class_='flex-col'):
        strong = div.find('strong')
        if strong and strong.text.strip() == 'Decided:':
            decided_date = div.find('span').text.strip()
        elif strong and strong.text.strip() == "Docket No.":
            docket_num =  div.find('span').text.strip()
    
    return decided_date, docket_num, title, citation, year

def get_main_opinion_page(url):
    url = url+"#opinions"
    response = requests.get(url)
    response.raise_for_status()  
    soup = BeautifulSoup(response.text, "html.parser")
    opinion_links = soup.select("ul#opinions-list a")
    return opinion_links, soup

def collect_opinion_text(soup, opinion_id):
    opinion_div = soup.find("div", {"id": f"tab-opinion-{opinion_id}"})
    text = BeautifulSoup(str(opinion_div).split('<div class="opinion-footnotes">')[0]).text
    text = replace_single_newlines(text)
    pattern = r'delivered the opinion of the Court'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        pre_match_text = text[:match.start()]
        last_tab_index = pre_match_text.rfind('\t')
        start_index = last_tab_index + 1 if last_tab_index != -1 else match.start()
        extracted_text = text[start_index:].strip()
    else:
        extracted_text = text
    return extracted_text

def replace_single_newlines(text):
    return re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

def collect_old_opinion_text(soup, opinion_id):
    opinion_div = soup.find("div", {"id": f"tab-opinion-{opinion_id}"})
    text = opinion_div.text
    text = replace_single_newlines(text)
    pattern = r'delivered the opinion of the Court'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        pre_match_text = text[:match.start()]
        last_tab_index = pre_match_text.rfind('\t')
        start_index = last_tab_index + 1 if last_tab_index != -1 else match.start()
        extracted_text = text[start_index:].strip()
        match = re.search(r'JUSTICE\s+([A-Z]+)', text)
        if match:
            author = match.group(1)
        else:
            author = np.nan
    else:
        match = re.search(r'\t+\s*([A-Z]+),\s+(?:C\.\s+J\.|J\.)\s*\n\t+(.*)', text, re.DOTALL)
        if match:
            author = match.group(1)
            extracted_text = match.group(2).strip()

        else:
            extracted_text = text
            author = np.nan


    return extracted_text, author

def parse_opinion(opinion):
    opinion_type = np.nan
    author = np.nan
    opinion_text = np.nan
    opinion_id = opinion["id"].replace("link-opinion-", "")
    opinion_link_text = opinion.text
    if opinion_link_text == "Opinions & Dissents":
        opinion_type = "majority"
        opinion_text, author = collect_old_opinion_text(soup, opinion_id)
    else:
        if opinion_link_text == "Per Curiam":
            opinion_type = "per_curiam"
            author = "per_curiam"
        else:
            match = re.match(r"(.+?)\s*\((.+)\)", opinion_link_text)
            if match:
                opinion_type = match.group(1).strip()
                author = match.group(2).strip()
        opinion_text = collect_opinion_text(soup, opinion_id)

    return opinion_type, author, opinion_text

def clean_opinion_text(text):
    cleaned = re.sub(r'\n\s*\[\w+ \d{1,2}, \d{4}\]\s*\n+', '\n', text)
    cleaned = cleaned.strip()
    return cleaned

def extract_author(row):
    current_author = row["author_names"]
    opinion_text = row["opinion_text"]
    if pd.notna(current_author):
        return current_author
    if re.search(r'\bCHIEF JUSTICE\b', opinion_text):
        return "chief_justice"
    if re.search(r'\bPER CURIAM\b', opinion_text):
        return "per_curiam"

    match = re.search(r'Justice\s+([A-Z][a-zA-Z\-\'\.]+)\s+delivered the opinion', opinion_text)
    if match:
        return match.group(1)
    return "per_curiam"

def main():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'fixed_urls.csv'))
    df = df[['usCite', 'docket', 'caseId', 'correct_url']].dropna(subset="correct_url")

    case_data = []
    urls = df["correct_url"].tolist()
    for url in tqdm(urls, desc="Processing cases"):
        decided_date, docket_num, title, citation, year = get_case_meta(url)
        time.sleep(random.uniform(1.5, 3.5))

        opinion_links, soup = get_main_opinion_page(url)
        for opinion in opinion_links:
            opinion_type, author, opinion_text = parse_opinion(opinion)
            case_data.append({
                "source":"justia",
                "collected_docket":docket_num,
                "collected_cite":citation,
                "case_url":url,
                "case_name":title,
                "date":decided_date,
                "year":year,
                "opinion_type":opinion_type,
                "opinion_text":opinion_text,
                "author_names":author,
            })
            time.sleep(random.uniform(2, 4))
    collected_df = pd.DataFrame(case_data)

    collected_df["opinion_type"] = collected_df["opinion_type"].str.lower()
    collected_df["opinion_type"] = collected_df["opinion_type"].replace("opinion", "majority")
    collected_df["opinion_text"] = collected_df["opinion_text"].apply(clean_opinion_text)
    merged_df = collected_df.merge(df, right_on="correct_url", left_on="case_url", how="left")
    merged_df["docket"] = merged_df["docket"].fillna(merged_df["collected_docket"])
    merged_df["usCite"] = merged_df["usCite"].fillna(merged_df["collected_cite"])

    merged_df["authors_raw"] = None
    merged_df["case_id"] = None
    merged_df["author_ids"] = None

    merged_df = merged_df.rename(columns = {"usCite":"citations","correct_url":"court_url"})
    merged_df["author_names"] = merged_df.apply(extract_author, axis = 1)

    merged_df = merged_df[['case_name', 'citations', 'court_url', 'docket', 'opinion_type',
        'author_names', 'opinion_text', 'source', 'case_url', 'authors_raw',
        'case_id', 'author_ids', 'date', 'year', 'caseId']]

    merged_df.to_csv(os.path.join(os.getcwd(), 'data', 'located_data.csv'))

if __name__ == "__main__":
    main()
