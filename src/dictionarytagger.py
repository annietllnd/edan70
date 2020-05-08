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
"""

import os
import json
import re
import pandas as pd


def obtain_metadata_args(metadata_dict):
    """
    Returns list of necessary columns from kaggle COVID-19 metadata dictionary. Index 0 gives cord_uid, index 1 gives
    source_x, index 2 gives pmcid.
    """
    cord_uid = metadata_dict['cord_uid']
    source_x = metadata_dict['source_x']
    pmcid = metadata_dict['pmcid']
    metadata_info = [cord_uid, source_x, pmcid]
    return metadata_info


def print_progress(nbr_articles_processed, total_articles):
    """
    Prints estimated progress based on number of total articles and number of articles processed.
    """
    print(f'TAGGER ESTIMATED PROGRESS: {nbr_articles_processed/total_articles*100:.2f}%')


class DictionaryTagger:
    """
    DictionaryTagger uses paths as arguments for the constructor in order to find all the necessary input data which is
    used to save date necassary for tagging.
    """
    def __init__(self, json_articles_dir_path, metadata_file_path, vocabularies_dir_path):
        self.articles_directory_name = json_articles_dir_path
        self.vocabs_col_dict = dict()
        self.patterns_dict = dict()
        self.metadata_indices_dict = dict()
        self.paragraph_matches = dict()
        self.pubannotations_dict = dict()
        self.metadata_list = list()
        self.word_classes = set()

        self.__load_vocabularies(vocabularies_dir_path)
        self.__load_patterns()
        self.__load_metadata(metadata_file_path)

    def __load_vocabularies(self, vocabularies_dir_path):
        """
        Uses path in order to find all vocabularies/dictionaries containing the words to be tagged in the articles.
        """
        vocabularies_file_names = os.listdir(vocabularies_dir_path)
        i = 0;
        for vocabulary_file_name in vocabularies_file_names:
            if vocabulary_file_name == '.DS_Store':  # For MacOS users skip .DS_Store-file
                continue  # generated.
            full_path = vocabularies_dir_path + vocabulary_file_name
            word_class = vocabulary_file_name.replace('.txt', '')
            self.__load_vocabulary(full_path, word_class)
            i += 1

    def __load_vocabulary(self, file_path, word_class):
        """
        Opens a vocabulary/dictionary containing the words to be tagged in the articles and saves them in a list which
        is added to a dictionary using the word class correspondig the filename as key. Word classes are added to a set.
        """
        vocab_list = [row.strip() for row in
                      open(file_path)]
        self.vocabs_col_dict.update({word_class:
                                     vocab_list})
        self.word_classes.add(word_class)

    def __load_patterns(self):
        """
        Save patterns in same fashion as vocabularies/dictionaries in a dictionary. Word classes are added to a set.
        Pattern 1. 'chemical_antiviral' tags all words ending in 'vir'.
        """
        self.patterns_dict = {'chemical_antiviral':
                              r'(?i)\b\S*vir\b'
                              }
        for word_class in self.patterns_dict:
            self.word_classes.add(word_class)

    def __load_metadata(self, metadata_file_path):
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
        """
        Iterate all articles and tag them.
        """
        article_paths = os.listdir(self.articles_directory_name)
        article_nbr = 0
        articles_total = len(article_paths)
        for article_name in article_paths:
            print_progress(article_nbr, articles_total)
            if article_name == '.DS_Store':  # For MacOS users skip .DS_Store-file
                continue  # generated.
            full_path = self.articles_directory_name + article_name
            with open(full_path) as article:
                article_dict = json.load(article)
            # Finds index of metadata that matches with sha of article_name
            # (without '.JSON' part.)
            metadata_index = self.metadata_indices_dict[article_dict['paper_id']]
            metadata_dict = self.metadata_list[metadata_index]
            self.__process_article(article_dict, metadata_dict)
            article_nbr += 1
        print_progress(article_nbr, articles_total)

    def __process_article(self, article_dict, metadata_dict):
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
                self.__tag_paragraph(paragraph)
                self.pubannotations_dict.update({f'{metadata_info[0]}-{str(file_index)}-{section}':
                                                {'matches': self.paragraph_matches.copy(),
                                                 'file_index': file_index,
                                                 'paragraph_text': paragraph,
                                                 'section_name': section,
                                                 'url': metadata_dict['url'],
                                                 'metadata_info': metadata_info}})
                file_index += 1

    def __tag_paragraph(self, paragraph):
        """
        For a paragraph, iterate through all vocabularies and patterns and tag using corresponding regex-pattern.
        """
        self.paragraph_matches.clear()
        for vocabulary in self.vocabs_col_dict:
            for word in self.vocabs_col_dict[vocabulary]:
                pattern = fr'(?i)\b{word}(es|s)?\b'
                self.__tag_pattern(pattern, paragraph, vocabulary)

        for word_class in self.patterns_dict:
            self.__tag_pattern(self.patterns_dict[word_class], paragraph, word_class)

    def __tag_pattern(self, pattern, text, word_class):
        """
        For a particular pattern, find matches in paragraph and add to 'paragraph_matches' dictionary, if match is
        prioritized.
        """
        for match in re.finditer(pattern, text):
            is_priority = self.__is_match_priority(pattern, match.group(0), word_class)
            if is_priority:
                self.paragraph_matches.update({match: word_class})

    def __is_match_priority(self, pattern, new_word_match, word_class):
        """
        Checks priorities of tagging for vocabularies. For 'Virus_SARS-CoV-2' and 'Disease_COVID-19' if already pattern
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

    def get_word_classes(self):
        """
        Returns set of word classes.
        """
        return self.word_classes.copy()

    def get_pubannotations(self):
        """
        Returns dictionary with pubannotations information.
        """
        return self.pubannotations_dict.copy()
