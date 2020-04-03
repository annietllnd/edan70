import re
import pandas as pd
import json
import os

def load_article(article_dict):
	article = []
	paragraphs = []

	title = article_dict['metadata']['title'] 
	title = re.sub(r'[^\w\s]','',title).lower()
	title = title.split()


	abstract = [s['text'] for s in article_dict['abstract']]

	for section in article_dict['body_text']:
		if(section['text'] is not None):
			article.append(section['text'])

	article = [paragraph.split() for paragraph in article]

	for paragraph in article:
		paragraph = [re.sub(r'[^\w\s]','',w).lower() for w in paragraph]
		paragraphs.append(paragraph)

		#corduid_text: 	metadata file
		#sourcedb_text	metadata file
		#sourceid_text:	metadata file
		#divid_index: 	obtain in program
		#main_text:		article file
		#denotations: 	obtain in program

	return title, abstract, paragraphs

#loads a metadata file and puts the content into lists
def load_metadata():
	metadata = pd.read_csv("metadata_comm_use_subset_100.csv")
	metadata = [[row] for row in metadata.values]

	return metadata


	#for article in metadata:
#		articles.append(article)#

#	abstracts = [[entry[8].split()] for entry in metadata if isinstance(entry[8], str)]#

#	for abstract in abstracts:
#		abstract[0] = [re.sub(r'[^\w\s]','',w).lower() for w in abstract[0]] #

#	return articles, abstracts

def load_metadata_row(cord_uid, metadata):
	for row in metadata:
		if(row[0][0] == cord_uid):
			return row

def obtain_metadata_args(row):
	row = row[0]
	cord_uid = row[0]
	sourcedb = row[2]
	sourceid = row[5]
	return cord_uid, sourcedb, sourceid

#loads the dictionaries from the supplemental files provided by @Aitslab
def load_dictionaries():
	dictionary_virus = [row.strip() for row in open('Supplemental_file1.txt')]
	dictionary_disease = [row.strip() for row in open('Supplemental_file2.txt')]

	return dictionary_virus, dictionary_disease

def tag(dictionary, corpus):
	tagged_words = []
	for w in corpus:
		if w in dictionary:
			tagged_words.append(w)

	return tagged_words

def tag_article(title, abstract, paragraphs, type, dictionary):

	if(type == "main_body"):
		for p in paragraphs:
			p_words = tag(dictionary, p)
			return p_words
	elif(type == "abstract"):
		for a in abstract:
			a_words = tag(dictionary, a)
			return a_words
	elif(type == "title"):
		t_words = tag(dictionary, title)
		return t_words
	else:
		print("Invalid type")
		return None

def get_span(match, body):
	regex_match = r"\b({0})\b".format(match)
	a = re.search(regex_match, body)
	if(a is None):
		return None, None
	else:
		return a.start(), a.end()



def construct_annotation(corduid_text, sourcedb_text, sourceid_text, divid_index, main_text, denotations):
	cord_uid = "\"cord_uid\":\"" + corduid_text + "\", "

	sourcedb = "\"sourcedb\":\"" + sourcedb_text + "\", "

	sourceid = "\"sourceid\":\"" + sourceid_text + "\", "

	divid = "\"divid\":" + divid_index + ", "

	text = "\"text\":\"" + main_text + "\", "

	project = "\"project\":\"cdlai_CORD-19\", "

	denotations_temp = ""
	for d in denotations:
		denotations_temp = denotations_temp + d

	denotations_str = "\"denotations\":" + denotations_temp

	body = "{" + cord_uid + sourcedb + sourceid + divid + text + project + denotations + "}"
	return body

def construct_dennoation(idd, begin, end, obj_url):
	idd = "\"id\":\"" + idd + "\", "

	span = "\"span\":{\"begin\":" + begin + "," + "\"end\":" + end  + "}, "

	obj = "\"obj\":\"" + obj_url + "\""

	body = "[{" + idd + span + obj + "}]"
	return body

def export_pubannotation(id, section_index, type, body):
	file_name = id + "-" + section_index + "-" + type
	text_file = open(file_name, "wt")
	text_file.write(body)
	text_file.close()


def main():

	# find paths
	files_path = [os.path.abspath(x) for x in os.listdir('comm_use_subset_100')]
	files_path = [path.split('edan70/edan70/') for path in files_path]
	files_path = [path[1] for path in files_path]

	# load dictionaries
	virus_dict, disease_dict = load_dictionaries()
	disease_dict = disease_dict + ["sars"]
	dicts = [virus_dict, disease_dict]
	dicts = {'virus':virus_dict, 'disease':disease_dict}

	# load article
	path = 'comm_use_subset_100/' + files_path[0]
	with open(path, 'r') as f:
		article_dict = json.load(f)

	title_text = article_dict['metadata']['title'] 

	title, abstract, paragraphs = load_article(article_dict)

	for dictionary in dicts:
		words = tag_article(title, abstract, paragraphs, "title", dicts[dictionary])
		print("tag dictionary found", len(words), "matches: ", words)

	for w in words:
		start, end = get_span(w, title_text)
		if(not start):
			print("No matches found, no index")



	#metadata = load_metadata()
	#load_metadata_row("ff7dg890", metadata)

	# test pubannotations
	#dennotation = construct_dennoation("PD-MONDO_T1", "37", "42","http://purl.obolibrary.org/obo/MONDO_0005737" ) 
	#annotation = construct_annotation("jjpi5gjm", "PMC", "PMC3516577", "1", "Cathepsin B \u0026 L are not required for ebola virus replication.\nEbola virus (EBOV), family Filoviridae, eme...", dennotation)
	#export_pubannotation("jjpi5gjm", "1", "abstract", annotation)

	#test search

if __name__ == '__main__':
	main()