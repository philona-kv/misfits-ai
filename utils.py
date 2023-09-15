import PyPDF2
import openai
import json
import requests

openai.api_key = 'Your API key here'

token = 'Your github PAI here'

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

def continue_conversation(context, user_input, assistant=None):
    
    messages = [{'role': 'system', 'content': context},
    ]
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    assistant_response = response['choices'][0]['message']['content']
    messages.append({"role":"system", "content":assistant_response})
    start_index = assistant_response.find('{')
    end_index = assistant_response.rfind('}')
    json_str = assistant_response[start_index:end_index+1]
    resume_summary = json.loads(json_str)
    return resume_summary

def get_commit_count(user):
    headers = {
        'Authorization': f'token {token}'
    }
    r = requests.get(f'https://api.github.com/users/{user}/repos', headers=headers)
    repos = json.loads(r.text)
    total_commits = 0  # Initialize total commit count
    
    for repo in repos:
        if repo['fork'] is True:
            # Skip forks
            continue
        commit_count = count_user_repo_commits(repo['commits_url'].replace('{/sha}', ''), user, headers)
        total_commits += commit_count
    
    return total_commits

def count_user_repo_commits(commits_url, user, headers, _acc=0):
    r = requests.get(commits_url, headers=headers)
    commits = json.loads(r.text)
    n = len([commit for commit in commits if commit['author']['login'] == user])
    
    if n == 0:
        return _acc
    
    link = r.headers.get('link')
    
    if link is None:
        return _acc + n
    
    next_url = find_next(link)
    
    if next_url is None:
        return _acc + n
    
    return count_user_repo_commits(next_url, user, headers, _acc + n)

def find_next(link):
    for l in link.split(','):
        a, b = l.split(';')
        
        if b.strip() == 'rel="next"':
            return a.strip()[1:-1]

def get_repo_count(username):
    api_url = f'https://api.github.com/users/{username}/repos'

    try:
        response = requests.get(api_url)

        if response.status_code == 200:
            repos = response.json()
            repo_count = len([repo for repo in repos if repo['fork']])
            return repo_count
        else:
            print(f"Failed to retrieve data from GitHub API. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
