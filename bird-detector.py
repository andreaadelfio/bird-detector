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


def load_names_species(italian_species_names):
    """
    Loads the Italian names of bird species from a file.

    Args:
        italian_species_names (str): The path to the file containing Italian species names.

    Returns:
        dict: A dictionary mapping scientific names to Italian names.

    """
    italian_names = {}
    if not os.path.exists(italian_species_names):
        open(italian_species_names, 'w').close()
    else:
        namesfile = open(italian_species_names, 'r')
        for italian_name in namesfile.readlines():
            a, b = italian_name.split('|')
            italian_names[a] = b.split('\n')[0]
        namesfile.close()
    return italian_names


def save_names_species(italian_names, detections, italian_species_names):
    """
    Saves the Italian names of newly detected bird species to a file.

    Args:
        italian_names (dict): A dictionary mapping scientific names to Italian names.
        detections (list): A list of bird sound detections.
        italian_species_names (str): The path to the file containing Italian species names.

    """
    namesfile = open(italian_species_names, 'a')
    wiki_wiki = wikipediaapi.Wikipedia(
        language='it', extract_format=wikipediaapi.ExtractFormat.HTML, user_agent='bird-detector')
    for detection in detections:
        if not italian_names.get(detection["scientific_name"]):
            page_py = wiki_wiki.page(detection["scientific_name"])
            if page_py.exists():
                italian_names[detection["scientific_name"]] = page_py.text[9:250].split('<')[0].split(',')[0].title()
                namesfile.write(f'{detection["scientific_name"]}|{italian_names[detection["scientific_name"]]}\n')
    namesfile.close()


def print_detections(italian_names, detections):
    """
    Prints the detected bird species and their details.

    Args:
        italian_names (dict): A dictionary mapping scientific names to Italian names.
        detections (list): A list of bird sound detections.

    """
    print('\nDetected:')
    for detection in detections:
        print(italian_names[detection["scientific_name"]] + ':',
              detection["start_time"], detection["end_time"], detection["confidence"])


if __name__ == '__main__':
    file_name = str(input('Insert recording name: '))
    lat, lon = 45.65423642845939, 13.812502298723128  # Ts
    italian_species_names = "italian_species_names.txt"
    detections = sound_detector(file_name, lat, lon)
    italian_names = load_names_species(italian_species_names)
    print('\nSpecies dictionary\n', italian_names)
    save_names_species(italian_names, detections, italian_species_names)
    print_detections(italian_names, detections)
