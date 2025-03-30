import openai
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

openai.api_key = 'your-api-key-here'  # 設置你的 API 金鑰

@app.route('/', methods=['GET', 'POST'])
def convert_code():
    # 在這裡設置標題
    title = 'Code Converter'

    if request.method == 'GET':
        # 渲染頁面並傳遞標題給模板
        return render_template('index.html', title=title)

    if request.method == 'POST':
        # 從前端接收 JSON 資料
        data = request.json
        
        # 解析前端發送過來的資料
        source_code = data['code']
        source_lang = data['source_lang']
        target_lang = data['target_lang']
        model_host = data['model']  # 獲取用戶選擇的模型
        
        # 根據 source_lang 和 target_lang 來構建提示 (prompt)
        prompt = f"將以下程式碼從 {source_lang} 轉換為 {target_lang}:\n\n{source_code}"
        
        # 呼叫 OpenAI API 執行轉換
        response = openai.ChatCompletion.create(
            model=model_host,  # 使用用戶選擇的模型
            messages=[
                {'role': 'system', 'content': '你是一個程式語言轉換器。'},
                {'role': 'user', 'content': prompt}
            ]
        )

        # 取得轉換後的程式碼
        converted_code = response['choices'][0]['message']['content']
        
        # 回傳轉換後的程式碼給前端
        return jsonify({'converted_code': converted_code})

if __name__ == '__main__':
    app.run(debug=True , port = 5001)
