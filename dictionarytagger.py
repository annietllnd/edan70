import re
import pandas as pd
from collections import defaultdict
import spacy
import en_core_web_sm
import numpy as np
import matplotlib.pyplot as plt

#loads a metadata file and puts the content into lists
def load_metadata():
	articles = []
	metadata = pd.read_csv("metadata_comm_use_subset_100.csv")
	metadata = [list(row) for row in metadata.values]
	
	for article in metadata:
		articles.append(article)

	return articles

#temporary to understand how the task should be performed
def test_dict():
	dictionary_sars = ['sars']
	temp_dict = ['disease', 'icecream', 'horse', 'sars']
	tags_sars = []

	for word in temp_dict:
		if(word in dictionary_sars):
			tags_sars.append([word, 'virus'])
		else:
			tags_sars.append([word, None])

	print(tags_sars)




def main():
	#test_dict()
	metadata = load_metadata()

if __name__ == '__main__':
	main()