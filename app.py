from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from openai import OpenAI
import os
import json

app = Flask(__name__)
app.secret_key = "mysecretkey"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------- LOGIN -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        session["user"] = username
        return redirect(url_for("home"))
    return '''
        <form method="post">
            <h2>Đăng nhập</h2>
            <input name="username" placeholder="Nhập tên của bạn">
            <button type="submit">Vào hệ thống</button>
        </form>
    '''

# ------------------- HOME -------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", user=session["user"])

# ------------------- CHAT AI -------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Bạn là AI cố vấn tương lai.
1. Phân tích mục tiêu của học sinh
2. Đưa ra kỹ năng cần phát triển
3. Đề xuất lộ trình 3 năm
4. Tạo kế hoạch hành động cụ thể từng bước
5. Truyền động lực tích cực"""
            },
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content

    # Lưu lịch sử
    history = {
        "user": session.get("user"),
        "question": user_message,
        "answer": reply
    }

    with open("history.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(history, ensure_ascii=False) + "\n")

    return jsonify({"reply": reply})

# ------------------- RUN SERVER -------------------
if __name__ == "__main__":
    app.run()


