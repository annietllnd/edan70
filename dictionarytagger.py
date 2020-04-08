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
    - Merge tag and returning indices
'''

import os
import json
import re
import copy
import pandas as pd


PUNCTUATION_REGEX = r'[^\w\s]'
METADATA_HEADER = ['cord_uid', 'sha', 'source_x', 'title', 'doi',
                   'pmcid', 'pubmed_id', 'license', 'abstract',
                   'publish_time', 'authors', 'journal', 'microsoftap_id',
                   '_', 'has_pdf_parse', 'has_pmc_xml_parse', 'full_text_file'
                   'url']


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


def find_token_index(token, text):
    """
    Returns a list of index placement for tokens in a text.
    """
    regex_token_match = fr"(?i)\b({token})\b"
    matches_list = re.findall(regex_token_match, text)
    token_index_list = [[None, None]]
    for match in matches_list:
        token_index_list.append([match.start(), match.end()])
    return token_index_list


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
def construct_denotation(idd, begin, end, obj_url):
    idd = "\"id\":\"" + idd + "\", "

    span = "\"span\":{\"begin\":" + begin + "," + "\"end\":" + end  + "}, "

    obj = "\"obj\":\"" + obj_url + "\""
    
    body = "{" + idd + span + obj + "}"
    return body

# returns a denotation string given a list of denotations, or just a placeholder string if it's empty
def concat_denotations(den_list):
    if(len(den_list) == 1):
        return "[" + den_list[0] + "]"
    elif(len(den_list) == 0):
        return "[]"

    final_denotation = ''

    for d in den_list:
        if(d == den_list[-1]):  # if d is the last element
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
    metadata_frame = pd.read_csv(metadata_csv_path,
                                 na_filter=False,
                                 names=METADATA_HEADER,
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
    for section in tokens_dict:
        # obtain the original, untokenized text
        if section == 'title':
            unprocessed_texts = [article_dict['metadata'][section]]
        else:
            unprocessed_texts = [section['text'] for section in article_dict[c]]
        for unprocessed_text in unprocessed_texts:  # iterate through each section that will have its own file
            denotations = []
            for vocabulary in VOCABS_COL_DICT:
                found_tokens = tag_tokens(VOCABS_COL_DICT[vocabulary],
                                          tokens_dict[section])
                if found_tokens == []:
                    [begin, end] = ['-1', '-1']  # No tokens found
                for found_token in found_tokens:
                    begin, end = find_token_index(found_token, unprocessed_text)  #TODO fix indice and tagging
                    begin = str(begin)
                    end = str(end)
                    if begin != '-1':
                        denotations.append(
                            construct_denotation(vocabulary,
                                                 begin,
                                                 end,
                                                 metadata_dict['url']))

            final_denotation = concat_denotations(denotations)

            temp_divid = str(divid_index)
            annotation = construct_annotation(cord_uid,
                                              pcmid,
                                              pubmed_id,
                                              temp_divid,
                                              unprocessed_texts[0],
                                              final_denotation)
            divid_index = divid_index + 1  # increase with each file
            export_pubannotation(cord_uid, temp_divid, section, annotation)


VOCABS_COL_DICT = load_vocabularies()


def main():
    """
    Main program.
    """
    article_paths = os.listdir('comm_use_subset_100')
    metadata_list, metadata_indices_dict = load_metadata()

    for article_name in article_paths:
        with open(article_name, 'r') as file_:
            article_dict = json.load(file_)

        # this index is used for the file name counter
        tokens_dict = generate_tokens_dict(article_dict)
        # Finds indice of metadata that matches with sha of article_name
        # without '.JSON' part.
        metadata_indice = metadata_indices_dict[
            article_name.replace('.json', '')]
        metadata_dict = metadata_list[metadata_indice]
        tag_and_export(article_dict, tokens_dict, metadata_dict)


if __name__ == '__main__':
    main()
