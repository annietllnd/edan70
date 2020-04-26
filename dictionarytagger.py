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
    - Create notebook with program.
    - Evaluate model (last)
'''

import os
import json
import re
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
section_matches = dict()


def load_vocabularies():
    """
    Return dictionary of imported vocabularies lists provided by @Aitslab.
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


def process_article(article_dict, metadata_dict):
    """
    Process article for each section and generate pub annotations for export to file.
    """
    file_index = 0
    metadata_info = obtain_metadata_args(metadata_dict)
    sections = ['metadata', 'abstract', 'body_text']
    for section in sections:
        section_matches.clear()
        paragraph_index = 0
        if section == 'metadata':
            section_texts = [article_dict[section]['title']]
            section = 'title'
        else:
            section_texts = [section['text'] for section in
                             article_dict[section]]
        if bool(section_texts):
            section_texts = ['']
        for section_text in section_texts:
            denotation, paragraph_index = get_denotation(section_text,
                                                         metadata_dict['url'],
                                                         paragraph_index)
            annotation = construct_pubannotation(metadata_info,
                                                 paragraph_index,
                                                 section_text,
                                                 denotation)
            # export_pubannotation(metadata_info[0],
            #                    file_index,
            #                    section,
            #                    annotation)
        file_index += 1  # Increase with each file


def get_denotation(section_text, url, paragraph_index):
    """
    Returns a denotation string, string with text where token and pattern
    matches where found.
    """
    denotations = []
    for vocabulary in VOCABS_COL_DICT:
        for word in VOCABS_COL_DICT[vocabulary]:
            pattern = fr'(?i)\b{word}\b'
            tag_section(pattern, section_text, url, denotations, vocabulary)

    for word_class in patterns:
        tag_section(patterns[word_class], section_text, url, denotations, word_class)
    paragraph_index += 1
    return concat_denotations(denotations), paragraph_index


def tag_section(pattern, section_text, url, denotations, word_class):
    """
    Finds all matches of a section for a pattern.
    """
    matches = tag_pattern(pattern, section_text, word_class)
    if bool(matches):
        for match in matches:
            begin, end = match.begin(), match.end()
            denotations.append(construct_denotation(word_class,
                                                    begin,
                                                    end,
                                                    url))


def tag_pattern(pattern, section_text, word_class):
    """Virus_SARS-CoV-2
    Returns a list of index placement for matches found using
    pattern in a section text.
    """
    matches = []
    for match in re.finditer(pattern, section_text):
        word_match = match.group(0)
        is_priority = check_match_priority(pattern, match, word_class)
        if is_priority:
            matches.append(match)
            section_matches.update({word_match: word_class})
    return matches


def check_match_priority(pattern, new_match, word_class):
    for word_match in section_matches:
        if word_class == 'Virus_SARS-CoV-2' or word_class == 'Disease_COVID-19':
            prev_tagged = re.match(pattern, word_match)
            if prev_tagged:
                longest_match = max(new_match, word_match, key=len)
                if longest_match == new_match:
                    del section_matches[word_match]
                    return True
                return False
            return True
        return True


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
    Returns a complete string of all separate denotations in list parameter,
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
        # Finds index of metadata that matches with sha of article_name
        # (without '.JSON' part.)
        metadata_index = metadata_indices_dict[
            article_name.replace('.json', '')]
        metadata_dict = metadata_list[metadata_index]
        process_article(article_dict, metadata_dict)


if __name__ == '__main__':
    main()
