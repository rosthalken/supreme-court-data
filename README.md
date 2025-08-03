# supreme-court-data


## Recreating the U.S. Supreme Court Opinion Dataset (1870-2024)

This repo contains code to recreate the following datasets:
- [Dataset of U.S. Supreme Court opinions issued between 1870-2024](https://cornell.box.com/s/1awudrm4h0w56jykyauqfnhwg0cnxxzr)
- [Opinion-level formal scores for opinions issued between 1870-2024](https://cornell.box.com/s/w30qci4sq95tj9gr5tegx6radifqv825)

###  Data Collection
There are three opinion text data sources: [Harvard Caselaw Access Project](https://case.law/), the [Supreme Court XML Archive](https://www.supremecourt.gov/xmls/), and [Justia](https://www.justia.com/). **The final dataset can be accessed [here](https://cornell.box.com/s/1awudrm4h0w56jykyauqfnhwg0cnxxzr)**. Note that a small set of 97 cases were not collected even through the Justia scraping step. A list of these cases and their citations are [here](https://cornell.box.com/s/db29c1zlc2xxdj9hfgv6k8h2m42iv7h3). 

1. **Download and parse data from the [Harvard Caselaw Access Project](https://case.law/)**  
    `python filter_cases.py`
    - Input: `data.jsonl`
    - Output: `filtered_data.jsonl`

2. **Scrape and parse data from the [Supreme Court XML Archive](https://www.supremecourt.gov/xmls/)**  
   `python collect_recent_opinions.py`
   - Output: Scraped XML files and `recent_court_data.csv`


3. **Scrape missing cases from [Justia](https://www.justia.com/)**   
   *Note that missing cases are identified by finding those that exist in SCDB, but are missing from our data (based on docket numbers and/or US reporter citations).*  
   
   a. Create likely Justia case URL   
   `python create_urls.py` 
   - Input: `missing_data.csv` (CSV file of missing case US Reporter citations and docket numbers)  
   - Output: `missing_data.csv` (adds column with URL to scrape)
  
   b. Scrape missing data from Justia   
   `python scrape_justia.py`
   - Input: `fixed_urls.csv` (hand-checked version of `missing_data.csv`)
   - Output: `located_data.csv`

4. **Consolidate the Caselaw, XML, and Justia data**  
   `python consolidate_data.py`
    - Input files:
      - `filtered_data.jsonl`
      - `recent_court_data.csv`
      - `located_data.csv`
      - Supreme Court Case-Centered Data 
    - Output: `consolidated_data.csv`

5. **Organize and clean metadata fields**  
   `python organize_data.py`
   - Input: 
     - Opinion data: `consolidated_data.csv`
     - External metadata:
       - [`SCDB_Legacy_07_caseCentered_Citation.csv`](http://scdb.wustl.edu/data.php?s=6#:~:text=in%20the%20future.-,Case%20Centered%20Data,-Total%20Rows%20%3A%2019%2C861)
       - [`SCDB_2024_01_caseCentered_Citation.csv`](http://scdb.wustl.edu/data.php?s=1#:~:text=The%20SCDB.-,Case%20Centered%20Data,-Total%20Rows%20%3A%2013%2C928)
       - [`SCDB_2024_01_justiceCentered_Citation.csv`](http://scdb.wustl.edu/data.php?s=1#:~:text=hide%20file%20sets-,Justice%20Centered%20Data,-Total%20Rows%20%3A%20124%2C770)
       - [`SCDB_Legacy_07_justiceCentered_Citation.csv`](http://scdb.wustl.edu/data.php?s=6#:~:text=hide%20download%20options-,Justice%20Centered%20Data,-Total%20Rows%20%3A%20172%2C213)
       - [`martin_quinn_justices.csv`](http://mqscores.wustl.edu/media/2022/justices.csv)
       - `fjc_judges.csv`
       - `HSall_members.csv`
   - Output: `sc_data.csv`


###  Legal Reasoning Measurement  
The code in `lr-measurement/` takes the collected U.S. Supreme Court data and measures formalism at the opinion level. **The final dataset can be accessed [here](https://cornell.box.com/s/w30qci4sq95tj9gr5tegx6radifqv825)**. The expert-annotated dataset is [here](https://drive.google.com/file/d/1i7dcshwcgCBF3TVLbNBC-Hutw8qVreTq/view?usp=sharing). 

1. **Prepare data for predictions**  
   `python lr-measurement/1_prep_predictions.py`
   - Input: `sc_data.csv`
   - Output: `data_for_predictions.csv`

2. **Predict with fine-tuned model**  
    `python lr-measurement/2_predictions.py`
    - Input: 
      - `data_for_predictions.csv`
      - Fine-tuned model, available for download [here](https://huggingface.co/rosamondthalken/legal-reasoning).
    - Output: `raw_output`, `combined_output`, `combined_output.csv`

3. **Reorganize prediction output**  
    `python lr-measurement/3_split_predictions.py`
    - Input: `combined_output.csv`
    - Output: `metadata.csv`, `predictions.csv`

4. **Calculate formal measurements**  
   `python lr-measurement/4_measure_formal.py`
   - Input: `metadata.csv`, `predictions.csv`
   - Output: `reasoning.csv`
   

## Metadata Fields
The following is a description of all fields in the [`reasoning.csv`](https://cornell.box.com/s/w30qci4sq95tj9gr5tegx6radifqv825) data:  

- `project_case_id`: Identifier issued for every case for this project. 
- `project_opinion_id`: Identifier issued for every opinion for this project. Identifier begins with `project_case_id` and ends with a number for the opinion number, starting at 0 for every case (e.g. `230_0` for the first (`0`th) opinion in `project_case_id` = `230`). 
- `source`: Source of the opinion text. For most opinions prior to 2014 this is the [Harvard Caselaw Access Project](https://case.law/) (`hclap`), for most opinions starting in 2014 this is the [Supreme Court Website](https://www.supremecourt.gov/xmls/) (`scg`), and for a small set of cases missing from the prior two sources, this is [Justia](https://www.justia.com/) (`justia`).
- `docket`: Docket number for the case. 
- `citations`: U.S. reporter citation for the case.
- `case_url`: URL that holds the specific case text data. 
- `case_name`: Name of the case.
- `date`: Date the case was decided.
- `year`: Year in which  the case was decided. 
- `opinion_type`: High-level opinion category, including `majority`, `concurrence`, `per_curiam`, and `dissent`.
- `opinion_text`: Full text of the opinion.
- `zauth`: Lowercased last name of the opinion author. If multiple judges share a last name, a number is appended to the end (e.g. `roberts1` and `roberts2`).
- `jid`: The judge identifier in SCDB and Martin Quinn data.
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
- `zformal`: Formal measurement, where higher scores are more formal and lower scores are more grand (i.e. anti formal)



This code accompanies Measuring Jurisprudence, and the data accompanies the following projects:
- Thalken, Stiglitz, Mimno, Wilkens. [Modeling Legal Reasoning: LM Annotation at the Edge of Human Agreement](https://aclanthology.org/2023.emnlp-main.575/). *EMNLP* 2023.
- Stiglitz, Thalken. [Historical Trends in Macro-jurisprudence: A Language Model Assessment, 1870-2023](https://digitalcommons.law.umaryland.edu/mlr/vol84/iss1/3/). *Maryland Law Review* 2024.
- Stiglitz, Thalken. Understanding Change in Jurisprudence. *Under Review.*

If you use this data, please cite:  
*bibtex to come*
