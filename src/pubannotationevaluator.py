"""
PubAnnotation evaluator for COVID-19

Authors:
    Annie Tallind, Lund University, Faculty of Engineering
    Kaggle ID: atllnd
    Github ID: annietllnd

    Sofi Flink, Lund University, Faculty of Engineering
    Kaggle ID: sofiflinck
    Github ID: obakanue

    TODO:
     - We have some fields that are currently not in use,
     or example nbr_true_entities which counts all files from true output for every class.
     - Try the evaluator with golden standard and retrieve result
     - Split code up if needed
     - Docs for member functions
     - Should we check correct word class?
     - Generate file with table of results?
"""

import os
import json


class PubannotationEvaluator:
    def __init__(self, tagger_output_dir_path, true_output_dir_path, word_classes_set):
        self.tagger_output_dicts = dict()
        self.true_output_dicts = dict()
        self.word_classes_result_dict = dict()
        self.recall_values = list()
        self.precision_values = list()
        self.word_classes_set = word_classes_set
        self.true_positives = self.true_negatives = self.false_positives = self.false_negatives = 0
        tagger_output_paths = os.listdir(tagger_output_dir_path)
        true_output_paths = os.listdir(true_output_dir_path)
        self.generate_result_dict(self.word_classes_set)
        self.nbr_true_entities = self.recall_value = self.precision_value = self.total_true_positives = \
            self.total_false_positives = self.total_false_negatives = 0

        for pubannotation_file_name in tagger_output_paths:
            if pubannotation_file_name == '.DS_Store':  # For MacOS users skip .DS_Store-file
                continue                                # generated.
            full_path = tagger_output_dir_path + pubannotation_file_name
            with open(full_path) as pubannotation_obj:
                pubannotation_dict = json.loads(pubannotation_obj.read())
                pubannotation_dict.update({'is_checked': False})
                self.tagger_output_dicts.update({pubannotation_dict['cord_uid']: pubannotation_dict})

        for file_name in true_output_paths:
            if file_name == ".DS_Store":  # For MacOS users skip .DS_Store-file
                continue  # generated.
            full_path = true_output_dir_path + file_name
            with open(full_path) as pubannotation:
                pubannotation_dict = json.load(pubannotation)
                for denotation in pubannotation_dict['denotations']:
                    word_class = denotation['id']
                    if word_class in word_classes_set:
                        self.word_classes_result_dict[word_class]['nbr_true_entities'] += 1
                pubannotation_dict.update({'is_checked': False})
                self.true_output_dicts.update({pubannotation_dict['cord_uid']: pubannotation_dict})

    def generate_result_dict(self, word_classes_set):
        for word_class in word_classes_set:
            self.word_classes_result_dict[word_class] = {'nbr_true_entities': 0,
                                                         'true_positives': 0,
                                                         'true_negatives': 0,
                                                         'false_positives': 0,
                                                         'false_negatives': 0
                                                         }

    def evaluate(self):
        print(self.true_output_dicts)
        for cord_uid in self.tagger_output_dicts:
            print(cord_uid)
            tagger_pubannotation = self.tagger_output_dicts[cord_uid]
            true_pubannotation = self.true_output_dicts[cord_uid]
            word_classes_list = [denotations_list_element['id'] for denotations_list_element in true_pubannotation['denotations']]
            
            self.compare_output(tagger_pubannotation['denotations'], true_pubannotation['denotations'], cord_uid, word_classes_list)
       
        for word_class in self.word_classes_result_dict:
            false_positives_result = 0
            false_negatives_result = 0
            for tagger_pubannotation in self.tagger_output_dicts.values():
                if(tagger_pubannotation['denotations'] != [] and tagger_pubannotation['denotations'][0]['id'] == word_class and tagger_pubannotation['is_checked'] is False):
                    false_positives_result += 1

            self.word_classes_result_dict[word_class]['false_positives'] = false_positives_result

            for true_pubannotation in self.true_output_dicts.values():

                if(true_pubannotation['denotations'] != [] and true_pubannotation['denotations'][0]['id'] == word_class and true_pubannotation['is_checked'] is False):
                    false_negatives_result += 1


            self.word_classes_result_dict[word_class]['false_negatives'] = false_negatives_result

            self.precision(word_class)
            self.recall(word_class)
            self.print_result(word_class)
        self.calculate_micro()
        self.print_result('MICRO')
        self.calculate_macro()
        self.print_result('MACRO')

    def compare_output(self, tagger_denotations, true_denotations, cord_uid, word_classes_list):
        if not bool(tagger_denotations) or not bool(true_denotations):
            if not bool(tagger_denotations) and bool(true_denotations): # before it compared when both were empty
                for word_class in word_classes_list:
                    if word_class in self.word_classes_set:
                        self.word_classes_result_dict[word_class]['false_negatives'] += 1
            self.tagger_output_dicts[cord_uid].update({'is_checked': True})
            self.true_output_dicts[cord_uid].update({'is_checked': True})
        for tagger_denotation in tagger_denotations:
            i = 0
            for true_denotation in true_denotations:
                if (tagger_denotation['span']['begin'] == true_denotation['span']['begin']
                        and tagger_denotation['span']['end'] == true_denotation['span']['end']):
                    self.word_classes_result_dict[word_classes_list[i]]['true_positives'] += 1
                    self.tagger_output_dicts[cord_uid].update({'is_checked': True})
                    self.true_output_dicts[cord_uid].update({'is_checked': True})
                i += 1

    # for any is_checked = False in tagger_output_dict -> False positives
    # for any is_checked = False in true_output_dict -> False negatives

    def precision(self, word_class):
        true_positives = self.word_classes_result_dict[word_class]['true_positives']
        false_positives = self.word_classes_result_dict[word_class]['false_positives']
        self.total_true_positives += true_positives
        self.total_false_positives += false_positives
        sum_value = true_positives + false_positives
        if sum_value:
            self.precision_value = true_positives / sum_value
            self.precision_values.append(self.precision_value.copy())
        else:
            print('########### WARNING ###########')
            print(f'{word_class} found no match, the result can be misleading')
            print("########### WARNING ###########")
            print('\n')
            self.precision_values.append(0)

    def recall(self, word_class):
        true_positives = self.word_classes_result_dict[word_class]['true_positives']
        false_negatives = self.word_classes_result_dict[word_class]['false_negatives']
        self.total_false_negatives += false_negatives
        sum_value = true_positives + false_negatives
        if sum_value:
            self.recall_value = true_positives / sum_value
            self.recall_values.append(self.recall_value.copy())
        else: 
            print('########### WARNING ###########')
            print(f"'{word_class}' found no match, the result can be misleading.")
            print('########### WARNING ###########')
            print('\n')
            self.precision_values.append(0)

    def calculate_micro(self):
        self.precision_value = self.total_true_positives / (self.total_true_positives + self.total_false_positives)
        self.recall_value = self.total_true_positives / (self.total_true_positives + self.total_false_negatives)

    def calculate_macro(self):
        self.precision_value = 0
        self.recall_value = 0
        for precision_value in self.precision_values:
            self.precision_value += precision_value
        for recall_value in self.recall_values:
            self.recall_value += recall_value
        self.precision_value /= len(self.precision_values)
        self.recall_value /= len(self.recall_values)

    def print_result(self, word_class):
        print(f'#########\t{word_class.upper()} PRECISION & RECALL RESULT:\t###########')
        print('\n')
        print(f'Precision:\t{self.precision_value * 100}%')
        print(f'Recall:\t\t{self.recall_value * 100}%')
        print('\n')

# load json -> dict
# true_positives = some_function() # number of true positives
# false_positives = some_other_function() # number of false positives
# true_negatives = other_function() # number of true negatives
# false_negatives = last_one() # number of false negatives

# true_output_dictionary['denotations']['span'] == tagger_output_dictionary['denotations']['span']
