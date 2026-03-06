import os
import requests
import gradio as gr
from dotenv import load_dotenv

# טעינת מפתח
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# הפרומפט המקורי כברירת מחדל
DEFAULT_SYSTEM_PROMPT = """You are a Windows CLI expert. 
Convert the user instruction to a Windows terminal command. 
Return ONLY the command text. No explanations, no markdown, no backticks."""


def translate_to_cli(user_input, system_prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

        # בניית הבקשה עם הפרומפט שמופיע בתיבה
        full_prompt = f"{system_prompt}\n\nInstruction: {user_input}"

        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0}
        }

        response = requests.post(url, json=payload)
        res_json = response.json()

        if "candidates" in res_json:
            answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return answer.strip().replace('`', '')
        return f"שגיאה: {res_json.get('error', {}).get('message', 'תגובה לא מזוהה')}"

    except Exception as e:
        return f"שגיאה טכנית: {str(e)}"


# עיצוב הממשק (Gradio UI)
with gr.Blocks(theme=gr.themes.Soft(), title="CLI Agent Pro") as demo:
    gr.Markdown("""
    # 🖥️ CLI Agent - Gemini 2.5 Edition
    ### המרת שפה טבעית לפקודות טרמינל (Windows)
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ הגדרות המודל (Prompt)")
            sys_input = gr.Textbox(
                value=DEFAULT_SYSTEM_PROMPT,
                label="System Prompt",
                lines=5,
                interactive=True
            )

        with gr.Column(scale=2):
            gr.Markdown("### 💬 שיחה עם ה-Agent")
            user_input = gr.Textbox(
                label="הוראה למחשב",
                placeholder="למשל: תראה לי את כל הקבצים בתיקייה ששוקלים מעל 1GB"
            )
            output_text = gr.Textbox(label="פקודת CLI סופית", interactive=False)
            btn = gr.Button("🚀 צור פקודה", variant="primary")

    # הפעלת הפונקציה
    btn.click(
        fn=translate_to_cli,
        inputs=[user_input, sys_input],
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch()