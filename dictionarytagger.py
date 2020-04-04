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
	abstract = [section.split() for section in abstract]

	abstract = [re.sub(r'[^\w\s]','',w).lower() for w in abstract[0]]

	for section in article_dict['body_text']:
		if(section['text'] is not None):
			article.append(section['text'])

	article = [paragraph.split() for paragraph in article]

	for paragraph in article:
		paragraph = [re.sub(r'[^\w\s]','',w).lower() for w in paragraph]
		paragraphs.append(paragraph)


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
	regex_match = r"(?i)\b({0})\b".format(match)
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

	body = "{" + cord_uid + sourcedb + sourceid + divid + text + project + denotations_str + "}"
	return body

def construct_dennoation(idd, begin, end, obj_url):
	idd = "\"id\":\"" + idd + "\", "

	span = "\"span\":{\"begin\":" + begin + "," + "\"end\":" + end  + "}, "

	obj = "\"obj\":\"" + obj_url + "\""

	body = "{" + idd + span + obj + "}"
	return body

def concat_denotations(den_list):
	if(len(den_list) == 1):
		return  "[" + den_list[0] + "]"
	elif(len(den_list) == 0):
		return "[]"

	final_denotation = ''
	first = True

	for d in den_list:
		if(d == den_list[-1]):
			final_denotation += d
		else:
			final_denotation += d + ", "


	return "[" + final_denotation + "]"

def export_pubannotation(id, section_index, type, annotation):
	file_name = id + "-" + section_index + "-" + type
	text_file = open("out/" + file_name + ".json", "wt")
	text_file.write(annotation)
	text_file.close()


def main():
	# find paths, can be separate
	files_path = [os.path.abspath(x) for x in os.listdir('comm_use_subset_100')]
	files_path = [path.split('edan70/edan70/') for path in files_path]
	files_path = [path[1] for path in files_path]


	# load dictionaries, can be separate
	virus_dict, disease_dict = load_dictionaries()
	disease_dict = disease_dict
	disease_dict = disease_dict + ["sars"]
	virus_dict = virus_dict + ["sars"]
	dicts = [virus_dict, disease_dict]
	dicts = {'Virus_SARS-CoV-2':virus_dict, 'Disease_COVID-19':disease_dict} #fix this

	# load metadata, can be separate
	metadata = load_metadata()
	cord_uids = [metadata[i][0][0] for i in range(len(metadata))]


	for i in range(0,2): #exchange for range(len(files_path))
		#load the ith file in the directory
		divid_index = 0
		path = 'comm_use_subset_100/' + files_path[i] #for loop
		with open(path, 'r') as f:
			article_dict = json.load(f)

		#load article from file
		title, abstract, body_text = load_article(article_dict)

		corpus = {"title": title, "abstract": abstract, "body_text": body_text}

		# load args for pubannotations
		# corduid_text: 	metadata file
		# sourcedb_text:	metadata file
		# sourceid_text:	metadata file
		cord_uid, sourcedb, sourceid = obtain_metadata_args(metadata[i])

		#obj_url 
		obj_url = metadata[i][0][16]

		for c in corpus:
			#obtain the original, untokenized text
			if(c == 'title'):
				section = [article_dict['metadata'][c]]
			else:
				section = [article_dict[c][0]['text'] for s in article_dict[c]]
			for subc in section:
				denotations = []	

				for dictionary in dicts:
					idd = dictionary
					words = tag(dicts[dictionary], corpus[c])
					#print("tag dictionary found", len(words), "matches: ", words)	
					if(words == []):
						[begin, end] = ['-1', '-1']				
					for w in words:
						begin, end = get_span(w, section[0])
						begin = str(begin)
						end = str(end)	

					if(begin != '-1'):
						denotations.append(construct_dennoation(idd, begin, end, obj_url))

				final_denotation = concat_denotations(denotations) 

					
				temp_divid = str(divid_index)
				annotation = construct_annotation(cord_uid, sourcedb, sourceid, temp_divid, section[0], final_denotation)	
				print(annotation)
				divid_index = divid_index + 1
				export_pubannotation(cord_uid, temp_divid, c, annotation)


if __name__ == '__main__':
	main()