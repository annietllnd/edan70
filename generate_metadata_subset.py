import os
import pandas as pd
import numpy as np
import json


metadata = pd.read_csv('data/metadata.csv', header=0)
metadata = metadata.replace(np.nan, '', regex=True)
header = metadata.columns.values

subset_n = pd.DataFrame(columns=header)
subset_dir_path = 'data/gold_standard_subset_10'
file_names = os.listdir(subset_dir_path)

for file_name in file_names:
	if file_name == '.DS_Store':  # For MacOS users skip .DS_Store-file
		continue  # generated.
	full_path = subset_dir_path + '/' + file_name
	with open(full_path) as article:
		article_dict = json.load(article)
	temp_row = metadata[metadata['sha'].str.contains(article_dict['paper_id'])]

	if not temp_row.empty:
		subset_n = subset_n.append(temp_row, ignore_index=True)

subset_n.to_csv('data/gold_standard_subset_10.csv', index=False)
