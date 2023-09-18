from flask import Flask, request, render_template
import os
from utils import continue_conversation, extract_text_from_pdf, get_repo_count, get_commit_count, get_wav_from_mp4,\
    get_transcript_from_wav, get_stackoverflow_info, ai_summarizer
import json

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return "Hello"


def exponential_cdf(x):
    exp_cdf = 1-2 ** -x
    return exp_cdf


@app.route('/resume-summary', methods=['GET', 'POST'])
def summarize_resume():
    if request.method == 'GET':
        return render_template("upload.html")
    
    if request.method == 'POST':
        file = request.files['resume']
        job_dec = request.form['job_description']
        file_path = os.path.join(app.root_path, file.filename)
        file.save(file_path)
        resume_text = extract_text_from_pdf(file_path)
        user_input = 'This is the extracted resume text ' + resume_text + 'and this is the job description ' + job_dec
        context = 'You are a professional resume and job description summariser. I am a client who will give ' \
                  'extracted resume text and job description you need find the matching between the resume text and ' \
                  'the job description and you need to rate the resume out of 10. From the resume get the name, ' \
                  'phone, email, skills, rating and the summary about the match between the resume and job ' \
                  'description in a json object. The object keys strictly should be name, phone, email, skills, ' \
                  'summary respectively. The skills should be an array of strings'
        resp = continue_conversation(context, user_input)
        os.remove(file_path)
        return resp


@app.route('/interview-summary', methods=['GET'])
def interview_summarizer():

    context = "You are a professional interview summariser. I am an client who will provide you the interview " \
              "conversation \n You must give me the summary of the entire interview highlighting the questions asked " \
              "and the candidates responses. The summary must be in bullets"
    
    user_input = "Summarise the following interview: Morning ma'am. Good morning. Can I hire resume? Yes ma'am. Okay, "\
                 "your good name? Madhuri. Okay Madhuri, please introduce yourself. I am Madhuri from JPK but " \
                 "currently staying in Hyderabad to build an independent career and I completed my graduation in " \
                 "Srijatana Institute of Technological Sciences from Electronics and Communication Engineering. " \
                 "During my graduation I had a project on brain tumor detection. Apart from a qualification I am good "\
                 "at Java and C. I can speak English and Peru. Regarding my strengths, I am a self motivated person " \
                 "and I can easily adopt myself to any environment. Coming to my weakness, I always need perfection " \
                 "in my work. So I will take little bit more time to complete my work. Later I realized it so now I'm "\
                 "trying to overcome it. Okay, good to know you mahdri. Okay, what are your technical skills? Okay " \
                 "why should I hire you as a fresher? I have theoretical knowledge so I'm looking for a platform to " \
                 "implement my skills and knowledge. If you give me a chance, I will put my effect 100% effort for " \
                 "the growth of the company. What are your Hobies? In my free time I regularly use today exercise and "\
                 "I'm interested in reading books. Okay, that's good. So why do you think you are good fit for this " \
                 "job? Based on this requirement, my skills are matching with this profile and also I'm an " \
                 "adaptability person so I can easily adapt to any environment and I will give my 100% to the growth " \
                 "of this company. Okay, so what do you know about this company? As per my knowledge, it is a fastest "\
                 "growing company and it provides lot of opportunities. And I hear from the employees that the work " \
                 "environment is good and supporting employees also. So if I hire you after five years where you are " \
                 "going to see yourself? I would like to see myself in a respectable position of that organization in "\
                 "leading position. With my leadership skills I am valuable person with more responsibilities. Okay, " \
                 "so how would you be a good asset for our organization? I will work hard and I will give my best to " \
                 "the company. And with my never give up attitude I will try to achieve a best position in that " \
                 "organization and I will also increase the growth of this organization. Okay, that's good. So what " \
                 "are your salary expectations as a fresher? My first priority is to enhance my skills and knowledge. "\
                 "So I always accept what you offer as per the company now which will fulfill my economical needs. So "\
                 "how long can you give services to work? I would like to work as long as the company needs me and " \
                 "based on carrying growth I will continue when the company will be satisfied with my work and also I "\
                 "would like to have better position. So how do you like to rate yourself from one to ten? I would " \
                 "like to rate myself as a because no one is perfect and there is always a scope for learning and " \
                 "improvement and I feel that continuous learning is fundamental part of professional and personal. " \
                 "Okay so kind thanks for coming we will respond you. We will get back to soon okay? Thank you. Thank "\
                 "you."
    
    new_response = ai_summarizer(context, user_input)

    return new_response.choices[0].message.content


@app.route('/github-details', methods=['GET'])
def github_parser():

    github_profile_url = request.args.get('url')
    username = github_profile_url.split('/')[-1]
    repo_count = get_repo_count(username)
    commit_count = get_commit_count(username)
    commit_weight = 4
    repos_weight = 3
    total_weight = commit_weight + repos_weight
    thresholds = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
    levels = [9, 8, 7, 6, 5, 4, 3, 2, 1]

    agg_val = 1 - (commit_weight * exponential_cdf(commit_count / 250) + repos_weight *
                   exponential_cdf(repo_count / 50))/total_weight
    index = next((i for i, t in enumerate(thresholds) if float(agg_val) * 100 <= t), None)

    rate = levels[index] if index is not None else None

    return {
        'repo_count': repo_count,
        'rate': rate,
        'commit_count': commit_count
    }


@app.route('/video-summary', methods=['GET'])
def video_summary():

    audio_filename = get_wav_from_mp4('interviews/madhuri.mp4')
    transcript = 'Summarise the following interview: ' + get_transcript_from_wav(audio_filename)
    context = "You are a professional interview summariser. I am an client who will provide you the interview " \
              "conversation \n You must give me the summary of the entire interview highlighting the questions asked " \
              "and the candidates responses. The summary must be in bullets"
    summary = ai_summarizer(context, transcript)

    return summary.choices[0].message.content


@app.route('/interview-feedback', methods=['GET'])
def interview_feedback():

    context = "You are a professional interview feedback provider. I am an client who will provide you the interview " \
              "conversation \n You must give me the feedback of the entire interview highlighting the candidates " \
              "technical skills, aptitude, soft skills and also a rating for all of them. The response must be in a " \
              "json object. The object keys strictly should be technical_skills_rating, aptitude_rating, " \
              "soft_skills_rating, technical_skills_feedback, aptitude_feedback and soft_skills_feedback respectively"
    user_input = "Interview: Yes, sir. Yes sir, I'm here or fabulous. Let's start. Rahul, introduce yourself please. " \
                 "Hello sir, my complete name complaint name is Rahul RajMar. And currently I'm from Mumbai. And sir, "\
                 "currently I am pursuing bachelor of Engineering in Information Technology from Jet of Engineering " \
                 "which is one of reading colleges in Mumbai. Currently I have a 7.6 aggregate six semester. And sir, "\
                 "currently I'm also working as an intern in Food Speedy company as a technical writer. And sir, " \
                 "talking about my project I done one of my project that is Dam automation IoT and working on my " \
                 "final year project which is a very exciting and problem solving project for my college that is a " \
                 "document plagiarism detector. And sir, apart from study I am very much involved in extra and co " \
                 "curricular activities. Sir, because I am elected as an event head and marketing executive for TEDx " \
                 "Xi and I am also selected as an event head event at four event in my college. Test answer apart " \
                 "from study, I love to do cooking and learning about mind. And sir, talking about my family. Sir, " \
                 "I am coming from a joint family. I am eldest son of my family. So I have a responsibility of my " \
                 "family. And sir, my goal is to join one of the leading company like yours. And I want to achieve " \
                 "organizational as well as personal goal by exploring myself more in industry. And sir, because I'm " \
                 "a part of a buckling NGO so I have one more goal in my life. I want to sponsor education for " \
                 "children. That's all about it. Rahul, you are mentioning about the finally a project you said it's " \
                 "exciting and all that can you elaborate a little bit more on that? Yes sir the project name is a " \
                 "document logarithm detector like you said it is basically as we know that in the colleges in school "\
                 "colleges and school the maximum students submitted assignments as well as practical sheets by " \
                 "copying some other students. So I am developing the system which helps teacher or examiner to check "\
                 "what is the similarity between the documents or like assignments or practical seats as submitted by "\
                 "students I am using some machine learning algorithm which helps to basically generate a score which "\
                 "gives a similarity score between the documents. For example how the first student document is " \
                 "similar to third student 56 students, 70 students basically it gives the similarity score so using " \
                 "that the teacher can calculate the particular document is copied from other student or it is right " \
                 "from your own. Rahul, considering the fact that in Indian schools most of the homework is submitted "\
                 "in written format not in digital format how will this thing work? Yes sir, basically I have using " \
                 "algorithms this algorithm actually detect first of all we have take the picture of the particular " \
                 "series and then the algorithms take all the words that scan and take all the words in array format " \
                 "and save all these words in another document and using those documents, we check the similarities " \
                 "both. And you are using machine learning in this? Yes, sir can you elaborate a little bit on what " \
                 "sort of algorithm you're using? Sir I am using three algorithms. Basically, first is a KMP Morris " \
                 "Pratt algorithm and second is a Voice Mood algorithm and third is a voice Embed and Ravindar " \
                 "algorithm. This is algorithm I am using. Rahul with so much interest in machine learning and all " \
                 "that, why do you want to join TCS? Considering the fact that we actually don't have openings in the "\
                 "field of machine learning, basically I'm interested in it. It will not mean I'm only interested in " \
                 "machine learning projects because I have done in my projects in various other technologies. First " \
                 "of all, I have done this in machine learning. And the second project I done in using IoT and the " \
                 "third project I was done using HTML and CSS. So this is not mean that I'm only interested in " \
                 "machine learning. But if I can get chance in working in development area of machine learning that " \
                 "it is good for me. What is the reason why your percentage in graduation is less? Actually, sir, " \
                 "in first two year my average pointer only 6.66 and in fifth semester and 6th semester the pointer " \
                 "is 9.19, and six semester my pointer is 9.92. Using that pointer stop. You are beautiful. You sold " \
                 "like shit. Now this is something I would love you guys to learn. He forced me to ask questions on " \
                 "his final year project. He talked about it's very exciting. But the beauty is when he was " \
                 "introducing himself, he didn't go to the depth. He actually tempted me. And after that he said many "\
                 "things. When Mayur was saying yes, shit. Project Ki. Project Ki. Project Ki. That is the temptation "\
                 "I want. When I put him in the corner, for example, when I talked about the fact that I don't have " \
                 "an opening in machine learning, why should you come? Rahul your mind works beautifully, sweetheart. "\
                 "He immediately said, look, that is not the only thing I'm excited about. I'm excited about " \
                 "technology as a whole. I've actually worked in various other technologies and quickly he mentioned " \
                 "one or two work he has done. By that way, he was able to talk about the breadth of exposure that he "\
                 "has. Similarly, when I asked percentage, one of the very common things people normally immediately " \
                 "come out with is impulsively. Talk about the fact that sir handwriting Achani sir other area. But " \
                 "this gentleman told me don't measure me by what I was in the first year and second year. Look at " \
                 "from the fifth semester. Fifth semester I'm a nine quarter. 6th semester I've done so and so and " \
                 "you are not buying me the way I was then and you are buying me the way I am now. Rahul it was " \
                 "amazing. Now, the only area where I would love to see you improve is your body language. A little " \
                 "bit because you are avoiding eye contact when you're thinking you look here, you actually dance a " \
                 "little bit and I believe there's a bit of disturbance that coming from your way. Do remember when a "\
                 "company comes, they would love to hear you because your answers were beautiful. But in case it so " \
                 "happened that they get distracted either because the technology fails or the fact that the noise is "\
                 "there, then it might impact the effectiveness of what you were. All right? And the good thing is " \
                 "when you are talking about your projects, I asked about algorithm you are able to recall. But I " \
                 "would like to see a little bit of speed in recall because at the end of the day, you don't get so " \
                 "much time in the interview process. But I'm going to give you huge marks for your performance. If I "\
                 "had been TCS, I would have labbed you up for a simple reason because you were very effective in " \
                 "communicating as to what amount of work you have done. And yes, that work is an exciting amount of " \
                 "work, all right. Especially the project that you're talking about. You really were able to " \
                 "successfully excite me in that area. I actually tried to put a googly saying that look what happens "\
                 "if it's a written thing. You said it will be scanned and converted. The fact of the matter is today "\
                 "technology is there. Okay? So I am going to give you a mark for that. The only thing rahul you need "\
                 "to be careful is there are already a lot of software available online for Plagiarism check. So do " \
                 "get to know a few of those softwares which are already there in the market. No one is expecting you "\
                 "to be original. Everyone knows you are after all, a student. So at know as long as you know of the " \
                 "projects of similar offerings which are there in the market, maybe you can even throw one or two " \
                 "things on how your offering is a bit little better than them, then you'll frankly make me fall in " \
                 "love with you. So I am going to give you huge marks for it is a well showed done. But see tweet " \
                 "that once in a while. You're smiling, sweetheart, because you don't want to position yourself as a " \
                 "person who is a very serious person as well. But fantastic. It was real pleasure interviewing you " \
                 "here. All right, let me take a question that Raghav said."
    feedback_data = ai_summarizer(context, user_input)
    feedback_data = feedback_data['choices'][0]['message']['content']
    start_index = feedback_data.find('{')
    end_index = feedback_data.rfind('}')
    json_str = feedback_data[start_index:end_index+1]
    feedback_data = json.loads(json_str)
    return feedback_data


@app.route('/stackoverflow-details', methods=['GET'])
def stackoverflow_parser():
    stackoverflow_profile_url = request.args.get('url')
    print('profile url is ', stackoverflow_profile_url)
    user_id = stackoverflow_profile_url.split('/')[4]
    stack_data = get_stackoverflow_info(user_id)
    return str(stack_data)


@app.route('/get-profiles', methods=['GET'])
def get_profiles():
    data = request.get_json()
    github_profile_url = data["github"]
    username = github_profile_url.split('/')[-1]
    repo_count = get_repo_count(username)
    commit_count = get_commit_count(username)
    commit_weight = 4
    repos_weight = 3
    total_weight = commit_weight + repos_weight
    thresholds = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
    levels = [9, 8, 7, 6, 5, 4, 3, 2, 1]

    agg_val = 1 - (commit_weight * exponential_cdf(commit_count / 250) + repos_weight *
                   exponential_cdf(repo_count / 50))/total_weight
    index = next((i for i, t in enumerate(thresholds) if float(agg_val) * 100 <= t), None)

    rate = levels[index] if index is not None else None

    stackoverflow_profile_url = data["stackoverflow"]
    user_id = stackoverflow_profile_url.split('/')[4]
    stack_data = get_stackoverflow_info(user_id)

    return {
        "githubRating": rate,
        "stackOverflowRating": stack_data,
    }


if __name__ == '__main__':
    app.run(debug=True, port=5007)
