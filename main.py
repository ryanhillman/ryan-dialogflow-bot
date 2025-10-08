from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

RESUME_URL = "https://storage.googleapis.com/ryan-resume-bucket/resume.json"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    intent = req.get('queryResult', {}).get('intent', {}).get('displayName')

    try:
        data = requests.get(RESUME_URL).json()
    except Exception as e:
        return jsonify({"fulfillmentText": f"Error loading resume: {str(e)}"})

    response_text = ""

    # --- Welcome ---
    if intent == "WELCOME":
        response_text = (
            "Hello! 👋 This is Ryan's interactive resume assistant. "
            "You can ask me about Ryan's skills, programming languages, "
            "experience, certifications, education, contact information, or awards."
        )

    # --- Skills (summary) ---
    elif intent == "Skills":
        skills = data.get("skills", {}).get("highlights", [])
        if skills:
            response_text = "Ryan's key skills include: " + ", ".join(skills) + "."
        else:
            response_text = "Ryan's skill information is currently unavailable."

    # --- Programming Languages ---
    elif intent == "ProgrammingLanguages":
        langs = data.get("skills", {}).get("programming_languages", [])
        if langs:
            response_text = "Ryan is experienced with the following programming languages: " + ", ".join(langs) + "."
        else:
            response_text = "Ryan's programming language information is currently unavailable."

    # --- Certifications ---
    elif intent == "Certifications":
        certs = data.get("certifications", [])
        response_text = "Ryan has earned certifications such as: " + "; ".join(certs) + "."

    # --- General Experience ---
    elif intent == "Experience":
        exp = data.get("experience", [])
        job_texts = []
        for job in exp:
            company = job.get("company", "")
            years = job.get("years", "")
            role = job.get("role", "")
            job_texts.append(f"{role} at {company} ({years})")
        response_text = "Here is Ryan's professional experience: " + ", ".join(job_texts) + "."

    # --- Accenture-specific Experience ---
    elif intent == "AccentureExperience":
        acc = next((j for j in data.get("experience", []) if j.get("company") == "Accenture"), None)
        if acc:
            roles = []
            for r in acc.get("roles", []):
                role = r.get("role", "")
                client = r.get("client", "")
                year = r.get("client_year", "")
                roles.append(f"{role} at {client} ({year})")
            response_text = f"During his time at Accenture ({acc.get('years')}), Ryan contributed as: " + ", ".join(roles) + "."
        else:
            response_text = "Ryan’s Accenture experience details could not be found."

    # --- Education ---
    elif intent == "Education":
        edu = data.get("education", {})
        response_text = f"Ryan completed his {edu.get('degree', '')} in {edu.get('concentration', '')} with a {edu.get('option', '')} option at {edu.get('school', '')}, graduating in {edu.get('year', '')}."

    # --- Awards ---
    elif intent == "Awards":
        awards = data.get("awards", [])
        response_text = "Ryan has been recognized with awards such as: " + "; ".join(awards) + "."

    # --- Contact ---
    elif intent == "Contact":
        contact = data.get("contact", {})
        phone = contact.get("phone", "")
        email = contact.get("email", "")
        location = contact.get("location", "")
        response_text = f"Here is Ryan's contact information: Phone: {phone}, Email: {email}, Location: {location}."

    # --- Fallback ---
    else:
        response_text = (
            "Sorry, I didn’t quite catch that. "
            "Try asking about Ryan's skills, programming languages, "
            "experience, certifications, education, contact information, or awards."
        )

    return jsonify({"fulfillmentText": response_text})

if __name__ == '__main__':
    app.run(debug=True)
