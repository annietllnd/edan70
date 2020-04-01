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

def load_dictionaries():
	dictionary_virus = [row.strip() for row in open('Supplemental_file1.txt')]
	dictionary_disease = [row.strip() for row in open('Supplemental_file2.txt')]

	return dictionary_virus, dictionary_disease

#def tag():
	#load dictionaries


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
	#load metadata
	#metadata = load_metadata()
	#load dictionary
	viruses, diseases = load_dictionaries()
	tags = ['virus', 'disease']
	

if __name__ == '__main__':
	main()