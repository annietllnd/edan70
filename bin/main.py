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
import time
# Problem with imports and running in terminal? Run 'python3 -m bin.main' instead of 'python3 bin/main'. Python does not
# save the paths and as such won't find the imports, an IDE will work this out for you when you assign
# working directory as edan70.




def main():
    """
    Main program.
    """
    start = time.time()
    # Tagging
    json_articles_dir_path = 'data/comm_use_subset_100/'
    metadata_file_path = 'data/metadata_comm_use_subset_100.csv'
    vocabularies_dir_path = 'data/dictionaries/'
    tagger = DictionaryTagger(json_articles_dir_path, metadata_file_path, vocabularies_dir_path)
    tagger.tag()
    word_classes_set = tagger.get_word_classes()
    # word_classes_set = {'Disease_COVID-19', 'Symptom_COVID-19', 'Virus_SARS-CoV-2'}  # Supported classes:
    #                                                                                   - 'chemical_antiviral'
    #                                                                                   - 'Disease_COVID-19'
    #                                                                                   - 'Symptom_Covid-19'
    #                                                                                   - 'Virus_SARS-CoV-2'
    
    # Generate Files
    output_dir_path = 'output/out_all/'
    pubannotations_dict = tagger.get_pubannotations()
    pubgenerator = PubannotationGenerator(pubannotations_dict, output_dir_path)
    pubgenerator.generate()
    
    # Evaluation
    tagger_output_dir_path = 'output/out_test/'
    true_output_dir_path = 'output/out_test_true/'
    evaluator = PubannotationEvaluator(tagger_output_dir_path, true_output_dir_path, word_classes_set)
    evaluator.evaluate()
    evaluator.print_all()
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))


if __name__ == '__main__':
    main()