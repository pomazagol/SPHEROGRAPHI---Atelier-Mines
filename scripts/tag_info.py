import requests
from datetime import datetime

def fetch_taginfo(key, value):
    # Define the API endpoint and parameters
    api_url = "https://taginfo.openstreetmap.org/api/4/tag/stats"
    params = {
        "key": key,
        "value": value
    }

    # Make the request to the API
    response = requests.get(api_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Extract relevant information
        total_count = data['data'][0]['count']
        nodes_count = data['data'][1]['count']
        ways_count = data['data'][2]['count']
        relations_count = data['data'][3]['count']

        # Prepare the markdown content
        markdown_content = (
            f"| Type | Count |\n"
            f"|------|-------|\n"
            f"| Total | {total_count} |\n"
            f"| Nodes | {nodes_count} |\n"
            f"| Ways | {ways_count} |\n"
            f"| Relations | {relations_count} |\n"
        )

        # Define the filename with the current date
        date_str = datetime.now().strftime("%d%m%Y")
        filename = f"{key}_eq_{value}_{date_str}.md"

        # Write the markdown content to a file
        with open(filename, 'w') as file:
            file.write(markdown_content)

        print(f"Data successfully written to {filename}")
    else:
        print("Failed to retrieve data. Please try again later.")

# Ask the user for input
key = input("Please enter the key: ")
value = input("Please enter the value: ")

# Fetch the tag info based on user input
fetch_taginfo(key, value)
