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
    (- Way of reaching files through github.)
    * - Generate correct CSV-file so we do not have to explicitly include
    header. UPDATE CODE and correct columns.
    // ANNIE
    *- Greedy search when tagging (non-composite words)
    // ANNIE
    - Create notebook with program.
    - Prioritize vocabularies
    - Evaluate model (last)
'''

import os
import json
import re
import copy
import pandas as pd

DIRECTORY_NAME = 'comm_use_subset_100'
PUNCTUATION_REGEX = r'[^\w\s]'

"""
Patterns:
1. All words ending in 'vir' case insensitive in class 'chemical_antiviral'.
"""
patterns = {'chemical_antiviral':
            r'(?i)\b\S*vir\b'
            }


def load_vocabularies():
    """
    Return dictionary of imported vocabularies lists proviced by p@Aitslab.
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


# Global so we do not have to send it between methods.
VOCABS_COL_DICT = load_vocabularies()


def load_metadata():
    """
    Returns list with metadata and dictionary with sha as keys and indices
    of metadata list as values.
    """
    metadata_csv_path = 'metadata_comm_use_subset_100.csv'
    metadata_frame = pd.read_csv(metadata_csv_path,
                                 na_filter=False,
                                 engine='python')
    metadata = metadata_frame.to_dict('records')
    index = 0
    metadata_indices_dict = dict()
    for data in metadata:
        shas = data['sha'].split('; ', 1)
        for sha in shas:
            metadata_indices_dict.update({sha: index})
        index += 1
    return metadata, metadata_indices_dict


def generate_tokens_dict(article_dict, regex=PUNCTUATION_REGEX):
    """
    Return dicionary of tokenized sections.
    """
    title = clean_title(article_dict, regex)
    abstract = clean_abstract(article_dict, regex)
    body_text = clean_body_text(article_dict, regex)

    tokens_dict = {'title': title,
                   'abstract': abstract,
                   'body_text': body_text}
    return tokens_dict


def clean_title(data_dict, regex):
    """
    Return title string after removing punctuations and format to lower case
    for title section of JSON-files.
    """
    title = data_dict['metadata']['title']
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


def obtain_metadata_args(metadata_dict):
    """
    Returns necessary columns from metadata dictionary. Index 0 gives cord_uid,
    index 1 gives source_x, index 2 gives pmcid.
    """
    cord_uid = metadata_dict['cord_uid']
    source_x = metadata_dict['source_x']
    pmcid = metadata_dict['pmcid']
    metadata_info = [cord_uid, source_x, pmcid]
    return metadata_info


def tag_tokens(vocabulary, tokens):
    """
    Return list of token strings found in dictionary.
    """
    tagged_words = set()
    for token in tokens:
        if token in vocabulary:  # TODO Maybe find another definition
            tagged_words.add(token)  # than vocabulary?
    return tagged_words


def find_token_indices(token, section_text):
    """
    Returns a list of index placement for tokens in a section text.
    """
    regex_token_match = fr"(?i)\b" + token + r"\b"
    matches_iterator = re.finditer(regex_token_match, section_text)
    token_index_list = []
    for match in matches_iterator:
        token_index_list.append([str(match.start()), str(match.end())])
    return token_index_list


def tag_pattern(pattern, section_text):
    """
    Returns a list of index placement for matches found using
    pattern in a section text.
    """
    matches_iterator = re.finditer(pattern, section_text)
    token_index_list = []
    for match in matches_iterator:
        print(match)
        token_index_list.append([str(match.start()), str(match.end())])
    return token_index_list


def process_section(article_dict, tokens_dict, metadata_dict):
    """
    For each text section
    """
    file_index = 0
    metadata_info = obtain_metadata_args(metadata_dict)
    for text_section in tokens_dict:
        paragraph_index = 0
        # obtain the original, untokenized text
        if text_section == 'title':
            unprocessed_texts = [article_dict['metadata'][text_section]]
        else:
            unprocessed_texts = [section['text'] for section in
                                 article_dict[text_section]]
        # Iterate through each section of unprocessed texts that will generate
        # its own file
        for unprocessed_text in unprocessed_texts:
            denotation = obtain_denotation(tokens_dict,
                                           text_section,
                                           unprocessed_text,
                                           metadata_dict['url'])
            annotation = construct_pubannotation(metadata_info,
                                                 paragraph_index,
                                                 unprocessed_text,
                                                 denotation)
            # export_pubannotation(metadata_info[0],
            #                    file_index,
            #                    text_section,
            #                    annotation)
            file_index += 1  # Increase with each file
            paragraph_index += 1  # Increase with each paragraph


def obtain_denotation(tokens_dict, section, unprocessed_text, url):
    """
    Returns a denotation string, string with text where token and pattern
    matches where found.
    """
    denotations = []
    for vocabulary in VOCABS_COL_DICT:
        token_index_list = []
        found_tokens = tag_tokens(VOCABS_COL_DICT[vocabulary],
                                  tokens_dict[section])
        for found_token in found_tokens:
            token_index_pairs = find_token_indices(found_token, unprocessed_text)
            if bool(token_index_pairs):
                token_index_list.append(token_index_pairs)
                print(found_token)
        for token_index_pair in token_index_list:
            begin, end = token_index_pair[0][0], token_index_pair[0][1]
            denotations.append(
                construct_denotation(vocabulary,
                                     begin,
                                     end,
                                     url))

    for pattern in patterns:
        token_index_list = []
        token_index_pairs = tag_pattern(pattern, unprocessed_text)
        if bool(token_index_pairs):
            token_index_list.append(token_index_pairs)
        for token_index_pair in token_index_list:
            begin, end = token_index_pair[0][0], token_index_pair[0][1]
            denotations.append(
                construct_denotation(pattern,
                                     begin,
                                     end,
                                     url))

    return concat_denotations(denotations)


def construct_denotation(idd, begin, end, url):
    """
    Returns a string for a single match.
    """
    idd = "\"id\":\"" + idd + "\", "

    span = "\"span\":{\"begin\":" + begin + "," + "\"end\":" + end + "}, "

    obj = "\"obj\":\"" + url + "\""
    denotation = "{" + idd + span + obj + "}"
    return denotation


def concat_denotations(denotations):
    """
    Returns a complete string of all seperate denotations in list parameter,
    or and empty string if there where no elements in the list.
    """
    if not bool(denotations):
        return "[]"

    full_denotation = ''

    for denotation in denotations:
        if denotation == denotations[-1]:
            full_denotation += denotation
        else:
            full_denotation += denotation + ", "
    return "[" + full_denotation + "]"


def construct_pubannotation(metadata_info, section_index, text, denotation):
    """
    Returns a string in pubannotation format.
    """
    cord_uid = "\"cord_uid\":\"" + metadata_info[0] + "\", "

    source_x = "\"sourcedb\":\"" + metadata_info[1] + "\", "

    pmcid = "\"sourceid\":\"" + metadata_info[2] + "\", "

    divid = "\"divid\":" + str(section_index) + ", "

    text = "\"text\":\"" + text + "\", "

    project = "\"project\":\"cdlai_CORD-19\", "

    denotations_str = "\"denotations\":" + denotation

    return "{" + cord_uid + source_x + pmcid + divid + text + project + \
           denotations_str + "}"


def export_pubannotation(idd, file_index, section_name, annotation):
    """
    Export pubannotation string to a file.
    """
    file_name = idd + "-" + str(file_index) + "-" + section_name
    text_file = open("out/" + file_name + ".json", "wt")
    text_file.write(annotation)
    text_file.close()


def main():
    """
    Main program.
    """
    article_paths = os.listdir(DIRECTORY_NAME)
    metadata_list, metadata_indices_dict = load_metadata()
    for article_name in article_paths:
        if article_name == ".DS_Store":  # For MacOS users skip .DS_Store-file
            continue  # generated.
        full_path = DIRECTORY_NAME + '/' + article_name
        with open(full_path) as article:
            article_dict = json.load(article)
        tokens_dict = generate_tokens_dict(article_dict)
        # Finds indice of metadata that matches with sha of article_name
        # (without '.JSON' part.)
        metadata_indice = metadata_indices_dict[
            article_name.replace('.json', '')]
        metadata_dict = metadata_list[metadata_indice]
        process_section(article_dict, tokens_dict, metadata_dict)


if __name__ == '__main__':
    main()
