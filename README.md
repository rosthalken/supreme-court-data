# supreme-court-data


## Recreating the Supreme Court Dataset

###  Data Collection
There are three opinion text data sources: [Harvard Caselaw Access Project](https://case.law/), the [Supreme Court XML Archive](https://www.supremecourt.gov/xmls/), and [Justia](https://www.justia.com/). The full data can be accessed [here](https://cornell.box.com/s/1awudrm4h0w56jykyauqfnhwg0cnxxzr){:target="_blank"}.

1. Download and parse data from the [Harvard Caselaw Access Project](https://case.law/).  
    `python filter_cases.py`
    - Input: `data.jsonl`
    - Output: `filtered_data.jsonl`

2. Scrape and parse data from the [Supreme Court XML Archive](https://www.supremecourt.gov/xmls/).  
   `python collect_recent_opinions.py`
   - Output: Scraped XML files and `recent_court_data.csv`


3. Scrape missing cases from [Justia](https://www.justia.com/)    
   *Note that missing cases are identified by finding those that exist in SCDB but are missing form our data based on docket numbers and/or US reporter citations.*  
   
   a. Use docket or case citation for missing data to identify URL to scrape.   
   `python create_urls.py` 
   - Input: `missing_data.csv` (CSV file of missing case US reporter citations and docket numbers)  
   - Output: `missing_data.csv` (adds column with URL to scrape from)
  
   b. Scrape missing data from Justia.   
   `python scrape_justia.py`
   - Input: `fixed_urls.csv` (hand-checked version of `missing_data.csv`)
   - Output: `located_data.csv`

4. Consolidate the Caselaw, XML, and Justia data.  
   `python consolidate_data.py`
    - Input files:
      - `filtered_data.jsonl`
      - `recent_court_data.csv`
      - `located_data.csv`
      - Supreme Court Case-Centered Data 
    - Output: `consolidated_data.csv`

5. Organize and clean metadata fields.  
   `python organize_data.py`
   - Input: 
     - Opinion data: `consolidated_data.csv`
     - External metadata:
       - `SCDB_Legacy_07_caseCentered_Citation.csv`
       - `SCDB_2024_01_caseCentered_Citation.csv`
       - `SCDB_2024_01_justiceCentered_Citation.csv`
       - `SCDB_Legacy_07_justiceCentered_Citation.csv`
       - `martin_quinn_justices.csv`
       - `fjc_judges.csv`
       - `HSall_members.csv`
   - Output: `sc_data.csv`




## `reasoning.csv`

- `project_case_id`: Identifier issued for every case for this project. 
- `project_opinion_id`: Identifier issued for every opinion for this project. Identifier begins with `project_case_id` and ends with a number for the opinion number. 
- `source`: Source of the opinion text. For most opinions this is the [Harvard Caselaw Access Project](https://case.law/) (`hclap`), for most opinions after 2014 this is the [Supreme Court Website](https://www.supremecourt.gov/xmls/) (`scg`) and for a small set of cases missing from the prior two sources, this is [Justia](https://www.justia.com/) (`justia`).
- `docket`: Docket number for the case. 
- `citations`: U.S. reporter citation for the case.
  - TODO: change name? 
- `case_url`: URL that holds the specific case text data. 
- `case_name`: Name of the case.
- `date`: Date the case was decided.
- `year`: Year in which  the case was decided. 
- `court_url`: High level URL for the court.
  - TODO: Drop from data?
- `opinion_type`: High-level opinion category, including `majority`, `concurrence`, `per_curiam`, and `dissent`.
- `opinion_text`: Full text of the opinion.
- `zauth`: Lowercased last name of the opinion author. If multiple judges share a last name, a number is appended to the end (e.g. `roberts1` and `roberts2`).
- `author_ids`: TODO FIGURES OUT MAYBE DROP
- `mqJId`: The identifier 
  - TODO: change to "jId"
- `mq`: Dynamic ideology score for the authoring judge in the given year. 
- `cdate`: Date the opinion author joined the Court. 
- `tdate`: Date the opinion author left the Court. 
- `presname`: The opinion author's appointing President's full name. 
- `preslast`: The opinion author's appointing President's lowercased last name.
- `presip`: The opinion author's appointing President's ideology score. 
- `pty`: The opinion author's appointing President's political party (`Republican`, `Democratic`, or `Whig`).
- `repub`: A binary numeric representation of `pty`, where `Republican` = 1; all else is 0.
- `decisionDirection`: Ideological direction of the decision, where 2 = liberal; 1 = conservative; 3 = unspecifiable ([SCDB](http://scdb.wustl.edu/documentation.php?var=decisionDirection)).
- `scdbCaseId`: The case-centered identifier for the Supreme Court Database (listed as `caseId` in SCDB).
- `scdbVoteId`:  The justice-centered identifier for the Supreme Court Database (listed as `voteId` in SCDB).
- `chief`: Chief justice in the given year. 
- `bpnformal`: 
- `zformal`