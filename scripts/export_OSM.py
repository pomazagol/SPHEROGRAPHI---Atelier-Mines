import os
import overpass
import time
import json
from datetime import datetime

#ci-dessus, déclaration des différentes librairies necessaires au programme (certaines ne sont pas/plus utilisées, car liées à des fonctions abandonnées)


api = overpass.API(timeout=600)                                                 #set le temps de calcul maximal d'overpass à 10 minutes


def run_from_file(file_path,file_save,output):                                  #fonction run from file
                                                                                #on vérifie si l'arborescence fichier données par l'utilisateur existe 
    if not os.path.isfile(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return                                                                  #sinon, on notifie l'erreur

                                                                                #On ouvre le fichier en lisant chaque ligne une par une
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        for line in lines:                                                      #pour chaque ligne
                                                                                #on retire les possibles espaces ou caractères invisibles qui perturberaient la query
            clean_line = line.strip()
            param = clean_line
            try :                                                               #on essaye (si un problème survient, le programme ne s'arretera pas et continuera avec la ligne suivante)
                print(f"Launching {line}")                                      #on notifie l'utilisateur du début de la query
                fetch_overpass(param,file_save,output)                          #on lance la fonction d'appelle de l'API
            except :
                print(f"Problème avec la requête de {line}")                    #si la fonction renvoie une erreur (charge serveur le plus souvent)
                with open(file_save+"\problem.txt","a") as f : 
                    f.write(line)
                    #break                                                      #on ouvre un dossier problem.txt (crée si il n'existe pas) et on écrit la ligne problématique
                time.sleep(15)                                                  #on ajoute 15 secondes d'attente pour ne pas surcharger le serveur 

def fetch_overpass(text,file_save,output):                                      #fonction de call d'api

    response = api.get(text, verbosity='meta', responseformat=output)           #on défini comment on appelle l'api overpass (via une query text, on veux un output type meta, en format défini par l'utilisateur)
    if type(response) == dict and output == 'geojson':                          #si la réponse est un dictionnaire (type du geojson), et l'output demandé est bien geojson
        naminggeojson(text,response,file_save)                                  #on lance la fonction naminggeojson (ligne 66) avec les paramètres text, response et file_save
        print(f"Processing success: {text}")                                    #une fois que naminggeojson est finie, on imprime processing succes {query}
    elif output == 'xml':                                                       #sinon si l'output est un XML
        namingxml(text,response,file_save)                                      #on lance la fonction namingxml (ligne 53)
        print(f"Processing success: {text} following up")                       #idem, une fois que la fonction précédente est finie, on notifie l'utilisateur
    else :
        print("un problème a eu lieu")                                          #si output n'est ni xml ni geojson, on notifie l'erreur

def namingxml(text,response,file_save):                                         #on nomme les xml
    fin_nom1 = text.find('=')-1
    debut_nom1 = 5
    debut_nom2 = fin_nom1 + 3
    fin_nom2 = text.find(']',debut_nom2) -1                                     # on récupère le nom pour le fichier a partir de la query
    nom1 = text[debut_nom1:fin_nom1]
    nom2 = text[debut_nom2:fin_nom2]
    date_str = datetime.now().strftime("%d%m%Y")                                #on date le fichier avec le jour
    with open(file_save+"\ "+nom1+'_'+nom2+'_'+date_str+'.xml',"w",encoding="utf-8") as f :
        f.write(response)                                                       #on ecrit le fichier téléchargé avec le nom crée
    return


def naminggeojson(text,response,file_save):                                     #pareil que naming xml mais avec les geojson
    fin_nom1 = text.find('=')-1
    debut_nom1 = 5
    debut_nom2 = fin_nom1 + 3
    fin_nom2 = text.find(']',debut_nom2) -1
    nom1 = text[debut_nom1:fin_nom1]
    nom2 = text[debut_nom2:fin_nom2]
    date_str = datetime.now().strftime("%d%m%Y")
    responsetxt = json.dumps(response)
    with open(file_save+"\ "+nom1+'_'+nom2+'_'+date_str+'.geosjon', "w") as f:
        f.write(responsetxt)
    return



if __name__ == "__main__":                                                      #test d'execution du programme en tant que programme principale (et pas appelé par un programme tierce), c'est une sécurité


    file_path = input('Enter the filepath to the file containing the tags (geom["key"="tag"]localisation; (._;>;); format): ') #on demande l'arborescence de fichier où se trouve le fichier txt avec les query
    file_save = input("Enter the file path to save the files :")                #Pareil, arborescence mais de sauvegarde des téléchargement cette fois

    while True :                                                                #boucle du programme demandant les input de format pour lancer le programme
        type_out = input("Quel format d'export ? xml ou geojson : ").strip().lower() #on demande le format, en retirant la casse
        if type_out == 'xml' or type_out == 'geojson':
            break                                                               #si le format est l'un des deux formats accepté, on sors de la boucle while
        else :
            print('format inconnu')                                             #sinon, on annonce un problème de format, et relance la boucle de demande

    run_from_file(file_path,file_save,type_out)                                   #lancement du programme
    print('program end')                                                        #annonce de fin de programme
