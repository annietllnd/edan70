import re
import pandas as pd
from collections import defaultdict
import spacy
import en_core_web_sm
import numpy as np
import matplotlib.pyplot as plt
import string
import json
import os

def load_article(path):
	article = []
	paragraphs = []
	abstract = []
	with open(path, 'r') as f:
		article_dict = json.load(f)

		abstract = [s['text'] for s in article_dict['abstract']]

	print(abstract)
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
			
			#print("matching words found in dictionary", tagword, ":")
			#print(virus_words)
def construct_annotations(corduid_text, sourcedb_text, sourceid_text, divid_index, main_text):
	cord_uid = "{\"cord_uid\":\"" + corduid_text + "\", "

	sourcedb = "\"sourcedb\":\"" + sourcedb_text + "\", "

	sourceid = "\"sourceid\":\"" + sourceid_text + "\", "

	divid = "\"divid\":" + divid_index + ", "

	text = "\"text\":\"" + main_text + "\", "

	project = "\"project\":\"cdlai_CORD-19\", "

	denotations = "\"denotations\":"

	body = cord_uid + sourcedb + sourceid + divid + text + project + denotations

	return body

def export_pubannotation(id, section_index, type, body):
	file_name = id + "-" + section_index + "-" + type
	text_file = open(file_name, "wt")
	n = text_file.write(body)
	text_file.close()


def main():

	#files_path = [os.path.abspath(x) for x in os.listdir('comm_use_subset_100')]
	#files_path = [path.split('edan70/edan70/') for path in files_path]
	#files_path = [path[1] for path in files_path]

	#tag_article('comm_use_subset_100/'+files_path[1])
	annotation = construct_annotations("jjpi5gjm", "PMC", "PMC3516577", "1", "Cathepsin B \u0026 L are not required for ebola virus replication.\nEbola virus (EBOV), family Filoviridae, eme...")
	export_pubannotation("jjpi5gjm", "1", "abstract", annotation)

if __name__ == '__main__':
	main()