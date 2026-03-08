import os
import requests
import gradio as gr
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def load_resource(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return ""

FINAL_SYSTEM_PROMPT = load_resource('system_prompt.md')
custom_css = load_resource('style.css')

def translate_to_cli(user_input):
    try:
        clean_key = api_key.strip()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={clean_key}"

        full_prompt = f"{FINAL_SYSTEM_PROMPT}\n\nInstruction: {user_input}"
        payload = {"contents": [{"parts": [{"text": full_prompt}]}], "generationConfig": {"temperature": 0}}

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 404:
            url_alt = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={clean_key}"
            response = requests.post(url_alt, json=payload, timeout=10)

        # טיפול בחריגת מכסה
        if response.status_code == 429:
            return "⚠️ ERROR 429: Too many requests. Please wait 60 seconds."

        response.raise_for_status()
        res_json = response.json()

        if "candidates" in res_json:
            answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return answer.strip().replace('`', '')

        return "🚫 ERROR: Unexpected response format."
    except Exception as e:
        return f"🚫 SYSTEM ERROR: {str(e)}"


with gr.Blocks(css=custom_css, title="CLI Command Station") as demo:
    with gr.Column(elem_id="main-container"):
        gr.HTML(
            '<div style="text-align: center; margin-bottom: 20px;"><div style="font-size: 4em; margin-bottom: 10px;">🚀</div><h1 style="margin: 0;">COMMAND STATION</h1><p style="color: #58a6ff; font-size: 0.9em; opacity: 0.7;">Secure Windows CLI Interface</p></div>')
        user_input = gr.Textbox(label=None, placeholder="Type your instruction...", lines=1, container=False)
        gr.Markdown("<div style='height: 5px;'></div>")
        btn = gr.Button("EXECUTE 📡", variant="primary")
        gr.Markdown("<div style='height: 5px;'></div>")
        output_text = gr.Textbox(label=None, placeholder="Awaiting signal...", interactive=False, container=False)
        gr.HTML('<div class="credit-text" style="text-align: center;">DEVELOPED BY TAMAR WINER</div>')

    btn.click(fn=translate_to_cli, inputs=user_input, outputs=output_text)

if __name__ == "__main__":
    demo.launch()