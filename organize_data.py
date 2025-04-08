import os
import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup
from collections import Counter
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from thefuzz import process


def normalize_opinion_types(df, column='opinion_type'):
    opinion_dict = {
        'majority': 'majority',
        'dissent': 'dissent',
        'per_curiam': 'per_curiam',
        'concurrence': 'concurrence',
        'concurring-in-part-and-dissenting-in-part': 'concurrence',
        'Per Curiam': 'per_curiam',
        'Statement': 'per_curiam', 
        'Concur and Dissent': 'concurrence',  
        'Opinion of': 'majority',  
        'Concurring in Judgment': 'concurrence',  
        'Opinion': 'majority', 
        'rehearing': 'per_curiam', 
        'Statement of': 'per_curiam', 
        'on-motion-to-strike-cost-bill': 'per_curiam', 
        'plurality': 'majority', 
        'Memorandum': 'per_curiam', 
        'Statement ': 'per_curiam',
    }
    df[column] = df[column].map(opinion_dict).fillna('majority')
    return df

def extract_author_html(html):
    if not isinstance(html, str):
        return None 
    soup = BeautifulSoup(html, 'html.parser')
    first_author = soup.find('author')

    if first_author:
        for tag in first_author.find_all('page-number'):
            tag.extract()
        author = first_author.get_text(strip=True)
    else:
        author = None

    return author


def clean_html_author_names(row):
    if row['source'] == 'hclap':
        author_name = extract_author_html(row['authors_raw'])
    else:
        author_name = row['author_names']
    return author_name


def update_per_curiam_name(row):
    if row['opinion_type'] == 'per_curiam':
        author = 'per_curiam'
    else:
        author = row['author_names']
    return author

def clean_author_names(authors):
    judge_dict ={  "TVT-r.. Justice Bradley, with whom concurred The Chief Justice and Mr. Justice Gray,":"bradley",
                'Mr. Justice Byrnes': 'byrnes',
                 'Me. Justice Claeke': 'clarke',
                 'Me. Justice Clieeoed': 'clifford',
                 'Mr. Justice IIarlan': 'harlan',
                 'By Mr. Chief Justice White.': 'white',
                 'Me. Justice Blatcheoed': 'blatchford',
                 'Mk. Chief Justice Hughes': 'hughes',
                 'By Mr. Justice Hughes.': 'hughes',
                 'Pee Cueiam.': 'per_curiam',
                 'Me. Justice Bkandeis': 'brandeis',
                 'Mr. Justice Blatciiford': 'blatchford',
                 'Mr. Justice Clefeord': 'clifford',
                 'Mr. Justice Swathe': 'swayne',
                 'Me. Justice Blatohfobd': 'blatchford',
                 'Mk. Justice Field': 'field',
                 'Mk. Justice Moody': 'moody',
                 'Justice Auto': 'alito',
                 'Justice White delivered': 'white',
                 'Mr. J ustice Harlan': 'harlan',
                 'Me. Justice Beennan': 'brennan',
                 'Mk. Justice Stone': 'stone',
                 'Me. Justice Maeshall,': 'marshall',
                 'Justice Soutee,': 'souter',
                 'Mr. Justice Blacicmun,': 'blackmun',
                 'Mk. Chief Justice Waite': 'waite',
                 'Me. Justice Beennan,': 'brennan',
                 'The Chiee Justice :': 'chief_justice',
                 'Mr. Justice Bbewer,': 'brewer',
                 'Mb. Justice Stbong': 'strong',
                 'Mk. Justice Roberts': 'roberts',
                 'Me. Justice Beoww,': 'brown',
                 'Mr. Justice Shuras,': 'shiras',
                 'Mr. Justice Beckham,': 'peckham',
                 'Me. Justioe HaelaN': 'harlan',
                 'Mr. Justice G-ray,': 'gray',
                 'Mr. Chief Justice Wa tte': 'waite',
                 'By Mr. Justice Lurton.': 'lurton',
                 'Mr. Justice I)AVIS': 'davis',
                 'Me. Justice Frankfuetee': 'frankfurter',
                 'Mr. Justice Peckiiam,': 'peckham',
                 'The Chiee Justice:': 'chief_justice',
                 'Tiie Chief Justice:': 'chief_justice',
                 'Me. Justice Beckham,': 'peckham',
                 'Per OuriaM.': 'per_curiam',
                 'Mk. Chief Justice Fullee,': 'fuller',
                 'Fuller, C. J.': 'fuller',
                 'Mr. Justice Harían': 'harlan',
                 'Mr. Justice Grat': 'gray',
                 'Fuller, C. J.:': 'fuller',
                 'Mr. Chief Justíce W41TE': 'waite',
                 'Justice Ginsbueg': 'ginsburg',
                 'Mr. Justice Pecrham': 'peckham',
                 'Mb. Justicie Peceham': 'peckham',
                 'Me. Justice Haeean': 'harlan',
                 'Me. Justice Clakk': 'clark',
                 'Mr. Justice Cakdozo': 'cardozo',
                 'Mr. Chief Justice Fueler': 'fuller',
                 'Mr. Justice STEONG': 'strong',
                 'Justice Scaua,': 'scalia',
                 'Me. Justice Haelaé,': 'harlan',
                 'Me. Justice Maeshall': 'marshall',
                 'Mr. Justice Rbhnquist': 'rehnquist',
                 'Mr. Justice White delivered': 'white',
                 'Me. Justice Siiieas,': 'shiras',
                 'Mk. Justice Peckham,': 'peckham',
                 'Mk. Justice Jackson': 'jackson',
                 'Mr. Justice Nehnquist': 'rehnquist',
                 'Mr. Justice Dat': 'day',
                 'Mr. Justice Claeke': 'clarke',
                 'Mk. Justice Field,': 'field',
                 'Me. Justice Bkewer': 'brewer',
                 'Me. Justice Sanfoed': 'sanford',
                 'Mr. Justice Huberts': 'roberts',
                 'Mr. Justice Murpht,': 'murphy',
                 'Me. Justice Foetas,': 'fortas',
                 'Mr. Justice Makshall': 'marshall',
                 'Mr. Justice Bbeweb': 'brewer',
                 'Mr. Chief Justice Taft': 'taft',
                 'Mr. Justice Murpht':'murphy',
                 'Mr. Justice Swavne': 'swayne',
            }
    
    if authors is not None:
        if authors in judge_dict:
            return judge_dict[authors]
        elif authors == "chief_justice":
            return "chief_justice"
        else:
            authors = re.sub(r"Mr\.|Ms\.|Mrs\.|Mu\.|Me |Mr |mr |chief|Mb |delivered the opinion of the court|Circuit|justice|Justice|Chief|,|[0-9]|[*]|[\n]|:|'|[.]", "", authors)
            authors = re.sub(r"mr[.]|ms[.]|mrs[.]|mu[.]|me |mr |chief|mb |deliveredtheopinionofthecourt|delivered the opinion of the court|Circuit|justice|concurring|chief|,|[0-9]|[*]|[\n]|:|'|[.]", "", authors.lower())

            authors = re.sub(r"^ {1,10}", "", authors)

            if ' and ' in authors:
                authors = authors.split(' ')[0]

            authors = re.sub(r"hablan", "harlan", authors)
            authors = re.sub(r"^ {1,10}", "", authors)
            authors = re.sub(r" ", "", authors)
            authors = re.sub(r"o’connor", "o'connor", authors)
            authors = re.sub(r" $", "", authors)
            authors = re.sub(r"mr", "", authors)

            replacements = {
                "robeets": "roberts",
                "roberts": "roberts",
                "chiefroberts": "roberts",
                "phy": "murphy",
                "puller": "fuller",
                "fullee": "fuller",
                "brandéis": "brandeis",
                "beandeis": "brandeis",
                "bbandeis": "brandeis",
                "beown": "brown",
                "bbown": "brown",
                "beewee": "brewer",
                "bbewee": "brewer",
                "beeweb": "brewer",
                "beewer": "brewer",
                "brewee": "brewer",
                "brewerj": "brewer",
                "blatcheord": "blatchford",
                "blatchfoed": "blatchford",
                "blatohford": "blatchford",
                "blatcheobd": "blatchford",
                "blatchfobd": "blatchford",
                "blatoheord": "blatchford",
                "blatohfoed": "blatchford",
                "chiefrehnquist": "rehnquist",
                "geay": "gray",
                "gbay": "gray",
                "geat": "gray",
                "haelan": "harlan",
                "mrharlan": "harlan",
                "millee": "miller",
                "milleb": "miller",
                "mrdouglas": "douglas",
                "douglasdeliveredtheopinionofthecourt": "douglas",
                "shieas": "shiras",
                "shibas": "shiras",
                "shirks": "shiras",
                "-waite": "waite",
                "chieewaite": "waite",
                "•waite": "waite",
                "chibewaite": "waite",
                "justioewaite": "waite",
                "beadley": "bradley",
                "bbadley": "bradley",
                "caedozo": "cardozo",
                "cabdozo": "cardozo",
                "lamae": "lamar",
                "lamab": "lamar",
                "lurton": "lurton",
                "peokham": "peckham",
                "pecicham": "peckham",
                "stewaet": "stewart",
                "vandevantee": "vandevanter",
                "vandevanteb": "vandevanter",
                "butlee": "butler",
                "-holmes": "holmes",
                "mkholmes": "holmes",
                "&alia": "scalia",
                "brennan-": "brennan",
                "brennandeliveredtheopinionofthecourt": "brennan",
                "buegee": "burger",
                "burgee": "burger",
                "eield": "field",
                "clabke": "clarke",
                "clieeord": "clifford",
                "clieeobd": "clifford",
                "mcretnolds": "mcreynolds",
                "oconnor": "o'connor",
                "mkwhite": "white",
                "lueton": "lurton",
                "strong-": "strong",
                "stewakt": "stewart",
                "o’connor": "o'connor",
                "'©bay":"gray"}


            for key, value in replacements.items():
                authors = re.sub(key, value, authors)

            authors = re.sub(r"[[]|[]]|[\"]|[[]|[]]", "", authors)
    else:
        authors = None
    
    return authors

def extract_last_name(text):
    match = re.search(r'(?:Justice|Chief Justice)\s+([A-Z][a-z]+)', text)
    return match.group(1) if match else None

def collect_missing_names(row):
    if row['zauth'] == '':
        name = extract_last_name(row['opinion_text'])
    else:
        name = row['zauth']
    return name

def get_court_data(row):
    if "Supreme Court" in str(row['Court Name (1)']):
        court_num =  "1"
    elif "Supreme Court" in str(row['Court Name (2)']):
        court_num = "2"
    elif "Supreme Court" in str(row['Court Name (3)']):
        court_num = "3"
    else:
        return np.nan
    cdate = row[f'Commission Date ({court_num})']
    tdate = row[f'Termination Date ({court_num})']
    cpty = row[f'Party of Appointing President ({court_num})']
    presname = row[f'Appointing President ({court_num})']
    
    return cdate, tdate, cpty, presname


def load_and_process_judges(judge_path, get_court_data):
    dj = pd.read_csv(judge_path)
    dj = dj[
        dj[['Court Name (1)', 'Court Name (2)', 'Court Name (3)']].apply(
            lambda x: x.str.contains('Supreme Court', na=False)
        ).any(axis=1)
    ]
    dj["zauth"] = dj["Last Name"].str.lower()
    new_rows = []
    for _, row in dj.iterrows():
        cdate, tdate, cpty, presname = get_court_data(row)
        new_rows.append({
            "zauth": row["zauth"],
            "cdate": cdate,
            "tdate": tdate,
            "cpty": cpty,
            "presname": presname
        })
    judge_df = pd.DataFrame(new_rows)
    judge_df["cdate"] = pd.to_numeric(judge_df["cdate"].astype(str).str[:4], errors="coerce")
    judge_df["tdate"] = (
        pd.to_numeric(judge_df["tdate"].astype(str).str[:4], errors="coerce")
        .fillna(9999)
        .astype(int)
    )
    return judge_df

def add_judge_data(big_df, judge_df):
    cdate_l = []
    tdate_l = []
    cpty_l = []
    presname_l = []

    for _, row in big_df.iterrows():
        author = row['zauth']
        year = row['year']
        match_rows = judge_df[
            (judge_df['zauth'] == author) &
            (year >= judge_df['cdate']) &
            (year <= judge_df['tdate'])
        ]

        if match_rows.shape[0] == 0 and author == 'per_curiam':
            cdate_l.append(np.nan)
            tdate_l.append(np.nan)
            cpty_l.append(np.nan)
            presname_l.append(np.nan)
        elif match_rows.shape[0] == 1:
            match = match_rows.iloc[0]
            cdate_l.append(match['cdate'])
            tdate_l.append(match['tdate'])
            cpty_l.append(match['cpty'])
            presname_l.append(match['presname'])
        else:
            cdate_l.append(np.nan)
            tdate_l.append(np.nan)
            cpty_l.append(np.nan)
            presname_l.append(np.nan)

    big_df = big_df.copy()
    big_df['cdate'] = cdate_l
    big_df['tdate'] = tdate_l
    big_df['pty'] = cpty_l
    big_df['presname'] = presname_l

    return big_df

def disambiguate_names(row):
    if row['zauth'] in ["robeets", "roberts", "chiefroberts"]:
        if row['year'] < 2005:
            name = 'roberts1'
        else:
            name = 'roberts2'
    elif row['zauth'] == 'white':
        if row['year'] < 1922:
            name = 'white1'
        else:
            name = 'white2'
    elif row['zauth'] in ["harlan", "haelan", "mrharlan"]:
        if row['year'] < 1912:
            name = 'harlan1'
        else:
            name = 'harlan2'
    elif row['zauth']  == 'jackson':
        if row['year'] < 2000:
            name = 'jackson1'
        else:
            name = 'jackson2'
    elif row['zauth']  == 'percuriam':
        name = 'per_curiam'
    elif row['zauth'] == 'murmurphy':
        name = 'murphy'
    else:
        name = row['zauth']
    return name

def final_name_selection(name, keep_l, threshold=90):
    if name in keep_l:
        return name
    elif name == 'the':
        return "chief_justice"  # don't forget to come back and replace!
    elif name == 'peecuriam':
        return 'per_curiam'
    elif "tooknopart" in name:
        return None
    else:
        result = process.extractOne(name, keep_l)
        if result:
            new_name, score = result
            if score >= threshold:
                return new_name
        return None

def filter_authors(big_df, final_name_selection, count_threshold=15):
    count_df = pd.DataFrame(big_df['zauth'].value_counts()).reset_index()
    count_df.columns = ['zauth', 'count']
    
    keep_l = set(count_df[count_df['count'] > count_threshold]['zauth'].tolist())
    exclude_list = ["the", "peecuriam"]
    keep_l = [l for l in keep_l if l not in exclude_list]
    additional_keep = ["mansfield", "lurton"]
    keep_l.extend(additional_keep)
    
    big_df = big_df.copy()
    big_df['zauth'] = big_df['zauth'].apply(lambda name: final_name_selection(str(name), keep_l))
    
    return big_df

def get_chief_justice(year):
    chief_justices = {
        "Chase": (1864, 1873),
        "Waite": (1874, 1888),
        "Fuller": (1888, 1910),
        "White": (1910, 1921),
        "Taft": (1921, 1930),
        "Stone": (1930, 1946),
        "Vinson": (1946, 1953),
        "Warren": (1953, 1969),
        "Burger": (1969, 1986),
        "Rehnquist": (1986, 2004),
        "Roberts": (2005, None)  
    }

    for chief, (start, end) in chief_justices.items():
        if (start <= year) and (end is None or year <= end):
            return chief
    return None  

def update_chief(row):
    if pd.isna(row["chief"]):
        return get_chief_justice(row["year"])
    else:
        return row["chief"]


def replace_cj(row):
    if row["zauth"] == "chief_justice":
        new_auth = row["chief"].lower()
        if new_auth == "roberts":
            new_auth = "roberts2"
        if new_auth == "white":
            new_auth = "white1"
        if new_auth == "harlan":
            new_auth = "harlan1"
        
    else:
        new_auth = row["zauth"]
    return new_auth

def create_justice_id_dict(legacy_opinion_path, modern_opinion_path, mq_path):
    legacy_opinion_df = pd.read_csv(legacy_opinion_path, low_memory=False)
    modern_opinion_df = pd.read_csv(modern_opinion_path, encoding='ISO-8859-1', low_memory=False)
    scdb_opinion_df = pd.concat([legacy_opinion_df, modern_opinion_df])

    scdb_justice_dict = {}
    for name in set(big_df["zauth"].dropna()):
        for n in set(scdb_opinion_df["justiceName"].dropna()):
            if isinstance(name, str) and name in n.lower():
                scdb_justice_dict[name] = list(set(scdb_opinion_df[scdb_opinion_df["justiceName"] == n]["justice"]))[0]

    mqd = pd.read_csv(mq_path)
    mq_justice_dict = {}

    for name in set(big_df["zauth"].dropna()):
        for n in set(mqd["justiceName"].dropna()):
            if isinstance(name, str) and name in n.lower():
                mq_justice_dict[name] = list(set(mqd[mqd["justiceName"] == n]["justice"]))[0]

    justice_dict = {**mq_justice_dict, **scdb_justice_dict}

    # HARD CODED EXCEPTIONS
    del justice_dict['marshall']
    justice_dict["white1"] = 56
    justice_dict["white2"] = 95

    justice_dict["roberts1"] = 76
    justice_dict["roberts2"] = 111

    justice_dict["o'connor"] = 104
    justice_dict["jackson1"] = 84
    justice_dict["marshall"] = 98

    return justice_dict, mqd

def disambiguate_names(row):
    old_name = row["bioname"]
    fixed_name = row["last"]
    if old_name == "BUSH, George Herbert Walker":
        new_name = "bush1"
    elif old_name == "BUSH, George Walker":
        new_name = "bush2"
        
    elif old_name == "JOHNSON, Andrew":
        new_name = "johnson1"
    elif old_name == "JOHNSON, Lyndon Baines":
        new_name = "johnson2"
        
    elif old_name == "ROOSEVELT, Franklin Delano":
        new_name = "roosevelt2"
    elif old_name == "ROOSEVELT, Theodore":
        new_name = "roosevelt1"
    else:
        new_name = fixed_name
    return new_name
    
def disambiguate_names_2(row):
    cleaned_name = row["preslast"]
    og_name = row["presname"]
    
    if og_name == "George H.W. Bush":
        new_name = "bush1"
    elif og_name == "George W. Bush":
        new_name = "bush2"
        
    elif og_name == "Lyndon B. Johnson":
        new_name = "johnson2"
    elif og_name == "Andrew Johnson":
        new_name = "johnson1"
        
    elif og_name == "Franklin D. Roosevelt":
        new_name = "roosevelt2"
    elif og_name == "Theodore Roosevelt":
        new_name = "roosevelt1"
    else:
        new_name = cleaned_name
    return new_name

def parse_president(big_df, dw_path):
    dw = pd.read_csv(dw_path)
    dw = dw[dw["chamber"]=="President"]
    dw["last"] = dw["bioname"].apply(lambda x: x.split(", ")[0].lower())
    dw["last"] = dw.apply(disambiguate_names, axis = 1)
    big_df["preslast"] = big_df["presname"].apply(lambda x: str(x).split(" ")[-1].lower())
    big_df["preslast"] = big_df.apply(disambiguate_names_2, axis =1)

    dw = dw[["last", "nominate_dim1"]].drop_duplicates()
    dw = dw.rename(columns = {"nominate_dim1":"presip"})
    dw = dw.dropna()

    big_df = big_df.merge(
        dw, 
        how="left", 
        left_on="preslast", 
        right_on="last")
    return big_df

def find_jid_match(row, variable, scdb_opinion_df):
    citation = row["citations"]
    doc_num = row["docket"]
    jid = row["jid"]
    
    match_rows = scdb_opinion_df[scdb_opinion_df['usCite'] == citation]
    
    if match_rows.empty:
        match_rows = scdb_opinion_df[scdb_opinion_df['docket'] == doc_num]
    
    if not match_rows.empty:
        filtered_rows = match_rows[match_rows['scdb_justice'] == jid]
        
        if not filtered_rows.empty:
            return (
                filtered_rows[variable].values[0],
                filtered_rows["voteId"].values[0]
            )
    
    return (np.nan, np.nan)

def merge_scdb_opinion_ids(big_df, legacy_opinion_path, modern_opinion_path):
    legacy_opinion_df = pd.read_csv(legacy_opinion_path, low_memory=False)
    modern_opinion_df = pd.read_csv(modern_opinion_path, encoding='ISO-8859-1', low_memory=False)
    scdb_opinion_df = pd.concat([legacy_opinion_df, modern_opinion_df])
    scdb_opinion_df = scdb_opinion_df.dropna(subset=['voteId'])
    scdb_opinion_df = scdb_opinion_df.rename(columns = {'justice':'scdb_justice'})
    big_df[["vote", "voteId"]] = big_df.apply(
        lambda x: pd.Series(find_jid_match(x, "vote", scdb_opinion_df)),
        axis=1
    )
    opinion_specific_dict = {
        1:"majority",
        2:"dissent",
        3:"regular",
        4:"special",
        5:"judgment",
        6:"dissent_from_denial",
        7:"jurisdictional_dissent",
        8:"justice_participated",

    }
    big_df['spec_opinion_type'] = big_df['vote'].map(opinion_specific_dict)

    return big_df

def drop_header(text):
    text = re.sub(r"^\nMe\.", "\nMr.", text)
    text = re.sub(r"^[^A-Za-z\n]+", "", text)
    text = re.sub(r"^\nMr\.\s*\.", "\nMr.", text)

    sentences = sent_tokenize(text)
    if sentences:  
        first_sentence = sentences[0]
        text = text.replace(first_sentence, "", 1).lstrip()
    return text


# Cleaning: Check for authors who have an opinion issues in a year outside of their years on the court
def fix_incorrect_names(big_df):
    big_df = big_df.copy()
    big_df["cdate_filled"] = big_df.groupby("zauth")["cdate"].transform(lambda x: x.ffill().bfill())
    big_df["tdate_filled"] = big_df.groupby("zauth")["tdate"].transform(lambda x: x.ffill().bfill())

    manual_fixes = {
        'rehnquist': {'tdate_filled': 2005},
        'vandevanter': {'cdate_filled': 1911, 'tdate_filled': 1937},
        'white1': {'tdate_filled': 1921},
        'hughes': {'tdate_filled': 1941},
        'taft': {'cdate_filled': 1921, 'tdate_filled': 1930},
        'stone': {'tdate_filled': 1946},
        'burton': {'tdate_filled': 1958},
    }

    for author, updates in manual_fixes.items():
        for col, val in updates.items():
            big_df.loc[big_df['zauth'] == author, col] = val

    def change_name_if_outlier(row):
        if row["zauth"] == "per_curiam":
            return "per_curiam"
        if row["cdate_filled"] <= row["year"] <= row["tdate_filled"]:
            return row["zauth"]
        return "unknown"

    big_df["zauth"] = big_df.apply(change_name_if_outlier, axis=1)

    return big_df


def drop_row_with_more_nas(group):
    return group.loc[group.isna().sum(axis=1).idxmin()]


def main():
    # Data paths
    data_dir = os.path.join(os.getcwd(), 'data')
    data_path = os.path.join(data_dir, 'consolidated_data.csv')

    # External metadata
    legacy_path = os.path.join(data_dir, 'connected-metadata', 'SCDB_Legacy_07_caseCentered_Citation.csv')
    modern_path = os.path.join(data_dir, 'connected-metadata', 'SCDB_2024_01_caseCentered_Citation.csv')
    legacy_opinion_path = os.path.join(data_dir, 'connected-metadata', 'SCDB_2024_01_justiceCentered_Citation.csv')
    modern_opinion_path = os.path.join(data_dir, 'connected-metadata', 'SCDB_Legacy_07_justiceCentered_Citation.csv')
    mq_path = os.path.join(data_dir, 'connected-metadata', 'martin_quinn_justices.csv')
    judge_path = os.path.join(data_dir, 'connected-metadata', 'fjc_judges.csv')
    dw_path = os.path.join(data_dir, 'connected-metadata', 'HSall_members.csv')

    # Load data
    big_df = pd.read_csv(data_path, low_memory=False)
    big_df = normalize_opinion_types(big_df)
    big_df['author_names'] = big_df.apply(clean_html_author_names, axis = 1)
    big_df['author_names'] = big_df.apply(update_per_curiam_name, axis = 1)
    big_df['zauth'] = big_df['author_names'].apply(clean_author_names)
    big_df['zauth'] = big_df.apply(collect_missing_names, axis = 1)

    # Connect judge metadata
    judge_df = load_and_process_judges(judge_path, get_court_data)
    big_df = add_judge_data(big_df, judge_df)
        
    # Standardize author last names       
    big_df['zauth'] = big_df.apply(disambiguate_names, axis = 1)
    big_df = filter_authors(big_df, final_name_selection)

    # Load in SCDB data
    legacy_df = pd.read_csv(legacy_path, encoding='ISO-8859-1')
    modern_df = pd.read_csv(modern_path)
    keep_cols = ['usCite','decisionDirection', 'majVotes', 'caseId', 'chief']
    scdb_df = pd.concat([legacy_df[keep_cols], modern_df[keep_cols]]).drop_duplicates(subset=keep_cols)
    big_df = big_df.merge(scdb_df, on = 'caseId', how = 'left')
    big_df["chief"] = big_df.apply(update_chief, axis =1)
    big_df["zauth"] = big_df.apply(replace_cj, axis = 1)

    # Connect JIDs
    justice_dict, mqd = create_justice_id_dict(legacy_opinion_path, modern_opinion_path, mq_path)
    big_df["jid"] = big_df["zauth"].map(justice_dict)
    big_df["jid"] = pd.to_numeric(big_df["jid"], errors="coerce").astype("Int64")
    big_df = big_df.fillna({'jid': 0})
    big_df["year"] = pd.to_numeric(big_df["year"], errors="coerce").astype("Int64")

    # Connect MQ Ideology
    mqd = mqd[['justice', 'term', 'post_mn']]
    big_df = big_df.merge(mqd, how = 'left', left_on = ['jid', 'year'], right_on = ['justice', 'term'])
    big_df = big_df.rename(columns = {'post_mn':'mq'})

    # Connect President Ideology
    big_df["repub"] = big_df["pty"].map(lambda x: 1 if x == "Republican" else (0 if x == "Democratic" else None))

    # Parse president
    big_df = parse_president(big_df, dw_path)

    # Add SCDB opinion identifier
    big_df = merge_scdb_opinion_ids(big_df, legacy_opinion_path, modern_opinion_path)

    # ## Opinion length
    big_df["char_len"] = big_df["opinion_text"].apply(lambda x: len(str(x)))
    big_df["word_len"] = big_df["opinion_text"].apply(lambda x: len(x.split(' ')))

    # Drop header
    big_df["opinion_text"] = big_df["opinion_text"].apply(drop_header)

    # Check if zauth was on the court when opinion was issued
    big_df = fix_incorrect_names(big_df)

    # Deduplicate: drop a row that has more NA values
    big_df = big_df.groupby(['case_name', 'opinion_type', 'zauth', 'year', 'opinion_text']).apply(drop_row_with_more_nas).reset_index(drop=True)

    # Reset IDs
    big_df = big_df[(big_df["year"]>1869) & (big_df["year"]<2025)]
    case_urls = list(set(big_df["case_url"].tolist()))
    case_url_dict = {url: idx for idx, url in enumerate(case_urls)}
    big_df['project_case_id'] = big_df["case_url"].map(case_url_dict) 

    big_df['opinion_number'] = big_df.groupby('project_case_id').cumcount()
    big_df['project_opinion_id'] = big_df['project_case_id'].astype(str) + '_' + big_df['opinion_number'].astype(str)
    big_df.drop(columns=['opinion_number'], inplace=True)

    big_df.to_csv(os.path.join(os.getcwd(), 'data', 'sc_data.csv'))


if __name__ == "__main__":
    main()
