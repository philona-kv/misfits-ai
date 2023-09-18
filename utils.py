import os
import PyPDF2
import openai
import json
import requests
import assemblyai as aai
import moviepy.editor as mp

openai.api_key = 'Your API key here'
token = 'Your github PAI here'

badge_weights = {
    "bronze": 60,
    "silver": 80,
    "gold": 100,
}

aai.settings.api_key = 'Your Assembly API key here'


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text


def continue_conversation(context, user_input):
    messages = [{'role': 'system', 'content': context}, {"role": "user", "content": user_input}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    assistant_response = response['choices'][0]['message']['content']
    messages.append({"role": "system", "content": assistant_response})
    start_index = assistant_response.find('{')
    end_index = assistant_response.rfind('}')
    json_str = assistant_response[start_index:end_index + 1]
    resume_summary = json.loads(json_str)
    return resume_summary


def ai_summarizer(context, user_input):
    messages = [{'role': 'system', 'content': context}, {"role": "user", "content": user_input}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    assistant_response = response['choices'][0]['message']['content']
    messages.append({"role": "system", "content": assistant_response})

    return response


def get_commit_count(user):
    headers = {
        'Authorization': f'token {token}'
    }
    r = requests.get(f'https://api.github.com/users/{user}/repos', headers=headers)
    repos = json.loads(r.text)
    total_commits = 0

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


def find_next(links):
    for link in links.split(','):
        a, b = link.split(';')

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


def get_wav_from_mp4(relative_path):
    directory, filename = os.path.split(relative_path)
    name, extension = os.path.splitext(filename)

    # Load the video
    video = mp.VideoFileClip(relative_path)

    # Extract the audio from the video
    audio_file = video.audio
    audio_filename = name + '.wav'
    audio_file.write_audiofile(audio_filename)

    return audio_filename


def get_transcript_from_wav(relative_path):
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(relative_path)
    text = transcript.text
    return text


def get_stackoverflow_info(user_id):
    api_url = f'https://api.stackexchange.com/2.2/users/{user_id}?site=stackoverflow.com'
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            details = response.json()
            details_string = json.dumps(details)
            badge_details = json.loads(details_string)
            badge_counts_object = badge_details["items"][0]["badge_counts"]
            total_weight = 0
            for badge in badge_counts_object:
                total_weight = total_weight + badge_counts_object[badge] * badge_weights[badge]
            print(total_weight)
            final_score = total_weight / 21000
            final_rating = final_score * float(10)
            return final_rating
        else:
            print('Failed to retrieve data.')
            return None
    except Exception as e:
        print(f"some error occured: {str(e)}")
        return None
