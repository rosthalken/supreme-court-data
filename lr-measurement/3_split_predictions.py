import pandas as pd
import os
from collections import Counter

output_dir = os.path.join(os.getcwd(), 'output')
predictions_dir = os.path.join(output_dir, 'combined_output.csv')
df = pd.read_csv(predictions_dir)

predictions_cols = ['project_case_id', 'project_opinion_id', 'paragraph',
       'section_id', 'par_word_count', 'grand_count', 'formal_count', 
       'predictions', 'prob_0', 'prob_1', 'prob_2', 'predicted_class']
predictions_df = df[predictions_cols].drop_duplicates()


metadata_cols = ['project_case_id', 'project_opinion_id', 'source', 'docket','case_url', 'case_name', 'citations', 'date', 'court_url',
       'opinion_type', 'opinion_text', 'authors_raw', 'author_names',
       'author_ids', 'year', 'zauth', 'cdate', 'tdate', 'pty', 'presname',
       'jid', 'justice', 'term', 'mq', 'repub', 'preslast', 'last', 'presip',
       'decisionDirection', 'majVotes', 'nytSalience', 'caseId', 'voteId', 'cqSalience',
       'chief',  'vote', 'spec_opinion_type']

metadata_df = df[metadata_cols].drop_duplicates()
metadata_df = metadata_df.drop_duplicates()

metadata_df.to_csv(os.path.join(output_dir, 'metadata.csv'))
predictions_df.to_csv(os.path.join(output_dir, 'predictions.csv'))

