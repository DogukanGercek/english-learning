from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    content = data.get('content', '')
    action = data.get('action', '')
    level = data.get('level', 'intermediate')

    if not content:
        return jsonify({"error": "No content provided"}), 400

    result = None

    try:
        if action == 'flashcards':
            result = generate_flashcards(content, level)
        elif action == 'questions':
            result = generate_questions(content, level)
        elif action == 'summary':
            result = generate_summary(content, level)
        else:
            return jsonify({"error": "Invalid action type"}), 400

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_flashcards(content, level):
    prompt = f"""
    Create 5 English learning flashcards based on the following content for a {level} level student:

    {content}

    Format each flashcard as a JSON object with 'front' and 'back' fields. 
    The front should be a word, phrase, or question, and the back should be the definition, 
    explanation, or answer.
    Return only the JSON array of flashcards without any additional text or markdown formatting.
    """

    response = model.generate_content(prompt)
    return response.text


def generate_questions(content, level):
    prompt = f"""
    Create 5 practice questions based on the following English content for a {level} level student:

    {content}

    For each question, include:
    1. The question
    2. Multiple choice answers (if appropriate)
    3. The correct answer

    Format as a JSON array where each object has 'question', 'options' (array), and 'answer' fields.
    Return only the JSON array without any additional text or markdown formatting.
    """

    response = model.generate_content(prompt)
    return response.text


def generate_summary(content, level):
    prompt = f"""
    Create a concise summary of the following English content for a {level} level student:

    {content}

    Also highlight 3-5 key vocabulary words or phrases with their definitions.
    Format as a JSON object with 'summary' and 'vocabulary' fields, where vocabulary is an array of objects
    with 'word' and 'definition' fields.
    Return only the JSON object without any additional text or markdown formatting.
    """

    response = model.generate_content(prompt)
    return response.text


if __name__ == '__main__':
    app.run(debug=True)