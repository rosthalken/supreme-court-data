import pandas as pd
import os
import numpy as np

df =  pd.read_csv(os.path.join(os.getcwd(), 'output', 'predictions.csv'))
metadata_df  = pd.read_csv(os.path.join(os.getcwd(), 'output', 'metadata.csv'))

df['bpnformal'] = (df['prob_0']*1 + df['prob_1']*(-1)) * (df['prob_0'] + df['prob_1']) # paragraph level scores
opinion_scores = pd.DataFrame(df.groupby('project_opinion_id')['bpnformal'].mean())
metadata_df = metadata_df.merge(opinion_scores, on = 'project_opinion_id')
metadata_df['zformal'] = (metadata_df['bpnformal'] - metadata_df['bpnformal'].mean()) / metadata_df['bpnformal'].std()
metadata_df = metadata_df.drop(columns = 'Unnamed: 0')


project_columns = ['project_case_id', 'project_opinion_id', 'source',
       'docket', 'case_url', 'case_name', 'citations', 'date', 'year', 
       'opinion_type', 'opinion_text', 'zauth','cdate', 'tdate', 'pty', 
       'presname', 'jid', 'mq', 'repub', 'preslast', 'presip',
       'decisionDirection', 'caseId', 'voteId', 'chief', 'zformal']

metadata_df = metadata_df[project_columns].sort_values(by = "project_case_id").reset_index(drop=True)
metadata_df = metadata_df.rename(columns = {"caseId":"scdbCaseId", "voteId":"scdbVoteId"})
metadata_df.to_csv(os.path.join(os.getcwd(), 'output', "reasoning.csv"))



