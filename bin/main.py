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
from src.dictionarytagger import DictionaryTagger
from src.pubannotationgenerator import PubannotationGenerator
from src.pubannotationevaluator import PubannotationEvaluator
# Problem with imports and running in terminal? Run 'python3 -m bin.main' instead of 'python3 bin/main'. Python does not
# save the paths and as such won't find the imports, an IDE will work this out for you when you assign
# working directory as edan70.


def main():
    """
    Main program.
    """
    # Tagging
    json_articles_dir_path = 'edan70/data/gold_standard_subset_10/'
    metadata_file_path = 'edan70/data/metadata_gold_standard_subset_10.csv'
    vocabularies_dir_path = 'edan70/data/dictionaries/'
    tagger = DictionaryTagger(json_articles_dir_path, metadata_file_path, vocabularies_dir_path)
    #tagger.tag()
    #word_classes_set = tagger.get_word_classes()
    #word_classes_set = {'PROTEIN', 'SPECIES'}
    word_classes_set = {'Disease_COVID-19', 'Symptom_COVID-19', 'Virus_SARS-CoV-2', 'chemical_antiviral'}  # Supported classes:
    #                                                                                   - 'chemical_antiviral'
    #                                                                                   - 'Disease_COVID-19'
    #                                                                                   - 'Symptom_Covid-19'
    #                                                                                   - 'Virus_SARS-CoV-2'
    
    # Generate Files
    output_dir_path = 'output/out_temp/'
    pubannotations_dict = tagger.get_pubannotations()
    pubgenerator = PubannotationGenerator(pubannotations_dict, output_dir_path)
    #pubgenerator.generate()
    
    # Evaluation
    tagger_output_dir_path = 'edan70/output/out_test/'
    true_output_dir_path = 'edan70/output/out_test_true/'
    evaluator = PubannotationEvaluator(tagger_output_dir_path, true_output_dir_path, word_classes_set)
    evaluator.evaluate()
    for word_class in word_classes_set:
        print(f'CLASS: {word_class}')
        print(f'Total: {evaluator.get_total(word_class)}')
        print(f'True Positives: {evaluator.get_true_positives(word_class)}')
        print(f'False Positives: {evaluator.get_false_positives(word_class)}')
        print(f'False Negatives: {evaluator.get_false_negatives(word_class)}')


if __name__ == '__main__':
    main()