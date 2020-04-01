import re
import pandas as pd
from collections import defaultdict
import spacy
import en_core_web_sm
import numpy as np
import matplotlib.pyplot as plt

#NOT USED
def test_supplthree():
	words = pd.read_csv("corona/manuscript/Supplemental_file3.csv")
	words = [list(word) for word in words.values]
	words = [pair[0] for pair in words]
	print(words[4])

def load_metadata():
	articles = []
	metadata = pd.read_csv("metadata_comm_use_subset_100.csv")
	metadata = [list(row) for row in metadata.values]
	
	for article in metadata:
		articles.append(article)

	print(articles)


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
	load_metadata()

if __name__ == '__main__':
	main()