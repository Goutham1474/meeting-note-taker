import json

def convert_to_json(input_string):
    # Clean up any unwanted spaces or characters
    input_string = input_string.strip()

    # Parse the string as JSON
    try:
        json_data = json.loads(input_string)
        return json_data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

# Example of valid input string (ensure it's formatted like this)
input_string = '''{
    "Overall_Observation": "The candidate did not perform well during the interview and expressed their lack of confidence in being a suitable candidate for the role.",
    "Strengths": ["No particular strengths found"],
    "Weaknesses": ["Lack of confidence", "Self-perceived inadequacy"],
    "Fit for the role": "Not suitable for the role",
    "intents": {
        "Overall performance assessment": "The candidate's lack of confidence and self-perceived inadequacy were evident throughout the interview, leading to the decision that they are not a good fit for the role."
    }
}'''

json_data = convert_to_json(input_string)
with open('response.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(json_data, indent=4))

print(json_data)
