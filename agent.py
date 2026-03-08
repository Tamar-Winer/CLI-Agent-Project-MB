import os
import requests
import gradio as gr
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def load_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# קריאת הפרומפט מהקובץ
FINAL_SYSTEM_PROMPT = load_prompt('system_prompt.md')

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

css = """
.gradio-container {
    background-color: #020408 !important;
    background-image: radial-gradient(circle at center, #0a192f 0%, #020408 100%) !important;
    height: 100vh !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
.form, .gradio-container .gr-form { background: transparent !important; border: none !important; }
#main-container {
    background: rgba(13, 17, 23, 0.85) !important;
    border: 1px solid rgba(56, 139, 253, 0.3) !important;
    border-radius: 30px !important;
    padding: 50px !important;
    width: 100% !important;
    max-width: 500px !important;
    box-shadow: 0 0 50px rgba(0, 0, 0, 0.9) !important;
    backdrop-filter: blur(20px);
    margin: auto !important;
}
textarea, input {
    background-color: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    color: #58a6ff !important;
    text-align: center !important;
    font-family: 'Consolas', monospace !important;
}
button.primary {
    background: linear-gradient(135deg, #1f6feb 0%, #0d419d 100%) !important;
    border: none !important;
    border-radius: 15px !important;
    padding: 16px !important;
    font-weight: 900 !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}
h1 { color: #ffffff !important; text-shadow: 0 0 15px rgba(255, 255, 255, 0.3); }
.credit-text { color: #4b5563 !important; font-size: 0.8em; margin-top: 35px; letter-spacing: 3px; font-weight: bold; }
"""

with gr.Blocks(css=css, title="CLI Command Station") as demo:
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