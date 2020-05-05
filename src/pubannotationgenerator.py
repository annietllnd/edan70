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

import os
import re
import json


def construct_pubannotation(metadata_info, section_index, text, denotation):
    """
    Returns a string in pub-annotation format.
    """
    cord_uid = "\"cord_uid\":\"" + metadata_info[0] + "\", "

    source_x = "\"sourcedb\":\"" + metadata_info[1] + "\", "

    pmcid = "\"sourceid\":\"" + metadata_info[2] + "\", "

    divid = "\"divid\":" + str(section_index) + ", "

    text = "\"text\":\"" + text + "\", "

    project = "\"project\":\"cdlai_CORD-19\", "

    denotations_str = "\"denotations\":" + denotation

    return "{" + cord_uid + source_x + pmcid + divid + text + project + denotations_str + "}"


def concat_denotations(denotations):
    """
    Returns a complete denotation string of all separate denotations in
    list parameter, or an empty string if there where no elements in the
    list.
    """
    if not bool(denotations):
        return "[]"

    full_denotation = ''

    for denotation in denotations:
        if denotation == denotations[-1]:
            full_denotation += denotation
        else:
            full_denotation += denotation + ", "
    return "[" + full_denotation + "]"


def construct_denotation(idd, begin, end, url):
    """
    Returns a string denotation for a single match.
    """
    idd = "\"id\":\"" + idd + "\", "

    span = "\"span\":{\"begin\":" + begin + "," + "\"end\":" + end + "}, "

    obj = "\"obj\":\"" + url + "\""
    denotation = "{" + idd + span + obj + "}"
    return denotation


class PubannotationGenerator:
    def __init__(self, pubannotations_dict,output_dir_path):
        self.pubannotations_dict = pubannotations_dict
        self.output_dir_path = output_dir_path

    def generate(self):
        for pubannotation_dict in self.pubannotations_dict:
            print(pubannotation_dict['metadata_info'][0])
            denotation = self.get_paragraph_denotation(pubannotation_dict['matches'],pubannotation_dict['url'])
            if not re.fullmatch(r'\[\]', denotation): # Uncomment in order to filter out only matches
                annotation = construct_pubannotation(pubannotation_dict['metadata_info'],
                                                      pubannotation_dict['file_index'],
                                                      pubannotation_dict['paragraph_text'],
                                                      denotation)
                self.export_pubannotation(pubannotation_dict['metadata_info[0]'],
                                      pubannotation_dict['file_index'],
                                      pubannotation_dict['section_name'],
                                      annotation)

    def get_paragraph_denotation(self, paragraph_matches, url):
        """
        Constructs complete string denotation for a paragraph.
        """
        denotations = []
        for match in self.paragraph_matches:
            print(url)
            print(match)
            denotations.append(construct_denotation(self.paragraph_matches[match],
                                                    str(match.start()),
                                                    str(match.end()), url))
        return concat_denotations(denotations)

    def export_pubannotation(self, idd, file_index, section, annotation):
        """
        Export pub-annotation string to corresponding section file.
        """
        file_name = idd + '-' + str(file_index) + '-' + section
        full_path = self.output_dir_path + file_name + '.json'
        text_file = open(full_path, 'wt')
        text_file.write(annotation)
        text_file.close()
