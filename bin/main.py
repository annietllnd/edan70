import sys
sys.path.append('../src')
sys.path.append('../output')
from dictionarytagger import DictionaryTagger
from pubannotationgenerator import PubannotationGenerator
from pubannotationevaluator import PubannotationEvaluator


def main():
    """
    Main program.
    """
    #### SUBSET 100 ####
    # Tagging
    json_articles_dir_path = 'data/comm_use_subset_100'
    metadata_file_path = 'data/metadata_comm_use_subset_100.csv'
    vocabularies_dir_path = 'data/dictionaries'
    tagger = DictionaryTagger(json_articles_dir_path, metadata_file_path, vocabularies_dir_path)
    tagger.tag()
    word_classes_set = tagger.get_word_classes()

    # Generate Files
    output_dir_path = 'output/out_filter/'
    pubannotations_dict = tagger.get_pubannotations()
    pubgenerator = PubannotationGenerator(pubannotations_dict, output_dir_path)
    pubgenerator.generate()

    # Evaluation
    # tagger_output_dir_path = 'output/out_all'
    # true_output_dir_path = 'output/' missing gold standard for subset
    # evaluator = PubannotationEvaluator(tagger_output_dir_path, true_output_dir_path, word_classes_set)
    # evaluator.evaluate()

    # #### SUBSET 10 GOLD STANDARD TEST ####
    # # Tagging
    # test_json_articles_dir_path = 'data/gold_standard_subset_10'
    # test_metadata_file_path = 'data/metadata_gold_standard_subset_10.csv'
    # test_tagger = DictionaryTagger(test_json_articles_dir_path, test_metadata_file_path, vocabularies_dir_path)
    # test_tagger.tag()
    # word_classes_set = test_tagger.get_word_classes()
    #
    # # Generate Files
    # output_dir_path = 'output/out_all/'
    # pubannotations_dict = test_tagger.get_pubannotations()
    # pubgenerator = PubannotationGenerator(pubannotations_dict, output_dir_path)
    # pubgenerator.generate()
    #
    # # Evaluation
    # tagger_output_dir_path = 'output/out_test'
    # true_output_dir_path = 'data/out_test_true'
    # evaluator = PubannotationEvaluator(tagger_output_dir_path, true_output_dir_path, word_classes_set)
    # evaluator.evaluate()

if __name__ == '__main__':
    main()
