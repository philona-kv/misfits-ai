from flask import Flask, request, jsonify, render_template
import PyPDF2
import string
import os
import openai

app = Flask(__name__)


openai.api_key = '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'

messages = [{'role': 'system', 'content': "You are a professional resume and job description summariser. I am a client who will give extracted resume text and job description you need find the matching between the resume text and the job description and you need to rank the resume. And from the resume structure the releveant data like the skills, education and projects in a json format"},
  ]


def continue_conversation(messages, user_input):
    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    assistant_response = response['choices'][0]['message']['content']
    messages.append({"role":"system", "content":assistant_response})
    print(assistant_response)
    return response


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

@app.route('/', methods=['GET'])
def hello():
    return "Hello"
    
@app.route('/summarize', methods=['GET', 'POST'])
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
        resp = continue_conversation(messages, user_input)
        os.remove(file_path)
        return resp


if __name__ == '__main__':
    app.run(debug=True, port=5007)
