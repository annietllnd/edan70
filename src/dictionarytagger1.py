"""
Dictionary tagger for COVID-19

Authors:
    Annie Tallind, Lund University, Faculty of Engineering
    Kaggle ID: atllnd
    Github ID: annietllnd

    Sofi Flink, Lund University, Faculty of Engineering
    Kaggle ID: sofiflinck
    Github ID: obakanue

Credit:
    Dictionaries were generated using golden- and silver-standard implemented by Aitslab.

TODO-list:
    (- Way of reaching files through github.)
    - Evaluate model (last) see discord for more information.
        * For every dictionary class
        * Precision recall
        * List with errors
"""

import os
import json
import re
import pandas as pd


def obtain_metadata_args(metadata_dict):
    """
    Returns necessary columns from metadata dictionary. Index 0 gives cord_uid, index 1 gives source_x, index 2 gives
    pmcid.
    """
    cord_uid = metadata_dict['cord_uid']
    source_x = metadata_dict['source_x']
    pmcid = metadata_dict['pmcid']
    metadata_info = [cord_uid, source_x, pmcid]
    return metadata_info


def construct_denotation(idd, begin, end, url):
    """
    Returns a string denotation for a single match.
    """
    idd = "\"id\":\"" + idd + "\", "

    span = "\"span\":{\"begin\":" + begin + "," + "\"end\":" + end + "}, "

    obj = "\"obj\":\"" + url + "\""
    denotation = "{" + idd + span + obj + "}"
    return denotation


def concat_denotations(denotations):
    """
    Returns a complete denotation string of all separate denotations in
    list parameter, or an empty string if there where no elements in the
    list.
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
    Returns a string in pub-annotation format.
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


def export_pubannotation(idd, file_index, section, annotation):
    """
    Export pub-annotation string to corresponding section file.
    """
    file_name = idd + '-' + str(file_index) + '-' + section
    text_file = open('out/' + file_name + '.json', 'wt')
    text_file.write(annotation)
    text_file.close()


class DictionaryTagger:
    def __init__(self, json_articles_dir_path, metadata_file_path, vocabularies_dir_path):
        self.articles_directory_name = json_articles_dir_path

        self.vocabs_col_dict = dict()
        self.patterns_dict = dict()
        self.metadata_list = list()
        self.metadata_indices_dict = dict()
        self.paragraph_matches = dict()
        self.word_classes = set()

        os.chdir('..')
        self.load_vocabularies(vocabularies_dir_path)
        self.load_patterns()
        self.load_metadata(metadata_file_path)

    def load_vocabularies(self, vocabularies_dir_path):
        vocabularies_file_names = os.listdir(vocabularies_dir_path)
        i = 0;
        for vocabulary_file_name in vocabularies_file_names:
            if vocabulary_file_name == '.DS_Store':  # For MacOS users skip .DS_Store-file
                continue  # generated.
            full_path = vocabularies_dir_path + '/' + vocabulary_file_name
            word_class = vocabulary_file_name.replace('.txt', '')
            self.load_vocabulary(full_path, word_class)
            i += 1

    def load_vocabulary(self, file_path, word_class):
        """
        Return dictionary of imported vocabularies lists provided by @Aitslab.
        """
        vocab_list = [row.strip() for row in
                      open(file_path)]
        self.vocabs_col_dict.update({word_class:
                                     vocab_list})
        self.word_classes.update(word_class)

    def load_patterns(self):
        self.patterns_dict = {'chemical_antiviral':
                              r'(?i)\b\S*vir\b'
                              }
        for word_class in self.patterns_dict:
            self.word_classes.update(word_class)

    def load_metadata(self, metadata_file_path):
        """
        Returns list with metadata and dictionary with sha as keys and indices of metadata list as values.
        """
        metadata_frame = pd.read_csv(metadata_file_path,
                                     na_filter=False,
                                     engine='python')
        self.metadata_list = metadata_frame.to_dict('records')
        index = 0
        for data in self.metadata_list:
            shas = data['sha'].split('; ', 1)
            for sha in shas:
                self.metadata_indices_dict.update({sha: index})
            index += 1

    def tag(self):
        article_paths = os.listdir(self.articles_directory_name)
        for article_name in article_paths:
            if article_name == '.DS_Store':  # For MacOS users skip .DS_Store-file
                continue  # generated.
            full_path = self.articles_directory_name + '/' + article_name
            with open(full_path) as article:
                article_dict = json.load(article)
            # Finds index of metadata that matches with sha of article_name
            # (without '.JSON' part.)
            metadata_index = self.metadata_indices_dict[
                article_name.replace('.json', '')]
            metadata_dict = self.metadata_list[metadata_index]
            self.process_article(article_dict, metadata_dict)

    def process_article(self, article_dict, metadata_dict):
        """
        Process article for each section and paragraph and generate pub-annotations for export to file.
        """
        file_index = 0
        metadata_info = obtain_metadata_args(metadata_dict)
        sections = ['metadata', 'abstract', 'body_text']
        for section in sections:
            if section == 'metadata':
                section_paragraphs = [article_dict[section]['title']]
                section = 'title'
            else:
                section_paragraphs = [section['text'] for section in
                                      article_dict[section]]
            if not bool(section_paragraphs):
                section_paragraphs = ['']
            for paragraph in section_paragraphs:
                self.tag_paragraph(paragraph)
                denotation = self.get_paragraph_denotation(metadata_dict['url'])
                if not re.fullmatch(r'\[\]', denotation): # Uncomment in order to filter out matches
                    annotation = construct_pubannotation(metadata_info,
                                                     file_index,
                                                     paragraph,
                                                     denotation)
                    export_pubannotation(metadata_info[0],
                                          file_index,
                                          section,
                                          annotation)
                    file_index += 1  # Increment with each file

    def tag_paragraph(self, paragraph):
        """
        For a paragraph, iterate through all vocabularies and patterns and tag using corresponding regex-pattern.
        """
        self.paragraph_matches.clear()
        for vocabulary in self.vocabs_col_dict:
            for word in self.vocabs_col_dict[vocabulary]:
                pattern = fr'(?i)\b{word}(es|s)?\b'
                self.tag_pattern(pattern, paragraph, vocabulary)

        for word_class in self.patterns_dict:
            self.tag_pattern(self.patterns_dict[word_class], paragraph, word_class)

    def tag_pattern(self, pattern, text, word_class):
        """
        For a particular pattern, find matches in paragraph and add to 'paragraph_matches' dictionary, if match is
        prioritized.
        """
        for match in re.finditer(pattern, text):
            is_priority = self.is_match_priority(pattern, match.group(0), word_class)
            if is_priority:
                self.paragraph_matches.update({match: word_class})

    def is_match_priority(self, pattern, new_word_match, word_class):
        """
        Checks priorites of tagging for vocabularies. For 'Virus_SARS-CoV-2' and 'Disease_COVID-19' if already pattern
        matches with existing match in 'paragraph_matches' then only the longest match will be kept in the dictionary.
        Returns 'True' if new match is to be added (prioritized).
        """
        for match in self.paragraph_matches:
            word_match = match.group(0)
            if word_class == 'Virus_SARS-CoV-2' or word_class == 'Disease_COVID-19':
                prev_tagged = re.match(pattern, word_match)
                if prev_tagged:
                    longest_match = max(new_word_match, word_match, key=len)
                    if longest_match == new_word_match:
                        del self.paragraph_matches[match]
                        return True
                    return False
                return True
        return True

    def get_paragraph_denotation(self, url):
        """
        Constructs complete string denotation for a paragraph.
        """
        denotations = []
        for match in self.paragraph_matches:
            print(url)
            print(match)
            denotations.append(construct_denotation(self.paragraph_matches[match],
                                                    str(match.start()),
                                                    str(match.end()), url))
        return concat_denotations(denotations)

    def get_word_classes(self):
        return self.word_classes
