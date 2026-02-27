from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from openai import OpenAI
import os
import json

app = Flask(__name__)
app.secret_key = "mysecretkey"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------- CẤU HÌNH TỐI ƯU -----------
MAX_FREE_USES = 3
MAX_TOKENS = 500   # giảm token để tiết kiệm

# ----------- LOGIN -----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        session["user"] = username
        session["free_uses"] = MAX_FREE_USES  # cấp 3 lượt miễn phí
        return redirect(url_for("home"))
    return '''
        <form method="post">
            <h2>Đăng nhập</h2>
            <input name="username" placeholder="Nhập tên của bạn">
            <button type="submit">Vào hệ thống</button>
        </form>
    '''

# ----------- HOME -----------
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", user=session["user"])

# ----------- CHAT AI -----------
@app.route("/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"reply": "Vui lòng đăng nhập."})

    # ----------- GIỚI HẠN 3 LẦN MIỄN PHÍ -----------
    if session.get("free_uses", 0) <= 0:
        return jsonify({
            "reply": "Bạn đã hết 3 lượt miễn phí. Vui lòng nâng cấp để tiếp tục sử dụng."
        })

    user_message = request.json["message"]

    # ----------- CACHE (tránh gọi API nếu câu hỏi trùng) -----------
    if os.path.exists("history.json"):
        with open("history.json", "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                if record["question"] == user_message:
                    return jsonify({"reply": record["answer"]})

    # ----------- GỌI OPENAI -----------
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Bạn là AI cố vấn tương lai.
1. Phân tích mục tiêu
2. Đưa ra kỹ năng cần phát triển
3. Đề xuất lộ trình 3 năm
4. Kế hoạch hành động cụ thể
Trả lời súc tích, không lan man."""
            },
            {"role": "user", "content": user_message}
        ],
        temperature=0.5,   # giảm sáng tạo để tiết kiệm token
        max_tokens=MAX_TOKENS
    )

    reply = response.choices[0].message.content

    # ----------- TRỪ LƯỢT -----------
    session["free_uses"] -= 1

    # ----------- LƯU LỊCH SỬ -----------
    history = {
        "user": session.get("user"),
        "question": user_message,
        "answer": reply
    }

    with open("history.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(history, ensure_ascii=False) + "\n")

    return jsonify({"reply": reply})

# ----------- RUN SERVER -----------
if __name__ == "__main__":
    app.run()

  

