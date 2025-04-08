import pandas as pd
import os 
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
from datetime import datetime

def scrape_page(url):
    sc_results = requests.get(url)
    html = sc_results.text
    page = BeautifulSoup(html, "html.parser")
    return page

def collect_good_links(page):
    table = page.find("pre")
    table_l = list(table.stripped_strings)[1:]

    time_l = []
    link_l = []
    for i, element in enumerate(table_l):
        if i % 2 == 0:
            time_l.append(element)
        else:
            link_l.append(element)
    good_links = []
    for link in link_l:
        if link.endswith("xml"):
            good_links.append(link)
        else:
            print(f"{link} omitted because not xml.")

    return good_links

def get_opinion_data(good_links, xml_path):
    dir = "https://www.supremecourt.gov/xmls/archive/"
    for link in good_links:
        full_link = dir+link
        r = requests.get(full_link)  
        with open(os.path.join(xml_path, link), 'wb') as f:
            f.write(r.content)

def parse_data(xml_path):
    json_l = []
    for file in os.listdir(xml_path):
        alpha_char = any([char.isalpha() for char in file.split(".")[0]])
        if alpha_char:
            continue
        else: 
            path = os.path.join(xml_path, file)
            with open(path, 'rb') as f:
                case_xml = f.read()
            soup = BeautifulSoup(case_xml)

            case_names = soup.find_all("p", {"style":"SYLCT-A"})
            if len(case_names) > 0:
                case_name = case_names[0].text
            else:
                case_name = "NA"

            citations = soup.find_all("p",  {"style":"Header--Citeas"})
            if len(citations) > 0:
                citation = citations[0].text
            else:
                citation = "NA"

            numbers = soup.find_all("p",  {"style":"CaseNumber"})
            if len(numbers) > 0:
                number = numbers[0].text
            else:
                number = "NA"
            documents = soup.find_all("document")

            for doc in documents:
                if doc.find("p", {"style": "Header--Disposition"}) is not None:
                    if doc.find("p", {"style": "Header--Disposition"}).text == "Syllabus":
                        continue
                    else:
                        type = doc.find("p", {"style": "Header--Disposition"}).text
                        casenum = doc["casenumber"]
                        
                        opinion_type = doc["disposition"]
                        if opinion_type != "Per Curiam":
                            try:
                                author = doc["chamber"]
                            except KeyError:
                                author = doc["chambers"]
                        else:
                            author = opinion_type


                        dates = doc.find_all("p",  {"style":"DateCode"})
                        if len(dates) > 0:
                            date = dates[0].text
                        else:
                            date = "NA"
            
                        if doc.find("body"):
                            opinion_l = [para.text for para in doc.find("body").find_all("p", {"jy":"both"})]
                        else:
                            opinion_l = [para.text for para in doc.find_all("p", {"jy":"both"})]
                        opinion_dict = {
                            "case_name": case_name,
                            "citations": citation,
                            "date": date,
                            "court_url": "https://www.supremecourt.gov/",
                            "docket": casenum,
                            "opinion_type": opinion_type,
                            "author_names": author,
                            "opinion_text": opinion_l,
                            "source": "scg",
                            "case_url": f"https://www.supremecourt.gov/xmls/archive/{file}",
                            "authors_raw":"na",
                            "case_id":"na",
                            "author_ids":"na"
    
                        }

                        json_l.append(opinion_dict)
    return json_l

def rename_opinions(cell):
    rename_dict = {
        "Dissent":"dissent",
        "Opinion of the Court":"majority",
        "Concur": "concurrence",
    }
    if cell in rename_dict:
        opinion_type = rename_dict[cell]
    else:
        opinion_type = cell
    return opinion_type

def convert_date(datetime_str):
    try:
        if len(datetime_str) < 4:
            new_date = datetime_str
        else:
            if "Decided" in datetime_str:
                datetime_str = datetime_str.split("Decided ")[1]
            datetime_str = datetime_str.strip()
            datetime_str = datetime_str.strip("[]")
            datetime_str = datetime_str.strip("()")
            date_object = datetime.strptime(datetime_str, '%B %d, %Y')
            new_date = date_object.strftime('%Y-%m-%d')
    except ValueError:
        new_date = datetime_str

    return new_date

def main():
    url = "https://www.supremecourt.gov/xmls/archive"

    data_path = os.path.join(os.getcwd(), 'data')
    xml_path = os.path.join(data_path, 'xml-files')
    out_path = os.path.join(data_path, 'recent_court_data.csv')

    if not os.path.exists(xml_path):
        os.makedirs(xml_path)

    page = scrape_page(url)
    good_links = collect_good_links(page)
    get_opinion_data(good_links, xml_path)
    json_l = parse_data(xml_path)
    df = pd.DataFrame(json_l)

    df["opinion_type"] = df["opinion_type"].apply(rename_opinions)
    df = df.rename(columns={"date":"unformatted_date"})
    df["date"] = df["unformatted_date"].apply(convert_date)
    df = df.drop(columns="unformatted_date")
    df["opinion_text"] = df["opinion_text"].apply(lambda x: '\n\n'.join(x))
    df = df.drop_duplicates()
    df.to_csv(out_path)

if __name__ == "__main__":
    main()
