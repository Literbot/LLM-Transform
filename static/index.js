document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("codeForm").addEventListener("submit", async function (event) {
        event.preventDefault();

        let source_code = document.getElementById("code").value;
        let source_lang = document.getElementById("source_lang").value;
        let target_lang = document.getElementById("target_lang").value;
        let model_choice = document.getElementById("model").value;
        let openai_key = document.getElementById("openai_key").value;

        let data = {
            code: source_code,
            source_lang: source_lang,
            target_lang: target_lang,
            model: model_choice,
            openai_key: openai_key
        };

        try {
            let response = await fetch("/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            let result = await response.json();
            document.getElementById("result-box").textContent = result.converted_code || result.error;
        } catch (error) {
            document.getElementById("result-box").textContent = "錯誤: " + error.message;
        }
    });
});
