        prompt = f"""Translate the following {source_lang} code to {target_lang}:
```{source_lang.lower()}
{source_code}
Output only the translated code without explanations. """