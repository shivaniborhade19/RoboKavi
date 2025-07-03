# poem_generator.py

import google.generativeai as genai
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
translator = GoogleTranslator()


def to_marathi(text):
    return GoogleTranslator(source='auto', target='mr').translate(text)


def generate_poem(name, subject, language="mr"):
    if language == "mr":
        name_mr = to_marathi(name)
        subject_mr = to_marathi(subject)
        prompt = f"""{name_mr} आणि {subject_mr} या विषयावर आधारित एक छोटी, ३-४
        ओळींची, यमकबद्ध मराठी कविता लिहा.
फक्त कविता लिहा, दुसरे काहीही नाही."""
    else:
        prompt = f"""Write a short English poem (3–4 lines) with rhyme based
        on the name '{name}' and the theme '{subject}'. Only the poem, no
        explanations."""

    response = model.generate_content(prompt)
    poem = (response.text.strip() if hasattr(response, 'text')
            and response.text else None)
    return poem
