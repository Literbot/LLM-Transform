document.getElementById('convert-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const model = document.getElementById('model').value;
    const sourceCode = document.getElementById('source-code').value;
    const sourceLang = document.getElementById('source-lang').value;
    const targetLang = document.getElementById('target-lang').value;

    const response = await fetch('http://127.0.0.1:5001/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: model,
            code: sourceCode,
            source_lang: sourceLang,
            target_lang: targetLang
        })
    });
    
    const data = await response.json();
    document.getElementById('converted-code').textContent = data.converted_code;
});