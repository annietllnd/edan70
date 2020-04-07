'''
Dictionary tagger for COVID-19

Authors:
    Annie Tallind, Lund University, Faculty of Engineering
    Kaggle ID: atllnd
    Github ID: annietllnd

    Sofi Flink, Lund University, Faculty of Engineering
    Kaggle ID: sofiflinck
    Github ID: obakanue

Credit:
    TODO

TODO-list:
    - Way of reaching files through github.
    - What to do when entries are empty?
    - Generate correct CSV-file so we do not have to explicitly include header.
    - Create a variable that denotes the index that should be written to the
      file. I.e. a file can be abcdefg-7-body_text but be the 2nd section of
      the body_text if the abstract has several sections.
    - Find another word than vocabulary representing covid dictionaries
      and not dictionary since this will confuse with the data type
    - Greedu search when tagging (non-composite words)
    - Why we need "path = path[1:]" in find sha.
    - Find good solution for keeping track of metadata index.
    - Check correct columns retrieved!
'''

import os
import json
import re
import copy
import pandas as pd


# Importing files locally
CURRENT_WORKING_DIR = os.getcwd() + '/'
ARTICLE_FULL_PATHS = os.listdir('comm_use_subset_100')

# Importing files from Kaggle project (for Kaggle implementation)
# ARTICLE_DIR_PATH = '../input/comm-use-subset-100/'  # Can be changed to path
# ARTICLE_FULL_PATHS = []                             # of folder for another
# for file in os.listdir(articles_dir):               # dataset.
#    ARTICLE_FULL_PATHS.append(ARTICLE_DIR_PATH = file)


# Importing files locally (machine dependent)
# files_path = [os.path.abspath(x) for x in os.listdir('comm_use_subset_100')]
# splits the path so we will only obtain the actual file name
# files_path = [path.split('edan70/edan70/') for path in files_path]
# files_path = [path[1] for path in files_path] # only the name of the file


# Load JSON-files from git-repository https://github.com/annietllnd/edan70/comm_use_subset 100. 
# TODO fix


# Parse JSON-files and add articles to array.
articles = []
for article_path in ARTICLE_FULL_PATHS:
    with open(article_path, 'r') as file_:
        articles.append(json.load(file_))


# Define functions for cleaning the articles.

# First function cleans the title section of the article and removes
# all punctuations and adjusts to lower case.
def clean_title(data_dict, regex):
    """
    Return title string after removing punctuations and format to lower case
    for title section of JSON-files.
    """
    title = data_dict['metadata']['title']
    # TODO What should we do when content is empty?
    if title is not None:
        title = re.sub(regex, '', title).lower()
        title = title.split()
    else:
        title = ''
    return title


# Second function cleans the abstract section of the article and removes
# all punctuations and adjusts to lower case.
def clean_abstract(data_dict, regex):
    """
    Return abstract list with strings after removing punctuations and format to
    lower case for title section of JSON-files.
    """
    abstract = [section['text'] for section in data_dict['abstract']]
    # TODO What should we do when content is empty?
    if abstract != []:
        abstract = [section.split() for section in abstract]
        abstract = [re.sub(regex, '', w).lower() for w in abstract[0]]
    else:
        abstract = ['']
    return abstract


# Third function cleans the body text section of the article and removes
# all punctuations and adjusts to lower case.
def clean_body_text(data_dict, regex):
    """
    Return paragraphs list words strings after removing punctuations and format
    to lower case for title section of JSON-files.
    """
    body_text = []

    for paragraph in data_dict['body_text']:
        if paragraph['text'] is not None:
            body_text.append(paragraph['text'])

    body_text = [paragraph.split() for paragraph in body_text]
    paragraphs = ['']
    for paragraph in body_text:
        paragraph = [re.sub(regex, '', word).lower() for word in paragraph]
        paragraphs.append(paragraph)
    return paragraphs


# Run defined cleaner functions on article data, iterating through every
# article and put files in a new array of cleaned articles.
cleaned_articles = []
PUNCTUATION_REGEX = r'[^\w\s]'  # Regex for everything that is not a
for article_dict in articles:           # character or space.
    clean_article_dict = copy.deepcopy(article_dict)
    clean_article_dict['metadata']['title'] = clean_title(clean_article_dict,
                                                          PUNCTUATION_REGEX)
    clean_article_dict['abstract'] = clean_abstract(clean_article_dict,
                                                    PUNCTUATION_REGEX)
    clean_article_dict['body_text'] = clean_body_text(clean_article_dict,
                                                      PUNCTUATION_REGEX)
    cleaned_articles.append(clean_article_dict)


# Import dicitonaries with words regarding viruses and disieases for COVID
# for tagging of data.

# Import from Kaggle path.
# VOCAB_COLLECTION_DICT = {'Virus_SARS-CoV-2':
#                          [row.strip()for row in
#                           open('../input/supplement/Supplemental_file1.txt')],
#                          'Disease_COVID-19':
#                          [row.strip() for row in
#                           open('../input/supplement/Supplemental_file2.txt')]}

# Import from local directory.
VOCAB_COL_DICT = {'Virus_SARS-CoV-2':
                         [row.strip()for row in
                          open(CURRENT_WORKING_DIR+'Supplemental_file1.txt')],
                         'Disease_COVID-19':
                         [row.strip() for row in
                          open(CURRENT_WORKING_DIR+'Supplemental_file2.txt')]}


# Define function for tagging words in vocabulary list.
def tag_tokens(vocabulary, tokens):
    """
    Return list of token strings found in dictionary.
    """
    tagged_words = []
    for token in tokens:
        if token in vocabulary:         # TODO Maybe find another definition
            tagged_words.append(token)  # than vocabulary?
    return tagged_words


# CSV-files with metadata for compensation for data missing in JSON-files.
# Import CSV-files with metadata for articles using Kaggle path.
# METADATA_CSV_PATH = '../input/metadata/metadata_comm_use_subset_100.csv'

# Import CSV-files with metadata for articles using local path.
METADATA_CSV_PATH = '../input/metadata/metadata_comm_use_subset_100.csv'
# TODO Fix CSV-file with header
METADATA_HEADER = ['cord_uid', 'sha', 'source_x', 'title', 'doi',
                   'pmcid', 'pubmed_id', 'license', 'abstract',
                   'publish_time', 'authors', 'journal', 'microsoftap_id',
                   '_', 'has_pdf_parse', 'has_pmc_xml_parse', 'full_text_file'
                   'url']
METADATA_FRAME = pd.read_csv(METADATA_CSV_PATH,
                             names=METADATA_HEADER,
                             engine='python')
metadata_list = METADATA_FRAME.to_dict('records')


def obtain_metadata_args(metadata_dict):
    """
    Returns necessary columns from metadata dictionary.
    """
    cord_uid = metadata_dict['cord_uid']
    pmcid = metadata_dict['pmcid']  # TODO not sure which column
    pubmed_id = metadata_dict['pubmed_id']
    return cord_uid, pmcid, pubmed_id


def load_vocabularies():
    """
    Return dictionary of imported vocabularies lists proviced by @Aitslab.
    """
    virus_vocab_list = [row.strip() for row in
                        open('Supplemental_file1.txt')]
    disease_vocab_list = [row.strip() for row in 
                          open('Supplemental_file2.txt')]
    vocabs_col_dict = {'Virus_SARS-CoV-2':
                       virus_vocab_list,
                       'Disease_COVID-19':
                       disease_vocab_list}
    return vocabs_col_dict


# tag a tokenized text using a given dictionary and return a list of the words
def tag(dictionary, corpus):
    tagged_words = []
    for w in corpus:
        if w in dictionary:
            tagged_words.append(w)

    return tagged_words

# given a word and a corpus, find the match for that word
# improve: what if there are several matches? 
def get_span(match, body):
    regex_match = r"(?i)\b({0})\b".format(match)
    a = re.search(regex_match, body)
    if(a is None):
        return None, None
    return a.start(), a.end()

# returns a pubannotation string
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

# returns a denotation string for a single match
def construct_dennoation(idd, begin, end, obj_url):
    idd = "\"id\":\"" + idd + "\", "

    span = "\"span\":{\"begin\":" + begin + "," + "\"end\":" + end  + "}, "

    obj = "\"obj\":\"" + obj_url + "\""

    body = "{" + idd + span + obj + "}"
    return body

# returns a denotation string given a list of denotations, or just a placeholder string if it's empty
def concat_denotations(den_list):
    if(len(den_list) == 1):
        return  "[" + den_list[0] + "]"
    elif(len(den_list) == 0):
        return "[]"

    final_denotation = ''
    first = True

    for d in den_list:
        if(d == den_list[-1]): # if d is the last element
            final_denotation += d
        else:
            final_denotation += d + ", "

    return "[" + final_denotation + "]"

# exports a given annotation string to a file
def export_pubannotation(idd, section_index, type_text, annotation):
    file_name = idd + "-" + section_index + "-" + type_text
    text_file = open("out/" + file_name + ".json", "wt")
    text_file.write(annotation)
    text_file.close()


def load_metadata():
    """
    Returns list with metadata and dictionary with sha as keys and indices
    of metadata list as values.
    """
    metadata_csv_path = 'metadata_comm_use_subset_100.csv'
    metadata_header = ['cord_uid', 'sha', 'source_x', 'title', 'doi',
                       'pmcid', 'pubmed_id', 'license', 'abstract',
                       'publish_time', 'authors', 'journal', 'microsoftap_id',
                       '_', 'has_pdf_parse', 'has_pmc_xml_parse',
                       'full_text_file', 'url']
    metadata_frame = pd.read_csv(metadata_csv_path,
                                 na_filter=False,
                                 names=metadata_header,
                                 engine='python')
    metadata = metadata_frame.to_dict('records')
    indice = 0
    metadata_indices_dict = dict()
    for data in metadata:  # TODO other solution?
        shas = data['sha'].split('; ', 1)
        for sha in shas:                                 # TODO Do we need to
            metadata_indices_dict.update({sha, indice})  # keep track of indice
        indice += 1                                      # of page-id/sha?
    return metadata, metadata_indices_dict


def generate_tokens_dict(article_dict, regex=PUNCTUATION_REGEX):
    """
    Return dicionary of tokenized sections.
    """
    title = clean_title(article_dict, regex)
    abstract = clean_abstract(article_dict, regex)
    body_text = clean_body_text(article_dict, regex)

    tokens_dict = {"title": title,
                   "abstract": abstract,
                   "body_text": body_text}
    return tokens_dict


def tag_and_export(article_dict, tokens_dict, metadata_dict):
    divid_index = 0  # TODO Check indices for file index and content index
    cord_uid, pcmid, pubmed_id = obtain_metadata_args(metadata_dict)
    for token in tokens_dict:
        # obtain the original, untokenized text
        if(token == 'title'):
            section = [article_dict['metadata'][token]]
        else:
            section = [article_dict[token][0]['text'] for s in article_dict[token]]
        for subc in section:  # iterate through each section that will have its own file
            denotations = []
            for vocabulary in VOCAB_COL_DICT:
                idd = vocabulary
                words = tag(VOCAB_COL_DICT[vocabulary], tokens_dict[token])
                if(words == []):
                    [begin, end] = ['-1', '-1']  # improve: maybe make a more sleek solution
                for w in words:
                    begin, end = get_span(w, section[0])
                    begin = str(begin)
                    end = str(end)
                    if(begin != '-1'):
                        print("tag dictionary found",
                              len(words), "matches: ", words)
                        denotations.append(
                        construct_dennoation(idd,
                                             begin,
                                             end,
                                             metadata_dict['url']))

        final_denotation = concat_denotations(denotations)

        temp_divid = str(divid_index)
        annotation = construct_annotation(cord_uid,
                                          pcmid,
                                          pubmed_id,
                                          temp_divid,
                                          section[0],
                                          final_denotation)
        divid_index = divid_index + 1  # we want the index in each file to increase
        export_pubannotation(cord_uid, temp_divid, token, annotation)
