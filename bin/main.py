"""
PubAnnotation program for COVID-19: Tagging articles, generating pubannotation files and evaluation using precision &
recall.

Authors:
    Annie Tallind, Lund University, Faculty of Engineering
    Kaggle ID: atllnd
    Github ID: annietllnd

    Sofi Flink, Lund University, Faculty of Engineering
    Kaggle ID: sofiflinck
    Github ID: obakanue

    TODO:
     - Generate file with table of results?
"""
import sys
from dictionarytagger import DictionaryTagger
from pubannotationgenerator import PubannotationGenerator
from pubannotationevaluator import PubannotationEvaluator

sys.path.append('../src')
sys.path.append('../output')


def main():
    """
    Main program.
    """
    # Tagging
    json_articles_dir_path = '../data/gold_standard_subset_10/'
    metadata_file_path = '../data/metadata_gold_standard_subset_10.csv'
    vocabularies_dir_path = '../data/dictionaries/'
    tagger = DictionaryTagger(json_articles_dir_path, metadata_file_path, vocabularies_dir_path)
    tagger.tag()
    word_classes_set = tagger.get_word_classes()
    # word_classes_set = {'Disease_COVID-19', 'Symptom_COVID-19', 'Virus_SARS-CoV-2'}  # Supported classes:
    #                                                                                   - 'chemical_antiviral'
    #                                                                                   - 'Disease_COVID-19'
    #                                                                                   - 'Symptom_Covid-19'
    #                                                                                   - 'Virus_SARS-CoV-2'
    
    # Generate Files
    output_dir_path = 'output/out_temp/'
    pubannotations_dict = tagger.get_pubannotations()
    pubgenerator = PubannotationGenerator(pubannotations_dict, output_dir_path)
    pubgenerator.generate()
    
    # Evaluation
    tagger_output_dir_path = 'output/out_temp/'
    true_output_dir_path = 'output/out_test_true/'
    evaluator = PubannotationEvaluator(tagger_output_dir_path, true_output_dir_path, word_classes_set)
    evaluator.evaluate()


if __name__ == '__main__':
    main()
