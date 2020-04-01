import re
import pandas as pd
from collections import defaultdict
import spacy
import en_core_web_sm
import numpy as np
import matplotlib.pyplot as plt
import string


#loads a metadata file and puts the content into lists
def load_metadata():
	articles = []
	metadata = pd.read_csv("metadata_comm_use_subset_100.csv")
	metadata = [row for row in metadata.values]


	for article in metadata:
		articles.append(article)

	return articles

#loads the dictionaries from the supplemental files provided by @Aitslab
def load_dictionaries():
	dictionary_virus = [row.strip() for row in open('Supplemental_file1.txt')]
	dictionary_disease = [row.strip() for row in open('Supplemental_file2.txt')]

	return dictionary_virus, dictionary_disease

def tag(dictionary, corpus, tag):
	tagged_words = []
	for w in corpus[0]:
		w = re.sub(r'[^\w\s]','',w)
		w = w.lower()
		
		if w in dictionary:
			tagged_words.append(w)

	return tag, tagged_words

def main():
	#load metadata
	metadata = load_metadata()
	abstracts = [[entry[8].split()] for entry in metadata if isinstance(entry[8], str)]
	#load dictionary
	viruses, diseases = load_dictionaries()
	tags = ['virus', 'disease']

	for tagword in tags:
		for abstract in abstracts:
			_, virus_words = tag(viruses, abstract, tagword)
			if(virus_words != []):
				print("matching words found in dictionary", tagword, ":")
				print(virus_words)




	

if __name__ == '__main__':
	main()