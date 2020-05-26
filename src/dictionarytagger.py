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
import string
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
    print_progress_bar(nbr_articles_processed, total_articles, prefix='TAGGER PROGRESS\t\t', suffix='COMPLETE')


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Author: StackOverflow
            User Greenstick
            Question 30740258
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='', flush=True)
    # Print New Line on Complete
    if iteration == total:
        print()


class DictionaryTagger:
    """
    DictionaryTagger uses paths as arguments for the constructor in order to find all the necessary input data which is
    used to save date necassary for tagging.
    """
    def __init__(self, json_articles_dir_path, metadata_file_path, vocabularies_dir_path):
        self.articles_directory_name = json_articles_dir_path
        self.vocabs_col_dict = dict()
        self.rules_dict = dict()
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
        i = 0
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
        self.rules_dict = {'chemical_antiviral':
                           r'(?i)\b\S*vir\b'
                           }
        for word_class in self.rules_dict:
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
        case_insensitive_regex = r'(?i)'
        hyphen_or_whitespace_or_both_regex = r'(\s|\-\s?)'
        opt_plural_regex = r'(es|s)?'
        boundary_regex = r'\b'
        for vocabulary in self.vocabs_col_dict:
            for word in self.vocabs_col_dict[vocabulary]:
                pattern = case_insensitive_regex + boundary_regex
                if True in [character in word for character in string.whitespace]:
                    composite_words = word.split()
                    for composite_word in composite_words:
                        if composite_word == composite_words[-1]:
                            pattern += composite_word + opt_plural_regex + boundary_regex
                        else:
                            pattern += composite_word + hyphen_or_whitespace_or_both_regex
                else:
                    pattern += word + opt_plural_regex
                self.__tag_pattern(pattern, paragraph, vocabulary)

        for word_class in self.rules_dict:
            self.__tag_pattern(self.rules_dict[word_class], paragraph, word_class)

    def __tag_pattern(self, pattern, text, word_class):
        """
        For a particular pattern, find matches in paragraph and add to 'paragraph_matches' dictionary, if match is
        prioritized.
        """
        temp_paragraph_matches = dict()
        for match in re.finditer(pattern, text):
            is_priority = self.__is_match_priority(match, word_class)
            if is_priority:
                temp_paragraph_matches.update({match: word_class})
        self.paragraph_matches.update(temp_paragraph_matches)

    def __is_match_priority(self, new_match, new_word_class):
        """
        Checks priorities of tagging for vocabularies. For 'Virus_SARS-CoV-2' and 'Disease_COVID-19' if pattern already
        matches with existing match in 'paragraph_matches' then only the longest match will be kept in the dictionary.
        If the the word class matches with a previously match word in word class the longest match will be kept.
        Returns 'True' if new match is to be added (prioritized).
        """
        temp_paragraph_matches = self.paragraph_matches.copy()
        for prev_match in temp_paragraph_matches:
            prev_word_class = temp_paragraph_matches[prev_match]
            is_virus_disease_rule = (new_word_class == 'Virus_SARS-CoV-2' and prev_word_class == 'Disease_COVID-19') or\
                                    (prev_word_class == 'Virus_SARS-CoV-2' and new_word_class == 'Disease_COVID-19')
            new_word_match = new_match.group(0)
            prev_word_match = prev_match.group(0)
            if prev_word_match == new_word_match:
                continue

            if prev_word_class == new_word_class:
                candidate_match = self.is_longest_match(new_match, prev_match)
                if candidate_match:
                    continue
                else:
                    return False
            elif is_virus_disease_rule:
                candidate_match = self.is_longest_match(new_match, prev_match)
                if candidate_match:
                    continue
                else:
                    return False
        return True

    def is_longest_match(self, new_match, prev_match):
        """
        Returns true if new match is equally long or longer than prev_match for a common span and if words don't match.
        """
        new_word_match = new_match.group(0)
        prev_word_match = prev_match.group(0)
        if prev_word_match == new_word_match:
            return True
        new_pattern = new_match.re
        prev_pattern = prev_match.re
        is_span_overlap = ((prev_match.start() <= new_match.end() and prev_match.end() >= new_match.start()) or
                           (prev_match.start() >= new_match.end() and prev_match.end() <= new_match.start()))
        shortest_word = min(new_word_match, prev_word_match, key=len)
        if shortest_word == new_word_match:
            prev_tagged = re.search(new_pattern, prev_word_match)
            if prev_tagged and is_span_overlap:
                return False
        else:
            prev_tagged = re.search(prev_pattern, new_word_match)
            if prev_tagged and is_span_overlap:
                del self.paragraph_matches[prev_match]
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
