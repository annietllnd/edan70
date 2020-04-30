import os
import json


class PubannotationEvaluator:
    def __init__(self, tagger_output_dir_path, true_output_dir_path):
        self.tagger_output_dicts = dict()
        self.true_output_dicts = dict()
        self.true_positives = self.true_negatives = self.false_positives = self.false_negatives = 0
        tagger_output_paths = os.listdir(tagger_output_dir_path)
        true_output_paths = os.listdir(true_output_dir_path)
        self.nbr_true_entities = len(true_output_paths)
        self.recall_value = 0
        self.precision_value = 0

        for pubannotation in tagger_output_paths:
            if pubannotation == '.DS_Store':  # For MacOS users skip .DS_Store-file
                continue  # generated.
            full_path = tagger_output_dir_path + '/' + pubannotation
            with open(full_path) as pubannotation:
                pubannotation_dict = json.load(pubannotation)
                pubannotation_dict.update({'is_checked': False})
                self.tagger_output_dicts.update({pubannotation_dict['cord_uid']: pubannotation_dict})

        for pubannotation in true_output_paths:
            if pubannotation == ".DS_Store":  # For MacOS users skip .DS_Store-file
                continue  # generated.
            full_path = true_output_dir_path + '/' + pubannotation
            with open(full_path) as pubannotation:
                pubannotation_dict = json.load(pubannotation)
                pubannotation_dict.update({'is_checked': False})
                self.true_output_dicts.update({pubannotation_dict['cord_uid']: pubannotation_dict})

    def evaluate(self):
        for cord_uid in self.tagger_output_dicts:
            tagger_pubannotation = self.tagger_output_dicts[cord_uid]
            true_pubannotation = self.true_output_dicts[cord_uid]
            self.compare_output(tagger_pubannotation['denotations'], true_pubannotation['denotations'], cord_uid)

        self.false_positives = sum(tagger_pubannotation['is_checked'] is False for tagger_pubannotation in
                                   self.tagger_output_dicts.values())
        self.false_negatives = sum(true_pubannotation['is_checked'] is False for true_pubannotation in
                                   self.true_output_dicts.values())
        self.recall()
        self.precision()
        self.print_result()

    def compare_output(self, tagger_denotations, true_denotations, cord_uid):
        if not bool(tagger_denotations) or not bool(true_denotations):
            if not bool(tagger_denotations) and not bool(true_denotations):
                self.false_negatives += 1
            self.tagger_output_dicts[cord_uid].update({'is_checked': True})
            self.true_output_dicts[cord_uid].update({'is_checked': True})
        for tagger_denotation in tagger_denotations:
            for true_denotation in true_denotations:
                if (tagger_denotation['span']['begin'] == true_denotation['span']['begin']
                        and tagger_denotation['span']['end'] == true_denotation['span']['end']):
                    self.true_positives += 1
                    self.tagger_output_dicts[cord_uid].update({'is_checked': True})
                    self.true_output_dicts[cord_uid].update({'is_checked': True})


# for any is_checked = False in tagger_output_dict -> False positives
# for any is_checked = False in true_output_dict -> False negatives
    def recall(self):
        sum_value = self.true_positives + self.false_negatives
        if sum_value:
            self.recall_value = self.true_positives / sum_value


    def precision(self):
        sum_value = self.true_positives + self.false_positives
        if sum_value:
            self.precision_value = self.true_positives / sum_value


    def print_result(self):
        print('#########\tPRECISION & RECALL RESULT:\t###########')
        print('\n')
        print(f"Precision:\t{self.precision_value * 100}%")
        print(f"Recall:\t{self.recall_value * 100}%")


    def compare_word_class(self, tagger_word_class, true_word_class):
        print('TODO')


    def compare_span(self, tagger_span_dict, true_span_dict):
        print('TODO')


# load json -> dict
# true_positives = some_function() # number of true positives
# false_positives = some_other_function() # number of false positives
# true_negatives = other_function() # number of true negatives
# false_negatives = last_one() # number of false negatives

# true_output_dictionary['denotations']['span'] == tagger_output_dictionary['denotations']['span']


def main():
    """
	Main program.
	"""
    path_1 = 'out/'
    path_2 = 'out/'
    eval_ = PubannotationEvaluator(path_1, path_2)
    eval_.evaluate()


if __name__ == '__main__':
    main()
