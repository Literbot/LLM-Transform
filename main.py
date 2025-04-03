import openai
import requests
from flask import Flask, request, render_template, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)

# OpenAI API Key（如果沒有，請留空）
OPENAI_API_KEY = ""  # 如果有 OpenAI API 金鑰，填入這裡
HUGGINGFACE_API_KEY = "你的 Hugging Face API Key"

# Hugging Face 模型
HF_MODEL_NAME = "google/gemma-3-4b-it"  # Gemma 模型名稱
hf_tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
hf_model = AutoModelForCausalLM.from_pretrained(HF_MODEL_NAME)

@app.route('/', methods=['GET', 'POST'])
def convert_code():
    if request.method == 'GET':
        return render_template('index.html', title='Code Converter')

    if request.method == 'POST':
        data = request.json
        source_code = data['code']
        source_lang = data['source_lang']
        target_lang = data['target_lang']
        model_choice = data['model']  # 使用者選擇的模型 (openai / huggingface)

        prompt = f"### 轉換程式碼\n將以下 {source_lang} 程式碼轉換為 {target_lang}:\n{source_code}\n### 結果："

        # 如果使用者選擇 OpenAI，且有 API Key
        if model_choice == "openai" and OPENAI_API_KEY:
            try:
                client = openai.OpenAI(api_key = OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-4-turbo",  # 可以改成 gpt-3.5-turbo
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.3
                )
                converted_code = response.choices[0].message.content
            except Exception as e:
                return jsonify({"error": f"OpenAI API 出錯: {str(e)}"}), 500

        # 如果選擇使用 Gemma
        elif model_choice == "huggingface":
            try:
                headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{HF_MODEL_NAME}",
                    headers=headers,
                    json={"inputs": prompt}
                )
                result = response.json()
                converted_code = result[0]["generated_text"] if isinstance(result, list) else "Hugging Face API 出錯"
            except Exception as e:
                return jsonify({"error": f"Hugging Face API 出錯: {str(e)}"}), 500

        else:
            return jsonify({"error": "未提供有效的模型選擇"}), 400

        return jsonify({"converted_code": converted_code})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
