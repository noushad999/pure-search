from flask import Flask, request, render_template_string, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session management

# Fake index
INDEX = {
    "https://en.wikipedia.org/wiki/Space": {
        "title": "Space - Wikipedia",
        "text": "Space is the boundless three-dimensional extent in which objects exist..."
    },
    "https://www.nasa.gov": {
        "title": "NASA",
        "text": "NASA explores space and aeronautics for the benefit of all..."
    },
    "https://www.google.com": {
        "title": "Google",
        "text": "Google is a search engine..."
    },
    "https://www.x.com": {
        "title": "X",
        "text": "X is a social media platform..."
    },
    "https://www.gmail.com": {
        "title": "Gmail",
        "text": "Gmail is an email service..."
    },
    "https://meet.google.com/": {
        "title": "Google Meet",
        "text": "Google Meet is a video conferencing service..."
    },
    "https://bangla.bdnews24.com/": {
        "title": "News24",
        "text": "News24 is a news portal..."
    }
}

# Stats tracking
adult_search_count = 0
blocked_count = 0
active_users = {}  # Dictionary to track user sessions by IP and timestamp

def search_index(query):
    global adult_search_count, blocked_count
    blacklist = [
        "pornhub", "xvideos", "adult", "xxx", "porn", "sex", "nude",
        "redtube", "youporn", "bangbros", "chaturbate"
    ]
    
    # Check if query contains a blacklisted term
    if any(bad in query.lower() for bad in blacklist):
        adult_search_count += 1
        blocked_count += 1
        return [{"warning": "God is watching you"}]
    
    # Normal search
    results = []
    for url, data in INDEX.items():
        if any(bad in data["text"].lower() or bad in data["title"].lower() for bad in blacklist):
            continue
        if query.lower() in data["text"].lower():
            results.append({
                "url": url,
                "title": data["title"],
                "snippet": data["text"][:100] + "..." if len(data["text"]) > 100 else data["text"]
            })
    return results

def update_active_users():
    # Simulate live users by tracking IPs with timestamps
    global active_users
    user_ip = request.remote_addr
    active_users[user_ip] = datetime.now()
    # Remove users inactive for more than 5 minutes
    active_users = {ip: ts for ip, ts in active_users.items() if datetime.now() - ts < timedelta(minutes=5)}
    return len(active_users)

# HTML templates with stats
HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PureSearch</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #f0f4f8, #e0e7ff);
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 90%;
        }
        h1 {
            color: #1e3a8a;
            font-size: 36px;
            margin-bottom: 20px;
        }
        form {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #dbe2ef;
            border-radius: 25px;
            outline: none;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            border-color: #3b82f6;
        }
        button {
            padding: 12px 20px;
            font-size: 16px;
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #1e3a8a;
        }
        .stats {
            margin-top: 20px;
            font-size: 14px;
            color: #4b5563;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PureSearch</h1>
        <form method="POST">
            <input type="text" name="query" placeholder="Search the pure web...">
            <button type="submit">Search</button>
        </form>
        <div class="stats">
            <p>Adult site searches attempted: {{ adult_count }}</p>
            <p>Successfully blocked: {{ blocked_count }}</p>
            <p>Live users: {{ live_users }}</p>
        </div>
    </div>
</body>
</html>
"""

RESULTS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PureSearch - Results</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #f0f4f8, #e0e7ff);
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #1e3a8a;
            font-size: 28px;
            margin-bottom: 20px;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            margin-bottom: 15px;
            padding: 10px;
            border-bottom: 1px solid #dbe2ef;
        }
        a {
            color: #3b82f6;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
        }
        a:hover {
            text-decoration: underline;
        }
        .snippet {
            color: #4b5563;
            font-size: 14px;
        }
        .warning {
            color: #dc2626;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        .back-btn {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #3b82f6;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: background-color 0.3s;
        }
        .back-btn:hover {
            background-color: #1e3a8a;
        }
        .stats {
            margin-top: 20px;
            font-size: 14px;
            color: #4b5563;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Results for "{{ query }}"</h1>
        {% if results and results[0].warning %}
            <div class="warning">{{ results[0].warning }}</div>
        {% else %}
            <ul>
            {% for result in results %}
                <li>
                    <a href="{{ result.url }}" target="_blank">{{ result.title }}</a>
                    <div class="snippet">{{ result.snippet }}</div>
                </li>
            {% endfor %}
            </ul>
            {% if not results %}
                <p>No results found. Try something else!</p>
            {% endif %}
        {% endif %}
        <a href="/" class="back-btn">Back to Search</a>
        <div class="stats">
            <p>Adult site searches attempted: {{ adult_count }}</p>
            <p>Successfully blocked: {{ blocked_count }}</p>
            <p>Live users: {{ live_users }}</p>
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    global adult_search_count, blocked_count
    live_users = update_active_users()
    
    if request.method == "POST":
        query = request.form["query"]
        results = search_index(query)
        return render_template_string(
            RESULTS_PAGE,
            query=query,
            results=results,
            adult_count=adult_search_count,
            blocked_count=blocked_count,
            live_users=live_users
        )
    return render_template_string(
        HOME_PAGE,
        adult_count=adult_search_count,
        blocked_count=blocked_count,
        live_users=live_users
    )

if __name__ == "__main__":
    app.run(debug=True)