import PyPDF2

def analyze_resume(path):

    text = ""

    with open(path, "rb") as file:

        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            text += page.extract_text()

    words = len(text.split())

    score = 50

    if "Python" in text:
        score += 10

    if "SQL" in text:
        score += 10

    if "Machine Learning" in text:
        score += 15

    if words > 300:
        score += 15

    return {
        "ATS Score": score,
        "Words": words,
        "Preview": text[:500]
    }