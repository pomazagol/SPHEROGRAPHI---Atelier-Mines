import os
import xml.etree.ElementTree as ET
import csv
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_osm_file(file_path):
    user_changesets = defaultdict(set)
    try:
        context = ET.iterparse(file_path, events=("end",))
        for event, elem in context:
            if elem.tag in {"node", "way", "relation"}:
                user = elem.get('user')
                uid = elem.get('uid')
                changeset = elem.get('changeset')

                if user and uid and changeset:
                    user_changesets[(user, uid)].add(changeset)

                elem.clear()  # Libérer de la mémoire
        print(f"Fichier {file_path} traité avec succès.")
    except ET.ParseError:
        print(f"Erreur lors de la lecture du fichier {file_path}.")

    return user_changesets

def parse_osm_files(directory):
    user_changesets = defaultdict(set)
    xml_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.xml')]

    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(parse_osm_file, file): file for file in xml_files}
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                for key, changesets in result.items():
                    user_changesets[key].update(changesets)
            except Exception as exc:
                print(f"Fichier {file} a généré une exception: {exc}")

    return user_changesets

def save_to_csv(user_changesets, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['user', 'uid', 'changeset_count'])
        writer.writerows([(user, uid, len(changesets)) for (user, uid), changesets in user_changesets.items()])
    print(f"Les résultats ont été enregistrés dans {output_file}.")

directory_path = '.'  # Dossier courant
output_file_path = 'utilisateurs_uniques_avec_changeset.csv'

print("Début du traitement des fichiers XML...")
user_changesets = parse_osm_files(directory_path)
save_to_csv(user_changesets, output_file_path)
print("Traitement terminé.")
