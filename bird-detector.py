"""Script to detect bird sounds in a .wav recording file and print the detected bird species
   and their details.
   
   Created by: Andrea Adelfio
   Created Date: 01-06-2023
   Modified Date: 14-02-2024
   To do:
   - gestire l'input del nome o dei nomi del file
   """
import os
from datetime import datetime
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import wikipediaapi


def sound_detector(file_name, lat, lon) -> list:
    """
    Detects bird sounds in a recording file.

    Args:
        file_name (str): The name of the recording file.
        lat (float): The latitude of the recording location.
        lon (float): The longitude of the recording location.

    Returns:
        list: A list of bird sound detections.

    """
    recording = Recording(
        Analyzer(),
        file_name,
        lat=lat,
        lon=lon,
        date=datetime.fromtimestamp(os.path.getctime(file_name)),
        min_conf=0.01,
    )
    recording.analyze()
    return recording.detections


def load_names_species(species_filename) -> dict:
    """
    Loads the Italian names of bird species from a file.

    Args:
        species_filename (str): The path to the file containing Italian species names.

    Returns:
        dict: A dictionary mapping scientific names to Italian names.

    """
    species_dict = {}
    if not os.path.exists(species_filename):
        open(species_filename, 'w', encoding='utf-8').close()
    else:
        with open(species_filename, 'r', encoding='utf-8') as namesfile:
            for name in namesfile.readlines():
                a, b, c = name.split('|')
                species_dict[a] = (c.split('\n')[0], b)
    print('\nSpecies dictionary\n', species_dict)
    return species_dict


def save_names_species(species_dict, detections_list, species_filename) -> dict:
    """
    Saves the Italian names of newly detected bird species to a file.

    Args:
        species_dict (dict): A dictionary mapping scientific names to Italian names.
        detections_list (list): A list of bird sound detections.
        species_filename (str): The path to the file containing Italian species names.

    """
    with open(species_filename, 'w', encoding='utf-8') as namesfile:
        wiki_wiki = wikipediaapi.Wikipedia(
            language='it', extract_format=wikipediaapi.ExtractFormat.HTML, user_agent='bird-detector')
        for detection in detections_list:
            if not species_dict.get(detection["scientific_name"]):
                page_py = wiki_wiki.page(detection["scientific_name"])
                if page_py.exists():
                    italian_name = page_py.summary.split('<b>')[1].split('<')[0].title()
                    species_dict[detection["scientific_name"]] = (italian_name, detection["common_name"])
        species_dict = dict(sorted(species_dict.items()))
        for scientific_name, names_tuple in species_dict.items():
            namesfile.write(f'{scientific_name}|{names_tuple[1]}|{names_tuple[0]}\n')
    return species_dict


def print_detections(species_dict, detections_list):
    """
    Prints the detected bird species and their details.

    Args:
        species_dict (dict): A dictionary mapping scientific names to Italian names.
        detections_list (list): A list of bird sound detections.

    """
    print('\nDetections:')
    for detection in detections_list:
        start_time = detection['start_time']
        end_time = detection['end_time']
        (italian_name, english_name) = species_dict[detection['scientific_name']]
        scientific_name = detection['scientific_name']
        confidence = round(detection['confidence'], 3)
        row = f"{start_time}s - {end_time}s -> {italian_name} ({scientific_name}, {english_name}) ({confidence})"
        print(row)


if __name__ == '__main__':
    FILENAMES = str(input('Insert recording name: ')).split(',')
    latitude, longitude = 45.65423642845939, 13.812502298723128  # Ts
    current_directory = os.path.dirname(os.path.abspath(__file__))
    SPECIES_FILENAME = os.path.join(current_directory, "species_names.txt")
    detections = []
    for FILENAME in FILENAMES:
        detections.extend(sound_detector(FILENAME, latitude, longitude))
    names = load_names_species(SPECIES_FILENAME)
    names = save_names_species(names, detections, SPECIES_FILENAME)
    print_detections(names, detections)
