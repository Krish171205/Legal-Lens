import subprocess

def summarize(text: str) -> str:
    prompt = (
        "Summarize the following legal document in concise, plain language:\n\n" + text
    )
    result = subprocess.run(
        [
            "ollama",
            "run",
            "bigbird-pegasus",
            "-p",
            prompt,
        ],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()