import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
from multiprocessing import Pool, cpu_count
from collections import defaultdict

def parse_osm_file(file_path):
    users = defaultdict(lambda: {
        "uid": None, "contribution": 0, "first_contribution": None, "last_contribution": None,
        "node": set(), "node_point": set(), "node_in_way": set(), "way": set(), "relation": set(), "changeset": set()
    })
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    ways_nodes = set()
    
    for way in root.findall('way'):
        for nd in way.findall('nd'):
            ways_nodes.add(nd.get('ref'))
    
    for element in root:
        if element.tag in ['node', 'way', 'relation']:
            user = element.get('user')
            uid = element.get('uid')
            changeset = element.get('changeset')
            timestamp = element.get('timestamp')
            
            if user and uid:
                users[user]["uid"] = uid
                users[user]["contribution"] += 1
                users[user]["changeset"].add(changeset)
                
                if users[user]["first_contribution"] is None or timestamp < users[user]["first_contribution"]:
                    users[user]["first_contribution"] = timestamp
                if users[user]["last_contribution"] is None or timestamp > users[user]["last_contribution"]:
                    users[user]["last_contribution"] = timestamp
                
                if element.tag == 'node':
                    node_id = element.get('id')
                    users[user]["node"].add(node_id)
                    if node_id in ways_nodes:
                        users[user]["node_in_way"].add(node_id)
                    else:
                        users[user]["node_point"].add(node_id)
                elif element.tag == 'way':
                    users[user]["way"].add(element.get('id'))
                elif element.tag == 'relation':
                    users[user]["relation"].add(element.get('id'))
    
    data = []
    for user, info in users.items():
        data.append([
            user, info["uid"], info["contribution"], info["first_contribution"], info["last_contribution"],
            len(info["node"]), len(info["node_point"]), len(info["node_in_way"]),
            len(info["way"]), len(info["relation"]), len(info["changeset"])
        ])
    
    df = pd.DataFrame(data, columns=[
        "user", "uid", "contribution", "first_contribution", "last_contribution",
        "node", "node_point", "node_in_way", "way", "relation", "changeset"
    ])
    
    total_row = [
        "TOTAL", "", df["contribution"].sum(), "", "",
        df["node"].sum(), df["node_point"].sum(), df["node_in_way"].sum(),
        df["way"].sum(), df["relation"].sum(), df["changeset"].sum()
    ]
    df.loc[len(df)] = total_row
    
    output_file = os.path.splitext(file_path)[0] + ".csv"
    df.to_csv(output_file, index=False)
    print(f"Processed: {file_path} -> {output_file}")

def main():
    xml_files = glob.glob("*.xml")
    
    if not xml_files:
        print("No XML files found in the current directory.")
        return
    
    with Pool(cpu_count()) as pool:
        pool.map(parse_osm_file, xml_files)
    
    print("Processing complete!")

if __name__ == "__main__":
    main()