import sys
sys.path.append('../src')
from dictionarytagger import DictionaryTagger
from pubannotationevaluator import PubannotationEvaluator


def main():
    """
    Main program.
    """
    # Tagging
    json_articles_dir_path = 'data/comm_use_subset_100'
    metadata_file_path = 'data/metadata_comm_use_subset_100.csv'
    vocabularies_dir_path = 'data/supplemental_files'
    word_classes_list = ['Virus_SARS-CoV-2', 'Disease_COVID-19']
    patterns_word_classes_list = ['chemical_antiviral']
    tagger = DictionaryTagger(json_articles_dir_path, metadata_file_path, vocabularies_dir_path, word_classes_list)
    #tagger.tag()

    # Evaluation
    tagger_output_dir_path = 'out/'
    true_output_dir_path = 'out/'
    word_classes_list.extend(patterns_word_classes_list)
    evaluator = PubannotationEvaluator(tagger_output_dir_path, true_output_dir_path, word_classes_list)
    evaluator.evaluate()


if __name__ == '__main__':
    main()
