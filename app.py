from flask import Flask, request, render_template
import os
from utils import continue_conversation, extract_text_from_pdf, get_repo_count, get_commit_count

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return "Hello"

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
        context = 'You are a professional resume and job description summariser. I am a client who will give extracted resume text and job description you need find the matching between the resume text and the job description and you need to rate the resume. And from the resume structure the relevant data like the skills, education, projects and the rating in a json format. Name the keys like Name, Phone, Email, Skills, Education, Work Experience and give the rating in the key Rating.'
        resp = continue_conversation(context, user_input)
        os.remove(file_path)
        return resp

@app.route('/interview-summary', methods=['GET'])
def interview_summarizer():

    context = "You are a professional interview summariser. I am an client who will provide you the interview conversation \n You must give me the summary of the entire interview highlighting the questions asked and the candidates responses. The summary must be in bullets"
    
    user_input = "Summarise the following interview: Morning ma'am. Good morning. Can I hire resume? Yes ma'am. Okay, your good name? Madhuri. Okay Madhuri, please introduce yourself. I am Madhuri from JPK but currently staying in Hyderabad to build an independent career and I completed my graduation in Srijatana Institute of Technological Sciences from Electronics and Communication Engineering. During my graduation I had a project on brain tumor detection. Apart from a qualification I am good at Java and C. I can speak English and Peru. Regarding my strengths, I am a self motivated person and I can easily adopt myself to any environment. Coming to my weakness, I always need perfection in my work. So I will take little bit more time to complete my work. Later I realized it so now I'm trying to overcome it. Okay, good to know you mahdri. Okay, what are your technical skills? Okay why should I hire you as a fresher? I have theoretical knowledge so I'm looking for a platform to implement my skills and knowledge. If you give me a chance, I will put my effect 100% effort for the growth of the company. What are your Hobies? In my free time I regularly use today exercise and I'm interested in reading books. Okay, that's good. So why do you think you are good fit for this job? Based on this requirement, my skills are matching with this profile and also I'm an adaptability person so I can easily adapt to any environment and I will give my 100% to the growth of this company. Okay, so what do you know about this company? As per my knowledge, it is a fastest growing company and it provides lot of opportunities. And I hear from the employees that the work environment is good and supporting employees also. So if I hire you after five years where you are going to see yourself? I would like to see myself in a respectable position of that organization in leading position. With my leadership skills I am valuable person with more responsibilities. Okay, so how would you be a good asset for our organization? I will work hard and I will give my best to the company. And with my never give up attitude I will try to achieve a best position in that organization and I will also increase the growth of this organization. Okay, that's good. So what are your salary expectations as a fresher? My first priority is to enhance my skills and knowledge. So I always accept what you offer as per the company now which will fulfill my economical needs. So how long can you give services to work? I would like to work as long as the company needs me and based on carrying growth I will continue when the company will be satisfied with my work and also I would like to have better position. So how do you like to rate yourself from one to ten? I would like to rate myself as a because no one is perfect and there is always a scope for learning and improvement and I feel that continuous learning is fundamental part of professional and personal. Okay so kind thanks for coming we will respond you. We will get back to soon okay? Thank you. Thank you."
    
    new_response = continue_conversation(context, user_input)

    return new_response

@app.route('/github-details', methods=['GET'])
def github_parser():
    github_profile_url = request.args.get('url')
    print(github_profile_url)
    username = github_profile_url.split('/')[-1]
    repo_count = get_repo_count(username)
    commit_count = get_commit_count(username)

    return {
            'repo_count': repo_count,
            'commit_count': commit_count
        }

if __name__ == '__main__':
    app.run(debug=True, port=5007)
  