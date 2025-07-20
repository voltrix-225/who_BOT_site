from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from who_BOT import extract_username, user_exists, scrape_user_data, build_prompt, call_hf_router

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')  # HTML must include linked JS

@app.route('/generate_persona', methods=['POST'])
def generate_persona():
    profile_url = request.json.get("profileUrl")
    username = extract_username(profile_url)

    if not username:
        return jsonify({"error": "Invalid Reddit profile URL format."}), 400

    if not user_exists(username):
        return jsonify({"error": f"Reddit user '{username}' not found or suspended."}), 404

    try:
        raw_data = scrape_user_data(username)
        prompt = build_prompt(raw_data)
        persona = call_hf_router(prompt)
        return jsonify({"persona": persona})
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
