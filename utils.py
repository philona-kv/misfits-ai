import PyPDF2
import openai

openai.api_key = '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'


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

def continue_conversation(context, user_input):
    
    messages = [{'role': 'system', 'content': context},
    ]
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    assistant_response = response['choices'][0]['message']['content']
    messages.append({"role":"system", "content":assistant_response})

    return response