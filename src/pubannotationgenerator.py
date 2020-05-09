"""
PubAnnotation generator for COVID-19

Authors:
    Annie Tallind, Lund University, Faculty of Engineering
    Kaggle ID: atllnd
    Github ID: annietllnd

    Sofi Flink, Lund University, Faculty of Engineering
    Kaggle ID: sofiflinck
    Github ID: obakanue
"""

import re
import os


def construct_pubannotation(metadata_info, section_index, text, denotation):
    """
    Returns a string in pub-annotation format.
    """
    cord_uid = "\n".ljust(4) + "\"cord_uid\": \"" + metadata_info[0] + "\","

    source_x = "\n".ljust(4) + "\"sourcedb\": \"" + metadata_info[1] + "\","

    pmcid = "\n".ljust(4) + "\"sourceid\": \"" + metadata_info[2] + "\","

    divid = "\n".ljust(4) + "\"divid\": " + str(section_index) + ","

    text = "\n".ljust(4) + "\"text\": \"" + text.replace('"', '\\"') + "\","

    project = "\n".ljust(4) + "\"project\": \"cdlai_CORD-19\", "

    denotations_str = "\n".ljust(4) + "\"denotations\": " + denotation

    return "{" + cord_uid + source_x + pmcid + divid + text + project + denotations_str + "}"


def concat_denotations(denotations):
    """
    Returns a complete denotation string of all separate denotations in
    list parameter, or an empty string if there where no elements in the
    list.
    """
    if not bool(denotations):
        return '[]'

    full_denotation = ''

    for denotation in denotations:
        if denotation == denotations[-1]:
            full_denotation += denotation
        else:
            full_denotation += denotation + ","
    return "[" + full_denotation + "\n".ljust(4) + "]\n"


def construct_denotation(idd, begin, end, url):
    """
    Returns a string denotation for a single match.
    """
    idd = "\n".ljust(12) + "\"id\": \"" + idd + "\", "

    span = "\n".ljust(12) + "\"span\": {\n".ljust(24) + "\"begin\":" + begin + ",\n".ljust(16) + "\"end\": " + end + \
           "\n".ljust(12) + "}, "

    obj = "\n".ljust(12) + "\"obj\": \"" + url + "\""
    denotation = "\n".ljust(8) + "{" + idd + span + obj + "\n".ljust(8) + "}"
    return denotation


def print_progress(nbr_pubannotations_processed, total_pubannotations):
    """
    Prints estimated progress based on number of total articles and number of articles processed.
    """
    print_progress_bar(nbr_pubannotations_processed, total_pubannotations, prefix='GENERATOR PROGRESS\t',
                       suffix='COMPLETE')


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
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


def get_paragraph_denotation(paragraph_matches, url):
    """
    Constructs complete string denotation for a paragraph.
    """
    denotations = []
    for match in paragraph_matches:
        denotations.append(construct_denotation(paragraph_matches[match],
                                                str(match.start()),
                                                str(match.end()), url))
    return concat_denotations(denotations)


class PubannotationGenerator:
    def __init__(self, pubannotations_dict,output_dir_path):
        self.pubannotations_dict = pubannotations_dict
        self.output_dir_path = output_dir_path
        os.chdir('..')

    def generate(self):
        pubannotation_nbr = 0
        pubannotations_total = len(self.pubannotations_dict)
        for pubannotation_key in self.pubannotations_dict:
            print_progress(pubannotation_nbr, pubannotations_total)
            denotation = get_paragraph_denotation(self.pubannotations_dict[pubannotation_key]['matches'],
                                                  self.pubannotations_dict[pubannotation_key]['url'])
            # if not re.fullmatch(r'\[\]', denotation): # Uncomment in order to filter out only matches
            annotation = construct_pubannotation(self.pubannotations_dict[pubannotation_key]['metadata_info'],
                                                 self.pubannotations_dict[pubannotation_key]['file_index'],
                                                 self.pubannotations_dict[pubannotation_key]['paragraph_text'],
                                                 denotation)
            self.__export_pubannotation(self.pubannotations_dict[pubannotation_key]['metadata_info'][0],
                                        self.pubannotations_dict[pubannotation_key]['file_index'],
                                        self.pubannotations_dict[pubannotation_key]['section_name'],
                                        annotation)
            pubannotation_nbr += 1
        print_progress(pubannotation_nbr, pubannotations_total)

    def __export_pubannotation(self, idd, file_index, section, annotation):
        """
        Export pub-annotation string to corresponding section file.
        """
        file_name = idd + '-' + str(file_index) + '-' + section
        full_path = self.output_dir_path + file_name + '.json'
        text_file = open(full_path, 'wt')
        text_file.write(annotation)
        text_file.close()
