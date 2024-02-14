"""Script to detect bird sounds in a .wav recording file and print the detected bird species and their details."""
import os
from datetime import datetime
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import wikipediaapi


def sound_detector(file_name, lat, lon):
    """
    Detects bird sounds in a recording file.

    Args:
        file_name (str): The name of the recording file.
        lat (float): The latitude of the recording location.
        lon (float): The longitude of the recording location.

    Returns:
        list: A list of bird sound detections.

    """
    analyzer = Analyzer()
    date = datetime.fromtimestamp(os.path.getctime(file_name))
    recording = Recording(
        analyzer,
        file_name,
        lat=lat,
        lon=lon,
        date=datetime(year=date.year, month=date.month, day=date.day),
        min_conf=0.25,
    )
    recording.analyze()
    return recording.detections


def load_names_species(italian_species_filename):
    """
    Loads the Italian names of bird species from a file.

    Args:
        italian_species_filename (str): The path to the file containing Italian species names.

    Returns:
        dict: A dictionary mapping scientific names to Italian names.

    """
    italian_species_dict = {}
    if not os.path.exists(italian_species_filename):
        open(italian_species_filename, 'w', encoding='utf-8').close()
    else:
        with open(italian_species_filename, 'r', encoding='utf-8') as namesfile:
            for italian_name in namesfile.readlines():
                a, b = italian_name.split('|')
                italian_species_dict[a] = b.split('\n')[0]
    return italian_species_dict


def save_names_species(italian_species_dict, detections_list, italian_species_filename):
    """
    Saves the Italian names of newly detected bird species to a file.

    Args:
        italian_species_dict (dict): A dictionary mapping scientific names to Italian names.
        detections_list (list): A list of bird sound detections.
        italian_species_filename (str): The path to the file containing Italian species names.

    """
    with open(italian_species_filename, 'a', encoding='utf-8') as namesfile:
        wiki_wiki = wikipediaapi.Wikipedia(
            language='it', extract_format=wikipediaapi.ExtractFormat.HTML, user_agent='bird-detector')
        for detection in detections_list:
            if not italian_species_dict.get(detection["scientific_name"]):
                page_py = wiki_wiki.page(detection["scientific_name"])
                if page_py.exists():
                    italian_species_dict[detection["scientific_name"]] = page_py.text[9:250].split('<')[0].split(',')[0].title()
                    namesfile.write(f'{detection["scientific_name"]}|{italian_species_dict[detection["scientific_name"]]}\n')


def print_detections(italian_species_dict, detections_list):
    """
    Prints the detected bird species and their details.

    Args:
        italian_species_dict (dict): A dictionary mapping scientific names to Italian names.
        detections_list (list): A list of bird sound detections.

    """
    print('\nDetected:')
    for detection in detections_list:
        print(italian_species_dict[detection["scientific_name"]] + ':',
              detection["start_time"], detection["end_time"], detection["confidence"])


if __name__ == '__main__':
    FILENAME = str(input('Insert recording name: '))
    latitude, longitude = 45.65423642845939, 13.812502298723128  # Ts
    ITALIAN_SPECIES_FILENAME = "italian_species_names.txt"
    detections = sound_detector(FILENAME, latitude, longitude)
    italian_names = load_names_species(ITALIAN_SPECIES_FILENAME)
    print('\nSpecies dictionary\n', italian_names)
    save_names_species(italian_names, detections, ITALIAN_SPECIES_FILENAME)
    print_detections(italian_names, detections)
