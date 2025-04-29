import openai
from flask import Flask, request, render_template, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re

app = Flask(__name__)

# API Keys（請替換為你自己的金鑰）
OPENAI_API_KEY = "your-openai-api-key"
HUGGINGFACE_API_KEY = "your-huggingface-api-key"

# Hugging Face 模型資訊
HF_MODEL_NAME = 'bigcode/StarCoder2-3B'
device = "cuda" if torch.cuda.is_available() else "cpu"

# 載入 tokenizer 和模型，並放置到對應設備上（GPU 或 CPU）
hf_tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME, trust_remote_code=True)
hf_model = AutoModelForCausalLM.from_pretrained(HF_MODEL_NAME, trust_remote_code=True).to(device)

# 從 Hugging Face 模型輸出中提取翻譯後的程式碼

def extract_translated_code(generated_text, prompt, target_lang):
    pattern = rf"```{target_lang.lower()}\s*(.*?)```"
    matches = re.findall(pattern, generated_text, re.DOTALL)
    if matches:
        return matches[0].strip()
    cleaned = generated_text.replace(prompt, "").strip()
    return cleaned.split('\n')[0].strip()

# 從 OpenAI 回傳的內容中擷取翻譯後的程式碼區塊
def extract_openai_code(response_text, target_lang):
    pattern = rf"```{target_lang.lower()}\s*(.*?)```"
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response_text.strip()

@app.route('/', methods=['GET', 'POST'])
def convert_code():
    if request.method == 'GET':
        return render_template('index.html', title='程式碼轉換工具')

    if request.method == 'POST':
        data = request.get_json(force=True)

        print(data)  # Debug
        source_code = data['code']
        source_lang = data['source_lang']
        target_lang = data['target_lang']
        model_choice = data['model']

        # 強化 prompt 格式
        prompt = f"""<filename>solutions/translate_solution.{target_lang.lower()}
        # Here is the correct {target_lang} translation of the provided {source_lang} code.

        Respond with only the translated code inside a code block. Do not add explanations, comments, or examples.

        Example output format:
        ```{target_lang.lower()}
        console.log("Hello");
        Now, please translate the following {source_lang} code:
        {source_code}
        ```"""

        if model_choice == "openai" and OPENAI_API_KEY:
            try:
                openai.api_key = OPENAI_API_KEY
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3
                )
                raw_output = response['choices'][0]['message']['content']
                converted_code = extract_openai_code(raw_output, target_lang)
            except Exception as e:
                return jsonify({"error": f"OpenAI API 出錯: {str(e)}"}), 500

        elif model_choice == "huggingface":
            try:
                inputs = hf_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
                outputs = hf_model.generate(
                    **inputs,
                    max_length=300,
                    temperature=0.5,
                    num_return_sequences=1,
                    top_p=0.95,
                    do_sample=True
                )
                raw_output = hf_tokenizer.decode(outputs[0], skip_special_tokens=True)
                converted_code = extract_translated_code(raw_output, prompt, target_lang)
            except Exception as e:
                return jsonify({"error": f"Hugging Face API 出錯: {str(e)}"}), 500

        else:
            return jsonify({"error": "未提供有效的模型選擇"}), 400

        return jsonify({"converted_code": converted_code})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
