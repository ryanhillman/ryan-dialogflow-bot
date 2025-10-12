from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

RESUME_URL = "https://storage.googleapis.com/ryan-resume-bucket/resume.json"

def load_resume():
    try:
        r = requests.get(RESUME_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)
    intent = (req.get("queryResult", {}).get("intent", {}) or {}).get("displayName", "")
    data = load_resume()

    if intent == "Experience":
        exps = data.get("experience", [])
        if not exps:
            return jsonify({"fulfillmentText": "No experience data found."})
        lines = [
            "Here is Ryan's professional experience",
            "",
        ]
        for job in exps:
            role = job.get("role", "")
            company = job.get("company", "")
            if role and company:
                lines.append(f"- {role} at {company}")
        return jsonify({"fulfillmentText": "\n".join(lines)})

    # ACCENTURE overview
    if intent == "Accenture":
        return jsonify({"fulfillmentText":
            "Ryan held two roles while at Accenture\n\n"
            "- Java Application Development with NYCERS (New York City Employees Retirement System)\n"
            "- Pegasystems Support and Development with BoA (Bank of America)\n\n"
            "- Would you like to hear more about either?"
        })

    # NYCERS details
    if intent in ["NYCERS Details", "Java Application Development Details", "New York City Employee Retirement System Details"]:
        accenture = next((x for x in data.get("experience", []) if x.get("company") == "Accenture"), {})
        bullets = accenture.get("details", {}).get("Java Application Development", [])
        if not bullets:
            return jsonify({"fulfillmentText": "No NYCERS details found."})
        text = "Java Application Developer for NYCERS\n\n" + "\n".join(f"- {b}" for b in bullets)
        return jsonify({"fulfillmentText": text})

    # BoA / Pegasystems details
    if intent in ["BoA Details", "Bank of America Details", "Pegasystems Support and Development Details"]:
        accenture = next((x for x in data.get("experience", []) if x.get("company") == "Accenture"), {})
        bullets = accenture.get("details", {}).get("Pegasystems Support and Development", [])
        if not bullets:
            return jsonify({"fulfillmentText": "No Bank of America details found."})
        text = "Pegasystems Support and Development for Bank of America\n\n" + "\n".join(f"- {b}" for b in bullets)
        return jsonify({"fulfillmentText": text})

    # SKILLS overview
    if intent == "Skills":
        return jsonify({"fulfillmentText":
            "Ryan has experience with Programming Languages, Frameworks, Platforms, and Tools. Which would you like to know more about?"
        })

    # SKILLS sub-intents
    if intent == "Languages":
        items = (data.get("skills", {}).get("Languages") or [])
        if not items:
            return jsonify({"fulfillmentText": "No languages found."})
        return jsonify({"fulfillmentText": "Ryan is skilled in\n\n" + "\n".join(f"- {x}" for x in items)})

    if intent == "Frameworks":
        items = (data.get("skills", {}).get("Frameworks") or [])
        if not items:
            return jsonify({"fulfillmentText": "No frameworks found."})
        return jsonify({"fulfillmentText": "Ryan has experience with\n\n" + "\n".join(f"- {x}" for x in items)})

    if intent == "Platforms":
        items = (data.get("skills", {}).get("Platforms") or [])
        if not items:
            return jsonify({"fulfillmentText": "No platforms found."})
        return jsonify({"fulfillmentText": "Ryan has worked with\n\n" + "\n".join(f"- {x}" for x in items)})

    if intent == "Tools":
        items = (data.get("skills", {}).get("Tools") or [])
        if not items:
            return jsonify({"fulfillmentText": "No tools found."})
        return jsonify({"fulfillmentText": "Ryan is familiar with\n\n" + "\n".join(f"- {x}" for x in items)})

    # EDUCATION 
    if intent == "Education":
        edu = data.get("education", {})
        school = edu.get("school", "")
        degree = edu.get("degree", "")
        grad = edu.get("graduation", "")
        text = f"Ryan earned his degree at {school}. It was a {degree}. He graduated in {grad}."
        return jsonify({"fulfillmentText": text})

    # CERTIFICATIONS
    if intent == "Certifications":
        certs = data.get("certifications", [])
        if not certs:
            return jsonify({"fulfillmentText": "No certifications found."})
        return jsonify({"fulfillmentText": "Ryan holds the following certifications\n\n" + "\n".join(f"- {c}" for c in certs)})

    # AWARDS
    if intent == "Awards":
        awards = data.get("awards", [])
        # allow either array of strings or array of {title, description}
        if isinstance(awards, list) and awards and isinstance(awards[0], dict):
            formatted = []
            for a in awards:
                title = a.get("title", "")
                desc = a.get("description", "")
                if title and desc:
                    formatted.append(f"- {title} - {desc}")
                elif title:
                    formatted.append(f"- {title}")
                elif desc:
                    formatted.append(f"- {desc}")
            return jsonify({"fulfillmentText": "Ryan has received the following awards\n\n" + "\n".join(formatted) if formatted else "No awards found."})
        elif isinstance(awards, list):
            return jsonify({"fulfillmentText": "Ryan has received the following awards\n\n" + "\n".join(f"- {a}" for a in awards) if awards else "No awards found."})
        else:
            return jsonify({"fulfillmentText": "No awards found."})

    # Fallback
    return jsonify({"fulfillmentText": "I can help with Ryan's experience, skills, education, certifications, and awards. Please ask about one!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

