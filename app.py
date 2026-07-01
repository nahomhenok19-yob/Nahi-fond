from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secretkey123"

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# User table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']

        new_user = User(username=user, password=pw)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']

        found_user = User.query.filter_by(username=user, password=pw).first()

        if found_user:
            session['user'] = user
            return redirect(url_for('dashboard'))
        else:
            return "Invalid login"

    return render_template('login.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect(url_for('login'))

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    from flask import Flask, render_template, request, redirect, session, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/videos"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# simple memory storage (upgrade later to DB)
users = {"admin": "1234"}
videos = []

# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users and users[u] == p:
            session["user"] = u
            return redirect("/dashboard")

    return render_template("login.html")

# DASHBOARD (TikTok feed)
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", user=session["user"], videos=videos)

# UPLOAD VIDEO
@app.route("/upload", methods=["GET","POST"])
def upload():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        file = request.files["video"]
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        videos.append(filename)

        return redirect("/dashboard")

    return render_template("upload.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
    from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from models import db, User, Video, Like, Comment, Follow

app = Flask(__name__)
app.secret_key = "secretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["UPLOAD_FOLDER"] = "uploads"

db.init_app(app)

with app.app_context():
    db.create_all()

# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        display_name = request.form["display_name"]

        user = User(username=username, password=password, display_name=display_name)
        db.session.add(user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")

# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            return redirect("/feed")

    return render_template("login.html")

# FEED (TikTok style)
@app.route("/feed")
def feed():
    if "user_id" not in session:
        return redirect("/")

    videos = Video.query.all()
    user = User.query.get(session["user_id"])

    return render_template("feed.html", videos=videos, user=user)

# UPLOAD VIDEO
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["video"]
    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)

    video = Video(filename=filename, user_id=session["user_id"])
    db.session.add(video)
    db.session.commit()

    return redirect("/feed")

# LIKE
@app.route("/like/<int:video_id>")
def like(video_id):
    like = Like(user_id=session["user_id"], video_id=video_id)
    db.session.add(like)
    db.session.commit()
    return redirect("/feed")

# COMMENT
@app.route("/comment/<int:video_id>", methods=["POST"])
def comment(video_id):
    text = request.form["text"]

    c = Comment(user_id=session["user_id"], video_id=video_id, text=text)
    db.session.add(c)
    db.session.commit()

    return redirect("/feed")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
    class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    user_id = db.Column(db.Integer)

    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.Integer, default=0)
    def get_likes(video_id):
    return Like.query.filter_by(video_id=video_id).count()

def get_comments(video_id):
    return Comment.query.filter_by(video_id=video_id).count()
    def score_video(video, user_id):

    likes = Like.query.filter_by(video_id=video.id).count()
    comments = Comment.query.filter_by(video_id=video.id).count()
    views = video.views

    # check if user follows creator
    follow_boost = Follow.query.filter_by(
        follower_id=user_id,
        following_id=video.user_id
    ).count() * 20

    score = (
        likes * 3 +
        comments * 5 +
        views * 1 +
        follow_boost
    )

    return score
    @app.route("/feed")
def feed():
    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    videos = Video.query.all()

    ranked_videos = sorted(
        videos,
        key=lambda v: score_video(v, user_id),
        reverse=True
    )

    return render_template("feed.html", videos=ranked_videos)
    @app.route("/view/<int:video_id>")
def view(video_id):
    video = Video.query.get(video_id)
    video.views += 1
    db.session.commit()
    return "ok"
    import pandas as pd

def build_features(user_id, videos):

    data = []

    for v in videos:
        likes = Like.query.filter_by(video_id=v.id).count()
        comments = Comment.query.filter_by(video_id=v.id).count()
        views = v.views

        follow = Follow.query.filter_by(
            follower_id=user_id,
            following_id=v.user_id
        ).count()

        data.append([
            likes,
            comments,
            views,
            follow
        ])

    df = pd.DataFrame(data, columns=[
        "likes", "comments", "views", "follow"
    ])

    return df
    from sklearn.ensemble import RandomForestRegressor
import numpy as np

model = RandomForestRegressor()

# training data (example - in real system this grows over time)
X_train = [
    [10, 5, 100, 1],
    [2, 1, 50, 0],
    [50, 20, 1000, 1],
    [1, 0, 10, 0]
]

y_train = [80, 20, 300, 5]  # engagement score

model.fit(X_train, y_train)
def ai_score(video, user_id):

    likes = Like.query.filter_by(video_id=video.id).count()
    comments = Comment.query.filter_by(video_id=video.id).count()
    views = video.views

    follow = Follow.query.filter_by(
        follower_id=user_id,
        following_id=video.user_id
    ).count()

    features = np.array([[likes, comments, views, follow]])

    score = model.predict(features)[0]

    return score
    @app.route("/feed")
def feed():

    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]
    videos = Video.query.all()

    ranked = sorted(
        videos,
        key=lambda v: ai_score(v, user_id),
        reverse=True
    )

    return render_template("feed.html", videos=ranked)
    class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer)
    following_id = db.Column(db.Integer)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    video_id = db.Column(db.Integer)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    video_id = db.Column(db.Integer)
    text = db.Column(db.String(300))
    @app.route("/follow/<int:user_id>")
def follow(user_id):

    me = session["user_id"]

    existing = Follow.query.filter_by(
        follower_id=me,
        following_id=user_id
    ).first()

    if not existing:
        db.session.add(Follow(
            follower_id=me,
            following_id=user_id
        ))
        db.session.commit()

    return "followed"
    @app.route("/like/<int:video_id>")
def like(video_id):

    me = session["user_id"]

    existing = Like.query.filter_by(
        user_id=me,
        video_id=video_id
    ).first()

    if not existing:
        db.session.add(Like(user_id=me, video_id=video_id))
        db.session.commit()

    return "liked"
    @app.route("/comment/<int:video_id>", methods=["POST"])
def comment(video_id):

    text = request.form["text"]

    db.session.add(Comment(
        user_id=session["user_id"],
        video_id=video_id,
        text=text
    ))

    db.session.commit()

    return "ok"
    @app.route("/feed")
def feed():

    me = session["user_id"]

    following = Follow.query.filter_by(follower_id=me).all()
    following_ids = [f.following_id for f in following]

    videos = Video.query.filter(Video.user_id.in_(following_ids)).all()

    if not videos:
        videos = Video.query.all()

    return render_template("feed.html", videos=videos)
    <!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body{
    margin:0;
    background:black;
    font-family:Arial;
    color:white;
}

/* FEED */
.feed{
    height:100vh;
    overflow-y:scroll;
    scroll-snap-type:y mandatory;
}

/* VIDEO */
.videoBox{
    height:100vh;
    position:relative;
    scroll-snap-align:start;
}

video{
    width:100%;
    height:100%;
    object-fit:cover;
}

/* RIGHT ACTION BAR */
.actions{
    position:absolute;
    right:12px;
    bottom:120px;
    display:flex;
    flex-direction:column;
    gap:20px;
}

.icon{
    width:55px;
    height:55px;
    border-radius:50%;
    background:rgba(255,0,0,0.15);
    border:1px solid red;
    display:flex;
    align-items:center;
    justify-content:center;
}

/* USER INFO */
.user{
    position:absolute;
    bottom:90px;
    left:15px;
}

.username{
    color:red;
    font-weight:bold;
}

/* FOLLOW BUTTON */
.follow{
    background:red;
    color:black;
    padding:6px 10px;
    border-radius:10px;
    font-size:12px;
    border:none;
}

/* COMMENT BOX */
.commentBox{
    position:fixed;
    bottom:0;
    width:100%;
    background:black;
    border-top:1px solid red;
    display:flex;
}

input{
    flex:1;
    padding:10px;
    background:black;
    border:none;
    color:white;
}

button{
    background:red;
    border:none;
    padding:10px;
}
</style>
</head>

<body>

<div class="feed">

{% for v in videos %}
<div class="videoBox">

    <video src="/uploads/{{v.filename}}" autoplay loop muted></video>

    <!-- ACTIONS -->
    <div class="actions">
        <div class="icon">❤️</div>
        <div class="icon">💬</div>
        <div class="icon">↗</div>
    </div>

    <!-- USER -->
    <div class="user">
        <div class="username">@user{{v.user_id}}</div>
        <button class="follow">Follow</button>
    </div>

</div>
{% endfor %}

</div>

<!-- COMMENT BAR -->
<form class="commentBox">
    <input placeholder="Add comment...">
    <button>Send</button>
</form>

<script>

/* SHARE SYSTEM */
document.querySelectorAll(".icon")[2].onclick = function(){
    navigator.clipboard.writeText(window.location.href);
    alert("Link copied 🔗");
}

/* FOLLOW BUTTON */
document.querySelectorAll(".follow").forEach(btn=>{
    btn.onclick = function(){
        btn.innerText = "Following";
        btn.style.background = "white";
        btn.style.color = "black";
    }
});

</script>

</body>
</html>
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# ONLINE USERS
online_users = {}

@app.route("/")
def home():
    return render_template("chat.html")

# USER CONNECTED
@socketio.on("connect_user")
def connect_user(data):
    username = data["username"]
    online_users[username] = request.sid

    emit("user_status", {"user": username, "status": "online"}, broadcast=True)

# PRIVATE MESSAGE
@socketio.on("private_message")
def private_message(data):
    receiver = data["to"]
    sender = data["from"]
    message = data["message"]

    if receiver in online_users:
        emit("new_message", {
            "from": sender,
            "message": message
        }, room=online_users[receiver])

# VIDEO / VOICE SIGNAL (WebRTC)
@socketio.on("call_signal")
def call_signal(data):
    target = data["to"]

    if target in online_users:
        emit("call_signal", data, room=online_users[target])

if __name__ == "__main__":
    socketio.run(app, debug=True)
    from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route("/")
def index():
    return render_template("call.html")

@socketio.on("join")
def join(data):
    username = data["username"]
    users[username] = request.sid

# SEND OFFER
@socketio.on("offer")
def offer(data):
    target = data["to"]
    if target in users:
        emit("offer", data, room=users[target])

# SEND ANSWER
@socketio.on("answer")
def answer(data):
    target = data["to"]
    if target in users:
        emit("answer", data, room=users[target])

# ICE CANDIDATES
@socketio.on("candidate")
def candidate(data):
    target = data["to"]
    if target in users:
        emit("candidate", data, room=users[target])

if __name__ == "__main__":
    socketio.run(app, debug=True)
    from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

@app.route("/")
def home():
    return render_template("group.html")

@socketio.on("join-room")
def join_room_event(data):
    room = data["room"]
    user = data["user"]

    join_room(room)

    if room not in rooms:
        rooms[room] = []

    rooms[room].append(request.sid)

    emit("user-connected", {
        "user": user,
        "id": request.sid
    }, room=room)

# SIGNALING (OFFER/ANSWER)
@socketio.on("signal")
def signal(data):
    emit("signal", data, room=data["to"])

@socketio.on("disconnect")
def disconnect():
    emit("user-disconnected", {"id": request.sid}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
    class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    user_id = db.Column(db.Integer)

    tag = db.Column(db.String(50))   # 🔥 IMPORTANT
    def get_similar_videos(current_video):

    tag = current_video.tag

    videos = Video.query.filter_by(tag=tag).all()

    # fallback if empty
    if not videos:
        videos = Video.query.all()

    return videos
    @app.route("/feed/<int:video_id>")
def feed(video_id):

    current = Video.query.get(video_id)

    videos = get_similar_videos(current)

    return render_template("feed.html", videos=videos)
    def ai_score(video, user_id):

    likes = Like.query.filter_by(video_id=video.id).count()
    comments = Comment.query.filter_by(video_id=video.id).count()
    views = video.views

    same_tag_boost = 10  # similarity boost

    score = (likes*3) + (comments*5) + (views*1) + same_tag_boost

    return score
    @app.route("/feed")
def feed():

    videos = Video.query.all()

    ranked = sorted(videos, key=lambda v: ai_score(v, session["user_id"]), reverse=True)

    return render_template("feed.html", videos=ranked)
    from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route("/")
def home():
    return render_template("chat.html")

# JOIN
@socketio.on("join")
def join(data):
    users[data["user"]] = request.sid
    emit("system", {"msg": f"{data['user']} joined chat"}, broadcast=True)

# MESSAGE
@socketio.on("message")
def message(data):
    to = data["to"]

    msg_data = {
        "from": data["from"],
        "message": data["message"]
    }

    # send to receiver
    if to in users:
        emit("private_message", msg_data, room=users[to])

    # send back to sender (sync UI)
    emit("private_message", msg_data, room=request.sid)

# AI AUTO REPLY (simple smart system)
@socketio.on("ai_reply")
def ai_reply(data):

    text = data["message"].lower()

    if "hi" in text:
        reply = "👋 Hello! How are you?"
    elif "video" in text:
        reply = "🎥 Check trending videos!"
    else:
        reply = "🤖 I am NAHI FOND AI chat bot"

    emit("private_message", {
        "from":"AI",
        "message":reply
    }, room=request.sid)

if __name__ == "__main__":
    socketio.run(app, debug=True)
    import openai

openai.api_key = "YOUR_OPENAI_API_KEY"
from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)

openai.api_key = "YOUR_OPENAI_API_KEY"

# simple memory storage (per user session)
chat_memory = {}

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ai", methods=["POST"])
def ai_chat():

    data = request.json
    user = data["user"]
    message = data["message"]

    # create memory if not exists
    if user not in chat_memory:
        chat_memory[user] = []

    chat_memory[user].append({"role":"user","content":message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_memory[user]
    )

    ai_reply = response["choices"][0]["message"]["content"]

    chat_memory[user].append({"role":"assistant","content":ai_reply})

    return jsonify({"reply": ai_reply})

if __name__ == "__main__":
    app.run(debug=True)
    from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import openai

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

openai.api_key = "YOUR_OPENAI_API_KEY"

users = {}

# HOME
@app.route("/")
def home():
    return render_template("chat.html")

# REGISTER USER ONLINE
@socketio.on("join")
def join(data):
    users[data["user"]] = request.sid
    emit("status", {"msg": f"{data['user']} online"}, broadcast=True)

# USER CHAT
@socketio.on("message")
def message(data):
    to = data["to"]

    if to in users:
        emit("private_message", data, room=users[to])

    emit("private_message", data, room=request.sid)

# AI VOICE TEXT REQUEST
@app.route("/ai", methods=["POST"])
def ai():
    text = request.json["text"]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":text}]
    )

    reply = response["choices"][0]["message"]["content"]

    return jsonify({"reply": reply})

if __name__ == "__main__":
    socketio.run(app, debug=True)
    from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
import os
import openai

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

openai.api_key = "YOUR_OPENAI_API_KEY"

users = {}

@app.route("/")
def home():
    return render_template("chat.html")

# 📁 FILE UPLOAD
@app.route("/upload", methods=["POST"])
def upload_file():

    file = request.files["file"]
    sender = request.form["sender"]
    receiver = request.form["receiver"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    # send file info to receiver via socket
    socketio.emit("file_received", {
        "from": sender,
        "filename": file.filename
    }, room=users.get(receiver, ""))

    return jsonify({"msg":"file sent"})

# 🤖 AI FILE ANALYSIS (text only demo)
@app.route("/analyze", methods=["POST"])
def analyze():

    text = request.json["text"]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":"Analyze this file content: " + text}]
    )

    return jsonify({"ai": response["choices"][0]["message"]["content"]})

# 👥 USER CONNECT
@socketio.on("join")
def join(data):
    users[data["user"]] = request.sid

if __name__ == "__main__":
    socketio.run(app, debug=True)
    from flask import Flask, request, jsonify, render_template
import openai
import os
import cv2

app = Flask(__name__)
UPLOAD = "uploads"
os.makedirs(UPLOAD, exist_ok=True)

openai.api_key = "YOUR_OPENAI_API_KEY"


# -------------------------
# 🖼️ IMAGE AI ANALYSIS
# -------------------------
@app.route("/analyze-image", methods=["POST"])
def analyze_image():

    file = request.files["file"]
    path = os.path.join(UPLOAD, file.filename)
    file.save(path)

    with open(path, "rb") as img:

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role":"user",
                    "content":[
                        {"type":"text","text":"Describe this image in detail"},
                        {"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"}}
                    ]
                }
            ]
        )

    return jsonify({"result":"Image received and analyzed (connect vision API properly)"})


# -------------------------
# 🎥 VIDEO AI ANALYSIS
# -------------------------
@app.route("/analyze-video", methods=["POST"])
def analyze_video():

    file = request.files["file"]
    path = os.path.join(UPLOAD, file.filename)
    file.save(path)

    cap = cv2.VideoCapture(path)

    frames = []
    count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if count % 30 == 0:  # every 30 frames
            frame_path = f"{UPLOAD}/frame_{count}.jpg"
            cv2.imwrite(frame_path, frame)
            frames.append(frame_path)

        count += 1

    cap.release()

    return jsonify({
        "frames_analyzed": len(frames),
        "message":"Video broken into frames for AI analysis"
    })


# -------------------------
# 🎨 IMAGE GENERATION (TEXT → IMAGE)
# -------------------------
@app.route("/generate-image", methods=["POST"])
def generate_image():

    prompt = request.json["prompt"]

    response = openai.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    image_url = response.data[0].url

    return jsonify({"image": image_url})


@app.route("/")
def home():
    return render_template("ai.html")


if __name__ == "__main__":
    app.run(debug=True)
    from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)
openai.api_key = "YOUR_OPENAI_API_KEY"

# demo data (replace with DB later)
users = ["henok", "nahi", "alex", "john"]
videos = [
    {"title":"dance video", "tag":"dance"},
    {"title":"coding tutorial", "tag":"tech"},
    {"title":"funny cats", "tag":"funny"}
]

@app.route("/")
def home():
    return render_template("search.html")

# 🔎 SEARCH SYSTEM
@app.route("/search", methods=["GET"])
def search():

    q = request.args.get("q").lower()

    # 👤 user search
    user_result = [u for u in users if q in u.lower()]

    # 🎬 content search
    video_result = [v for v in videos if q in v["title"] or q in v["tag"]]

    return jsonify({
        "users": user_result,
        "videos": video_result
    })

# 🤖 AI SEARCH (ChatGPT inside search bar)
@app.route("/ai-search", methods=["POST"])
def ai_search():

    q = request.json["q"]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":q}]
    )

    return jsonify({
        "ai_result": response["choices"][0]["message"]["content"]
    })

if __name__ == "__main__":
    app.run(debug=True)
    from flask import Flask, request, render_template, jsonify
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📦 STORE POSTS (replace with DB later)
posts = []

@app.route("/")
def home():
    return render_template("upload.html")

# 📤 UPLOAD FILE + DESCRIPTION
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]
    desc = request.form["description"]
    user = request.form["user"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    posts.append({
        "user": user,
        "file": file.filename,
        "description": desc
    })

    return jsonify({"msg":"uploaded successfully"})

# 📺 FEED
@app.route("/feed")
def feed():
    return jsonify(posts)

if __name__ == "__main__":
    app.run(debug=True)
    from flask import Flask, render_template, request, jsonify, redirect, session
import os

app = Flask(__name__)
app.secret_key = "nahi_fond_secret"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📦 DATABASE (temporary but clean)
posts = []
users = {"admin": "1234"}

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users and users[u] == p:
            session["user"] = u
            return redirect("/feed")

        return "Invalid login"

    return render_template("login.html")


# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":

        file = request.files["file"]
        desc = request.form["description"]
        user = session.get("user","guest")

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        posts.append({
            "user": user,
            "file": file.filename,
            "description": desc
        })

        return redirect("/feed")

    return render_template("upload.html")


# ---------------- FEED ----------------
@app.route("/feed")
def feed():
    return render_template("feed.html", posts=posts)


if __name__ == "__main__":
    app.run(debug=True)
    from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "nahi_fond_secret"

# 📦 DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nahi_fond.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    filename = db.Column(db.String(200))
    description = db.Column(db.String(300))

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)
    text = db.Column(db.String(300))

# ---------------- INIT DB ----------------
with app.app_context():
    db.create_all()

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        user = User.query.filter_by(username=u, password=p).first()

        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect("/feed")

        return "Invalid login"

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    u = request.form["username"]
    p = request.form["password"]

    new_user = User(username=u, password=p)
    db.session.add(new_user)
    db.session.commit()

    return redirect("/login")

# ---------------- UPLOAD POST ----------------
@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":

        file = request.files["file"]
        desc = request.form["description"]

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        post = Post(
            user_id=session["user_id"],
            filename=file.filename,
            description=desc
        )

        db.session.add(post)
        db.session.commit()

        return redirect("/feed")

    return render_template("upload.html")

# ---------------- FEED ----------------
@app.route("/feed")
def feed():
    posts = Post.query.all()
    users = User.query.all()

    user_map = {u.id: u.username for u in users}

    return render_template("feed.html", posts=posts, user_map=user_map)

# ---------------- LIKE ----------------
@app.route("/like/<int:post_id>")
def like(post_id):

    user_id = session["user_id"]

    existing = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

    if not existing:
        db.session.add(Like(user_id=user_id, post_id=post_id))
        db.session.commit()

    return redirect("/feed")

# ---------------- COMMENT ----------------
@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):

    text = request.form["text"]

    db.session.add(Comment(
        user_id=session["user_id"],
        post_id=post_id,
        text=text
    ))

    db.session.commit()

    return redirect("/feed")


if __name__ == "__main__":
    app.run(debug=True)
    