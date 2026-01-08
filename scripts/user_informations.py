import csv
import requests
import time
import os

def get_osm_user_info(uid):
    url = f"https://api.openstreetmap.org/api/0.6/user/{uid}.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 410:
            print(f"Utilisateur {uid} n'existe plus (410 Gone).")
        else:
            print(f"Erreur {response.status_code} pour l'utilisateur {uid}")
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération des informations pour l'utilisateur {uid}: {e}")
        return None

def process_csv(input_csv, output_csv):
    with open(input_csv, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        users = list(reader)

    total_users = len(users)
    print(f"Total d'utilisateurs à traiter : {total_users}")

    with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['user', 'uid', 'changeset_count', 'account_created', 'description', 'contributions']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, user in enumerate(users, start=1):
            uid = user['uid']
            user_info = get_osm_user_info(uid)

            if user_info:
                user_data = user_info.get('user', {})
                row = {
                    'user': user['user'],
                    'uid': uid,
                    'changeset_count': user.get('changeset_count', 'N/A'),
                    'account_created': user_data.get('account_created'),
                    'description': user_data.get('description'),
                    'contributions': user_data.get('contributions')
                }
                writer.writerow(row)

            print(f"Progression : {index}/{total_users} utilisateurs traités.")
            time.sleep(1)  # Respecter les limites de taux de l'API

    print(f"Les informations des utilisateurs ont été écrites dans {output_csv}")

def main():
    # Lister les fichiers CSV dans le dossier courant
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

    if not csv_files:
        print("Aucun fichier CSV trouvé dans le dossier courant.")
        return

    # Afficher les fichiers disponibles et demander à l'utilisateur de faire un choix
    print("Fichiers CSV disponibles dans le dossier courant :")
    for index, csv_file in enumerate(csv_files, start=1):
        print(f"{index}. {csv_file}")

    try:
        choice = int(input("Veuillez entrer le numéro du fichier CSV que vous souhaitez utiliser : "))
        if 1 <= choice <= len(csv_files):
            input_csv = csv_files[choice - 1]
        else:
            print("Choix invalide.")
            return
    except ValueError:
        print("Entrée invalide. Veuillez entrer un numéro.")
        return

    # Définir le chemin du fichier de sortie
    output_csv = 'user_info.csv'

    # Traiter le fichier CSV
    process_csv(input_csv, output_csv)

if __name__ == "__main__":
    main()
