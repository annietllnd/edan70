from src.dictionarytagger import DictionaryTagger
from src.pubannotationevaluator import PubannotationEvaluator


def main():
    """
    Main program.
    """
    # Tagging
    json_articles_dir_path = 'data/comm_use_subset_100'
    metadata_file_path = 'data/metadata_comm_use_subset_100.csv'
    vocabularies_dir_path = 'data/git add supplemental_files'
    word_classes_list = ['Virus_SARS-CoV-2', 'Disease_COVID-19']
    tagger = DictionaryTagger(json_articles_dir_path, metadata_file_path, vocabularies_dir_path, word_classes_list)
    tagger.tag()

    # Evaluation
    tagger_output_dir_path = 'out/'
    true_output_dir_path = 'out/'
    evaluator = PubannotationEvaluator(tagger_output_dir_path, true_output_dir_path)
    evaluator.evaluate()


if __name__ == '__main__':
    main()