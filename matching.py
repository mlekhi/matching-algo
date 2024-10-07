import csv
import json
import os
from dotenv import load_dotenv
from openai import Client 
import random

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client
client = Client()

# 1. Function to read CSV from /csvs directory and convert it to JSON
def read_csv_to_json(csv_filename):
    csv_path = os.path.join('csvs', csv_filename)
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file {csv_filename} not found in /csvs directory.")
    
    people = []
    with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            person_data = {
                "api_id": row.get("api_id"),
                "name": row.get("name"),
                "email": row.get("email"),
                "phone_number": row.get("phone_number"),
                "created_at": row.get("created_at"),
                "approval_status": row.get("approval_status"),
                "what_to_learn": row.get("What is something you’ve always wanted to learn about but haven’t started yet?"),
                "do_with_time_and_money": row.get("If you had all the time and money in the world, what would you do?"),
                "useless_item": row.get("If you could have an unlimited supply of one completely useless item, what would it be?"),
                "proud_of": row.get("What's the last thing you worked on that you're proud of?"),
                "accommodations": row.get("(optional) Do you require any accommodations? (e.g. dietary restrictions, accessibility needs)")
            }
            people.append(person_data)
    
    return people

# 2. Function to filter people by "approved" status
def filter_by_approved(people):
    # Filter people by 'approved' status and return only specific fields
    return [
        {
            "api_id": person.get('api_id'),
            "name": person.get('name'),
            "what_to_learn": person.get('what_to_learn'),
            "do_with_time_and_money": person.get('do_with_time_and_money'),
            "useless_item": person.get('useless_item'),
            "proud_of": person.get('proud_of')
        }
        for person in people if person.get('approval_status', '').lower() == 'approved'
    ]

# 3. Function to create discussion topics using GPT API via the Client
def create_discussion_topics(person):
    interest = person.get('what_to_learn', 'general interests')
    accomplishment = person.get('proud_of', 'something recent they did')

    # Use the Client's chat completion API
    prompt = f"Generate three general discussion topics that would be good to talk to someone interested in {interest} and with recent accomplishment(s): {accomplishment}. Make them each 2-6 words describing topics."

    response = client.chat.completions.create(  # Adjusted method call
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates discussion topics."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.7
    )

    # Access response choices using attributes
    topics = response.choices[0].message.content.strip()

    # Split topics by newlines or punctuation like periods (you can customize this)
    topic_list = topics.split('\n') if '\n' in topics else topics.split('.')

    # Clean up extra spaces and return only non-empty topics
    return [topic.strip() for topic in topic_list if topic.strip()]

# 4. Function to create matching scores between people using OpenAI
def create_matching_scores(people):
    for person in people:
        person['matching_scores'] = {}
        for other_person in people:
            if person['name'] == other_person['name']:
                person['matching_scores'][other_person['name']] = 100  # Matching score with self
            else:
                score = random.randint(0, 100)

                # Assign the score to the matching_scores dictionary
                person['matching_scores'][other_person['name']] = score

# 5. Function to process CSV, filter, generate topics, and matching scores
def process_csv_to_json(csv_filename):
    # Step 1: Read the CSV
    people = read_csv_to_json(csv_filename)
    
    # Step 2: Filter by approved status
    approved_people = filter_by_approved(people)
    print(approved_people)
    
    # Step 3: Generate discussion topics for each person
    for person in approved_people:
        person['discussion_topics'] = create_discussion_topics(person)
    
    # Step 4: Create matching scores between approved people
    create_matching_scores(approved_people)
    
    # Convert to JSON
    return json.dumps(approved_people, indent=2)

# Specify the path to your CSV file in the /csvs directory
csv_file = 'people_data.csv'  # Replace this with your actual CSV file name in the /csvs directory

# Process CSV and generate JSON output
json_output = process_csv_to_json(csv_file)

# Save the JSON output to a file
with open('people_data.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_output)

print("JSON output saved to 'people_data.json'")
