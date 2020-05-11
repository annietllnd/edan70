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
     - Should we check correct word class?
"""
import os
import json
# true_positives = some_function() # number of true positives
# false_positives = some_other_function() # number of false positives
# true_negatives = other_function() # number of true negatives
# false_negatives = last_one() # number of false negatives
# for any is_checked = False in tagger_output_dict -> False positives
# for any is_checked = False in true_output_dict -> False negatives


def print_progress(nbr_pubannotations_evaluated, total_pubannotations):
    """
    Prints estimated progress based on number of total articles and number of articles processed.
    """
    print_progress_bar(nbr_pubannotations_evaluated,
                       total_pubannotations,
                       prefix='EVALUATION PROGRESS\t',
                       suffix='COMPLETE')


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
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\n', flush=True)
    # Print New Line on Complete
    if iteration == total:
        print()


class PubannotationEvaluator:
    """
    PubAnnotationEvaluator evaluates output compared to a true output, the arguments are the directory paths to the
    location of the outputs and a set containing what word classes/dictionaries to be evaluated.
    """
    def __init__(self, tagger_output_dir_path, true_output_dir_path, word_classes_set):
        self.tagger_output_dicts = dict()
        self.true_output_dicts = dict()
        self.word_classes_result_dict = dict()
        self.recall_values = list()
        self.precision_values = list()

        self.word_classes_set = word_classes_set
        self.true_positives = self.true_negatives = self.false_positives = self.false_negatives = \
            self.nbr_true_entities = self.recall_value = self.precision_value = self.total_true_positives = \
            self.total_false_positives = self.total_false_negatives = self.output_nbr = 0

        self.__generate_result_dict(self.word_classes_set)

        self.__load_output(tagger_output_dir_path, 1)
        self.__load_output(true_output_dir_path, 0)

        self.processes_total = len(self.tagger_output_dicts) + len(self.word_classes_result_dict)

    def __generate_result_dict(self, word_classes_set):
        """
        Initializes a dictionary containing all the results for respective word class.
        """
        for word_class in word_classes_set:
            self.word_classes_result_dict[word_class] = {'true_positives': 0,
                                                         'true_negatives': 0,
                                                         'false_positives': 0,
                                                         'false_negatives': 0
                                                         }

    def __load_output(self, dir_output_path, is_tagger_output):
        """
        Loads output files from a given directory in to corresponding dictionary. Second argument indicates if it is
        the true output or the output to be evaluated.
        """
        output_paths = os.listdir(dir_output_path)
        for pubannotation_file_name in output_paths:
            if pubannotation_file_name == '.DS_Store':  # For MacOS users skip .DS_Store-file
                continue                                # generated.
            full_path = dir_output_path + pubannotation_file_name
            with open(full_path) as pubannotation_obj:
                pubannotation_dict = json.loads(pubannotation_obj.read())
                pubannotation_dict.update({'is_checked': False})
                if is_tagger_output:
                    self.tagger_output_dicts.update({pubannotation_file_name: pubannotation_dict})
                else:
                    self.true_output_dicts.update({pubannotation_file_name: pubannotation_dict})

    def evaluate(self):
        """
        Evaluates outputs compared to true outputs.
        """
        self.__compare_outputs()
        self.__evaluate_word_class()
        self.__calculate_micro()
        self.__print_result('MICRO')
        self.__calculate_macro()
        self.__print_result('MACRO')
        self.__calculate_harmonic_mean()

    def __compare_outputs(self):
        """
        Iterates through all outputs to be compared to through output and compare output denotations.
        """
        for cord_uid in self.tagger_output_dicts:
            print_progress(self.output_nbr, self.processes_total)
            tagger_pubannotation = self.tagger_output_dicts[cord_uid]
            if(cord_uid in self.true_output_dicts):
                true_pubannotation = self.true_output_dicts[cord_uid]
                word_classes_list = [denotations_list_element['id'] for denotations_list_element in
                                      true_pubannotation['denotations']]
            else:
                continue
            self.__compare_output(tagger_pubannotation['denotations'],
                                  true_pubannotation['denotations'],
                                  cord_uid,
                                  word_classes_list)
            self.output_nbr += 1
        print_progress(self.output_nbr, self.processes_total)

    def __compare_output(self, tagger_denotations, true_denotations, cord_uid, word_classes_list):
        """
        Compares denotations with true denotations, false negatives field are incremented if there is a an existing
        match in true denotations that does not exist in denotations to be compared, and only for the word classes
        existing in the list argument. When a PubAnnotations is checked the field 'is_checked' is set to True which
        helps to calculate false positives and false negatives. If two denotations are matching in span true positives
        filed will be incremented in the result dictionary.
        """
        if not bool(tagger_denotations) or not bool(true_denotations):
            if not bool(tagger_denotations) and bool(true_denotations):  # before it compared when both were empty
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
                    # Might want to change to a safer implementation where we don't depend on an ordered
                    # word_classes_list. TODO
                    if(word_classes_list[i] in self.word_classes_result_dict.keys()):
                        self.word_classes_result_dict[word_classes_list[i]]['true_positives'] += 1
                        self.tagger_output_dicts[cord_uid].update({'is_checked': True})
                        self.true_output_dicts[cord_uid].update({'is_checked': True})
                i += 1

    def __evaluate_word_class(self):
        """
        Evaluates results for each word class.
        """
        for word_class in self.word_classes_result_dict:
            print_progress(self.output_nbr, self.processes_total)
            false_positives_result = 0
            false_negatives_result = 0
            for tagger_pubannotation in self.tagger_output_dicts.values():
                if(tagger_pubannotation['denotations'] != [] and tagger_pubannotation['denotations'][0]['id'] ==
                        word_class and tagger_pubannotation['is_checked'] is False):
                    false_positives_result += 1

            self.word_classes_result_dict[word_class]['false_positives'] = false_positives_result

            for true_pubannotation_dict in self.true_output_dicts.values():

                if(true_pubannotation_dict['denotations'] != [] and true_pubannotation_dict['denotations'][0]['id'] ==
                        word_class and true_pubannotation_dict['is_checked'] is False):
                    false_negatives_result += 1

            self.word_classes_result_dict[word_class]['false_negatives'] = false_negatives_result

            self.__precision(word_class)
            self.__recall(word_class)
            self.__print_result(word_class)
            self.output_nbr += 1
        print_progress(self.output_nbr, self.processes_total)

    def __precision(self, word_class):
        """
        Calculates precision figure.
        """
        true_positives = self.word_classes_result_dict[word_class]['true_positives']
        false_positives = self.word_classes_result_dict[word_class]['false_positives']
        self.total_true_positives += true_positives
        self.total_false_positives += false_positives
        sum_value = true_positives + false_positives
        if sum_value:
            self.precision_value = true_positives / sum_value
            self.precision_values.append(self.precision_value)
        else:
            print('########### WARNING ###########')
            print(f'{word_class} found no match, the precision result can be misleading')
            print("########### WARNING ###########")
            print('\n')
            self.precision_values.append(0)
            self.precision_value = 0

    def __recall(self, word_class):
        """
        Calculates recall figure.
        """
        true_positives = self.word_classes_result_dict[word_class]['true_positives']
        false_negatives = self.word_classes_result_dict[word_class]['false_negatives']
        self.total_false_negatives += false_negatives
        sum_value = true_positives + false_negatives
        if sum_value:
            self.recall_value = true_positives / sum_value
            self.recall_values.append(self.recall_value)
        else: 
            print('########### WARNING ###########')
            print(f"'{word_class}' found no match, the recall result can be misleading")
            print('########### WARNING ###########')
            print('\n')
            self.precision_values.append(0)
            self.recall_value = 0

    def __calculate_micro(self):
        """
        Calculates micro figure.
        """
        self.precision_value = self.total_true_positives / (self.total_true_positives + self.total_false_positives)
        self.recall_value = self.total_true_positives / (self.total_true_positives + self.total_false_negatives)

    def __calculate_macro(self):
        """
        Calculates macro figure.
        """
        self.precision_value = 0
        self.recall_value = 0
        for precision_value in self.precision_values:
            self.precision_value += precision_value
        for recall_value in self.recall_values:
            self.recall_value += recall_value
        self.precision_value /= len(self.precision_values)
        self.recall_value /= len(self.recall_values)

    def __calculate_harmonic_mean(self):
        """
        Calculates harmonic mean/F1 score figure.
        """
        harmonic_mean = (2*self.precision_value*self.recall_value) / (self.precision_value + self.recall_value)
        print(f'#########\tHARMONIC MEAN RESULT:\t###########')
        print(f'Harmonic mean:\t{harmonic_mean * 100:.0f}%')

    def __print_result(self, word_class):
        """
        Prints result for a given section/word class.
        """
        print(f'\n\n#########\t{word_class.upper()} PRECISION & RECALL RESULT:\t###########')
        print('\n')
        print(f'Precision:\t{self.precision_value * 100:.0f}%')
        print(f'Recall:\t\t{self.recall_value * 100:.0f}%')
        print('\n')
