import re
import pandas as pd
from collections import defaultdict
import spacy
import en_core_web_sm
import numpy as np
import matplotlib.pyplot as plt
import string
import json

def load_article(path):
	article = []
	paragraphs = []
	with open(path, 'r') as f:
		article_dict = json.load(f)

	for section in article_dict['body_text']:
		if(section['text'] is not None):
			article.append(section['text'])

	article = [paragraph.split() for paragraph in article]

	for paragraph in article:
		paragraph = [re.sub(r'[^\w\s]','',w).lower() for w in paragraph]
		paragraphs.append(paragraph)

	return paragraphs

#loads a metadata file and puts the content into lists
def load_metadata():
	articles = []
	metadata = pd.read_csv("metadata_comm_use_subset_100.csv")
	metadata = [row for row in metadata.values]


	for article in metadata:
		articles.append(article)

	abstracts = [[entry[8].split()] for entry in metadata if isinstance(entry[8], str)]

	for abstract in abstracts:
		abstract[0] = [re.sub(r'[^\w\s]','',w).lower() for w in abstract[0]] 

	return articles, abstracts

#loads the dictionaries from the supplemental files provided by @Aitslab
def load_dictionaries():
	dictionary_virus = [row.strip() for row in open('Supplemental_file1.txt')]
	dictionary_disease = [row.strip() for row in open('Supplemental_file2.txt')]

	return dictionary_virus, dictionary_disease

def tag(dictionary, corpus, tag):
	tagged_words = []
	for w in corpus:
		if w in dictionary:
			tagged_words.append(w)

	return tag, tagged_words

def tag_article(path):
	article = load_article(path)

	virus_dict, disease_dict = load_dictionaries()
	dicts = [virus_dict, disease_dict]
	dicts = {'virus':virus_dict, 'disease':disease_dict}

	for dictionary in dicts:
		for section in article:
			tagword, virus_words = tag(dicts[dictionary], section, dictionary)
			
			print("matching words found in dictionary", tagword, ":")
			print(virus_words)


def main():

	tag_article('comm_use_subset_100/0fb887acf88daa31d5ae2b7d176baf904d6c5dfc.json')
	
	

if __name__ == '__main__':
	main()