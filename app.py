import os
import sqlite3
from functools import wraps
from datetime import datetime

from flask import (
    Flask,
    request,
    redirect,
    session,
    url_for,
    render_template_string,
    send_from_directory,
    abort,
)


# ============================================================
# ABHINANDAN FITNESS
# RITESH HQ
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "fitness.db")
STATIC_DIR = os.path.join(BASE_DIR, "static")
MEDIA_DIR = os.path.join(STATIC_DIR, "media")

MAIN_IMAGE = "abhinandan.jpg"

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static",
)

app.secret_key = os.environ["FLASK_SECRET_KEY"]


# ============================================================
# LOGIN
# ============================================================

USERNAME = os.environ["CREATOR_USERNAME"]
PASSWORD = os.environ["CREATOR_PASSWORD"]

# ============================================================
# CONSTANTS
# ============================================================

CATEGORIES = [
    "Workout",
    "Nutrition",
    "Mindset",
    "Motivation",
    "Fitness Knowledge",
]


EXERCISE_DATA = [
    {"name":"Bench Press","category":"Chest","level":"Beginner","description":"A basic chest pressing movement that also trains the shoulders and triceps.","steps":["Set up with a stable position and controlled grip.","Lower the weight with control while keeping a comfortable range of motion.","Press back up smoothly without rushing."],"safety":"Use appropriate supervision and a manageable load. Stop if you feel pain or unusual discomfort."},
    {"name":"Incline Dumbbell Press","category":"Chest","level":"Beginner","description":"A dumbbell pressing exercise performed on an incline bench.","steps":["Sit securely on an incline bench with the dumbbells controlled.","Lower both dumbbells slowly and evenly.","Press them upward with controlled movement."],"safety":"Choose a manageable weight and keep the movement controlled."},
    {"name":"Push-Ups","category":"Chest","level":"Beginner","description":"A bodyweight pushing exercise for the chest, shoulders and triceps.","steps":["Start in a stable plank position with hands comfortably placed.","Lower your body under control.","Push back to the starting position."],"safety":"Keep a comfortable range of motion and stop if you experience pain."},
    {"name":"Lat Pulldown","category":"Back","level":"Beginner","description":"A cable exercise that trains the upper back and pulling muscles.","steps":["Sit securely and grip the bar comfortably.","Pull the bar down with controlled movement.","Return the bar slowly to the starting position."],"safety":"Avoid jerking the weight or pulling behind the neck."},
    {"name":"Seated Cable Row","category":"Back","level":"Beginner","description":"A seated pulling exercise focused on the back and upper-body control.","steps":["Sit upright and hold the handle comfortably.","Pull toward your torso while keeping the movement controlled.","Slowly return to the starting position."],"safety":"Keep the load manageable and avoid using momentum."},
    {"name":"One-Arm Dumbbell Row","category":"Back","level":"Beginner","description":"A single-arm rowing movement for the back and pulling muscles.","steps":["Use a stable supported position.","Pull the dumbbell toward your torso under control.","Lower it slowly before repeating."],"safety":"Use a stable setup and a manageable weight."},
    {"name":"Shoulder Press","category":"Shoulders","level":"Beginner","description":"An overhead pressing movement that trains the shoulders and arms.","steps":["Start with a stable seated or standing position.","Press the weight upward in a controlled path.","Lower it slowly to the starting position."],"safety":"Use a comfortable range of motion and avoid forcing the movement."},
    {"name":"Lateral Raise","category":"Shoulders","level":"Beginner","description":"A light dumbbell movement commonly used to train the side shoulder muscles.","steps":["Hold light weights at your sides.","Raise your arms smoothly to a comfortable height.","Lower them slowly."],"safety":"Use light resistance and avoid swinging the weights."},
    {"name":"Face Pull","category":"Shoulders","level":"Beginner","description":"A cable movement that trains the upper back and shoulder-area muscles.","steps":["Set the cable at an appropriate height and hold the rope.","Pull the rope toward your face with control.","Return slowly to the starting position."],"safety":"Keep resistance manageable and avoid jerky movement."},
    {"name":"Dumbbell Curl","category":"Arms","level":"Beginner","description":"A simple arm exercise that trains the biceps.","steps":["Hold the dumbbells with a comfortable grip.","Curl the weights upward without swinging.","Lower them slowly."],"safety":"Use a manageable weight and keep the movement controlled."},
    {"name":"Hammer Curl","category":"Arms","level":"Beginner","description":"A curl variation using a neutral hand position.","steps":["Hold the dumbbells with palms facing inward.","Curl upward while keeping the elbows controlled.","Lower slowly."],"safety":"Avoid using body momentum to lift the weight."},
    {"name":"Triceps Pushdown","category":"Arms","level":"Beginner","description":"A cable exercise focused on the triceps.","steps":["Stand securely and hold the cable attachment.","Push the handle downward under control.","Return slowly to the starting position."],"safety":"Keep the load manageable and avoid locking or forcing the joints."},
    {"name":"Squat","category":"Legs","level":"Beginner","description":"A fundamental lower-body movement involving the hips and legs.","steps":["Stand with a comfortable stance.","Lower your body under control while maintaining balance.","Return to standing smoothly."],"safety":"Use a comfortable depth and learn technique before adding resistance."},
    {"name":"Leg Press","category":"Legs","level":"Beginner","description":"A machine-based lower-body pressing exercise.","steps":["Set up securely on the machine.","Press the platform away with controlled movement.","Return slowly without rushing."],"safety":"Follow the machine instructions and use a manageable resistance."},
    {"name":"Romanian Deadlift","category":"Legs","level":"Beginner","description":"A hip-hinge movement that trains the posterior chain.","steps":["Stand securely with the weight close to your body.","Hinge at the hips while keeping the movement controlled.","Return to standing by driving through the hips."],"safety":"Learn the hip-hinge technique before using significant resistance."},
    {"name":"Plank","category":"Core","level":"Beginner","description":"A bodyweight exercise for core stability.","steps":["Set up in a stable plank position.","Keep your body controlled and breathe normally.","Hold only for a comfortable duration."],"safety":"Stop if you feel pain and focus on good positioning rather than duration."},
    {"name":"Dead Bug","category":"Core","level":"Beginner","description":"A controlled core exercise that develops coordination and stability.","steps":["Lie comfortably on your back with arms and legs positioned safely.","Move opposite limbs slowly while keeping control.","Return to the starting position and alternate sides."],"safety":"Move slowly and keep the range of motion comfortable."},
    {"name":"Hanging Knee Raise","category":"Core","level":"Beginner","description":"A hanging movement that trains core control.","steps":["Use a secure support and establish a stable hanging position.","Raise the knees with controlled movement.","Lower them slowly."],"safety":"Use secure equipment and stop if your grip or control becomes unsafe."},
]

EXERCISES = [item["name"] for item in EXERCISE_DATA]
EXERCISE_CATEGORIES = ["All", "Chest", "Back", "Shoulders", "Arms", "Legs", "Core"]


KNOWLEDGE = [
    (
        "Consistency",
        "Progress comes from consistent and sensible habits over time."
    ),
    (
        "Recovery",
        "Rest and recovery are important parts of a balanced training routine."
    ),
    (
        "Safe Training",
        "Learn proper technique and use sensible training progression."
    ),
    (
        "Progressive Training",
        "Training can gradually become more challenging as skills improve."
    ),
    (
        "Nutrition Basics",
        "Balanced nutrition supports energy, growth and daily activity."
    ),
    (
        "Mindset",
        "Patience and consistency matter more than chasing quick results."
    ),
]


# ============================================================
# DATABASE
# ============================================================

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def has_column(db, table_name, column_name):

    columns = db.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return any(
        row["name"] == column_name
        for row in columns
    )


def init_database():

    db = get_db()

    # --------------------------------------------------------
    # POSTS
    # --------------------------------------------------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    if not has_column(db, "posts", "category"):
        db.execute("""
            ALTER TABLE posts
            ADD COLUMN category TEXT DEFAULT 'Fitness Knowledge'
        """)

    if not has_column(db, "posts", "featured"):
        db.execute("""
            ALTER TABLE posts
            ADD COLUMN featured INTEGER DEFAULT 0
        """)

    if not has_column(db, "posts", "views"):
        db.execute("""
            ALTER TABLE posts
            ADD COLUMN views INTEGER DEFAULT 0
        """)

    # --------------------------------------------------------
    # SITE SETTINGS
    # --------------------------------------------------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS site_settings (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            website_title TEXT DEFAULT 'Abhinandan Fitness',
            website_description TEXT DEFAULT
                'Fitness, knowledge, motivation and consistency.',
            website_views INTEGER DEFAULT 0
        )
    """)

    # --------------------------------------------------------
    # CREATOR
    # --------------------------------------------------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS creator (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            name TEXT,
            role TEXT,
            bio TEXT,
            instagram TEXT,
            website_title TEXT
        )
    """)

    # --------------------------------------------------------
    # MEDIA
    # --------------------------------------------------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT,
            uploaded_at TEXT,
            is_main INTEGER DEFAULT 0
        )
    """)

    # --------------------------------------------------------
    # DEFAULT SETTINGS
    # --------------------------------------------------------

    settings = db.execute(
        "SELECT id FROM site_settings WHERE id=1"
    ).fetchone()

    if not settings:

        db.execute("""
            INSERT INTO site_settings
            (
                id,
                website_title,
                website_description,
                website_views
            )
            VALUES
            (
                1,
                'Abhinandan Fitness',
                'Fitness, knowledge, motivation and consistency.',
                0
            )
        """)

    # --------------------------------------------------------
    # DEFAULT CREATOR
    # --------------------------------------------------------

    creator = db.execute(
        "SELECT id FROM creator WHERE id=1"
    ).fetchone()

    if not creator:

        db.execute("""
            INSERT INTO creator
            (
                id,
                name,
                role,
                bio,
                instagram,
                website_title
            )
            VALUES
            (
                1,
                'Ritesh Kumar Prajapati',
                'Website Developer',
                'Abhinandan Fitness is a digital fitness platform created and developed by Ritesh Kumar Prajapati.',
                'https://www.instagram.com/abhi.lifts.69/',
                'Abhinandan Fitness'
            )
        """)

    # --------------------------------------------------------
    # MAIN IMAGE
    # --------------------------------------------------------

    image_path = os.path.join(
        STATIC_DIR,
        MAIN_IMAGE
    )

    existing_main = db.execute(
        "SELECT id FROM media WHERE is_main=1 LIMIT 1"
    ).fetchone()

    if os.path.exists(image_path) and not existing_main:

        db.execute("""
            INSERT INTO media
            (
                filename,
                original_name,
                uploaded_at,
                is_main
            )
            VALUES (?, ?, ?, 1)
        """, (
            MAIN_IMAGE,
            MAIN_IMAGE,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        ))

    db.commit()
    db.close()


# ============================================================
# AUTH
# ============================================================

def logged_in():

    return session.get(
        "creator_logged_in"
    ) is True


def login_required():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    return None


def clean(value, default=""):

    value = value or default

    return value.strip()


# ============================================================
# GLOBAL STYLE
# ============================================================

STYLE = r"""
<style>

:root{
    --bg:#090a0c;
    --panel:#111317;
    --panel2:#15171c;
    --border:#292c33;
    --text:#f4f5f7;
    --muted:#9da3ad;
    --red:#ff3040;
    --red2:#ff5965;
    --green:#36d98b;
}

*{
    box-sizing:border-box;
}

html{
    scroll-behavior:smooth;
}

body{
    margin:0;
    background:var(--bg);
    color:var(--text);
    font-family:Arial,Helvetica,sans-serif;
}

a{
    color:inherit;
    text-decoration:none !important;
}

button,
input,
textarea,
select{
    font:inherit;
}

.container{
    width:min(1160px,92%);
    margin:auto;
}


/* ============================================================
   NAVBAR
   ============================================================ */

.nav{
    position:sticky;
    top:0;
    z-index:100;
    background:rgba(9,10,12,.97);
    border-bottom:1px solid var(--border);
}

.nav-inner{
    min-height:72px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:20px;
}

.brand{
    font-weight:900;
    letter-spacing:.5px;
    white-space:nowrap;
}

.brand span{
    color:var(--red);
}

.nav-links{
    display:flex;
    align-items:center;
    gap:20px;
}

.nav-links a{
    color:#d9dce1;
    font-weight:700;
    font-size:14px;
    white-space:nowrap;
}

.nav-links a:hover{
    color:var(--red2);
}

.instagram-btn{
    color:var(--red) !important;
}


/* ============================================================
   HERO
   ============================================================ */

.hero{
    min-height:650px;
    display:grid;
    grid-template-columns:1.1fr .9fr;
    align-items:center;
    gap:55px;
}

.kicker{
    color:var(--red);
    font-weight:900;
    letter-spacing:2px;
}

.hero h1{
    font-size:clamp(45px,7vw,82px);
    line-height:.95;
    margin:15px 0 22px;
}

.hero p{
    color:var(--muted);
    font-size:18px;
    line-height:1.7;
}

.btns{
    display:flex;
    flex-wrap:wrap;
    gap:12px;
    margin-top:28px;
}

.btn{
    display:inline-block;
    padding:12px 17px;
    border-radius:10px;
    border:1px solid var(--border);
    background:var(--panel);
    color:white;
    font-weight:900;
    cursor:pointer;
}

.btn:hover{
    border-color:var(--red);
}

.btn.primary{
    background:var(--red);
    border-color:var(--red);
    color:white;
}

.hero-card{
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:24px;
    overflow:hidden;
}

.heroImg{
    width:100%;
    display:block;
    max-height:600px;
    object-fit:cover;
}


/* ============================================================
   SECTIONS
   ============================================================ */

section{
    padding:80px 0;
}

.section-title{
    font-size:38px;
    margin:0 0 12px;
}

.section-sub{
    color:var(--muted);
    line-height:1.7;
    max-width:760px;
}

.cards,
.exercise-grid,
.blog-grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:18px;
    margin-top:28px;
}

.card,
.article-card{
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:16px;
    padding:24px;
}

.card h3{
    margin-top:0;
}

.card p,
.article-card p{
    color:var(--muted);
    line-height:1.7;
}

.exercise{
    padding:22px;
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:16px;
    font-weight:800;
    transition:.2s;
}

.exercise:hover{
    transform:translateY(-3px);
    border-color:var(--red);
}

.exercise-top{
    display:flex;
    justify-content:space-between;
    gap:10px;
    align-items:center;
    margin-bottom:12px;
}

.exercise-name{
    font-size:18px;
}

.exercise-category{
    color:var(--red);
    font-size:11px;
    font-weight:900;
    text-transform:uppercase;
    letter-spacing:.8px;
}

.exercise-description{
    color:var(--muted);
    line-height:1.6;
    font-size:14px;
    min-height:68px;
}

.exercise-actions{
    margin-top:16px;
}

.filter-row{
    display:flex;
    gap:9px;
    flex-wrap:wrap;
    margin:22px 0 4px;
}

.filter-btn{
    padding:9px 13px;
    border:1px solid var(--border);
    border-radius:9px;
    background:#0d0f12;
    color:#dfe2e7;
    font-weight:800;
    cursor:pointer;
}

.filter-btn:hover,
.filter-btn.active{
    background:var(--red);
    border-color:var(--red);
    color:white;
}

.exercise-detail{
    max-width:820px;
    margin:50px auto;
}

.step-list{
    padding-left:22px;
    color:#c8cdd5;
    line-height:1.9;
}

.article-card .meta{
    color:var(--red);
    font-size:12px;
    font-weight:900;
    text-transform:uppercase;
}

.creator-box{
    background:linear-gradient(
        135deg,
        #14161b,
        #0e1013
    );
    border:1px solid var(--border);
    border-radius:20px;
    padding:32px;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer{
    padding:35px 0;
    border-top:1px solid var(--border);
    color:var(--muted);
}


/* ============================================================
   FORMS
   ============================================================ */

.form-card{
    max-width:700px;
    margin:45px auto;
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:18px;
    padding:28px;
}

label{
    display:block;
    margin:15px 0 8px;
    font-weight:800;
}

input,
textarea,
select{
    width:100%;
    background:#0b0d10;
    color:white;
    border:1px solid var(--border);
    border-radius:10px;
    padding:12px;
    outline:none;
}

input:focus,
textarea:focus,
select:focus{
    border-color:var(--red);
}

textarea{
    min-height:180px;
    resize:vertical;
}

.alert{
    padding:12px 14px;
    border-radius:10px;
    background:#301117;
    border:1px solid #6f202b;
    color:#ff9da5;
    margin:15px 0;
}


/* ============================================================
   RITESH HQ
   ============================================================ */

.hq-wrap{
    min-height:100vh;
    background:#090a0c;
}

.hq-top{
    padding:22px 0;
    border-bottom:1px solid var(--border);
}

.hq-top-inner{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:18px;
}

.hq-layout{
    display:grid;
    grid-template-columns:245px 1fr;
    gap:22px;
    padding:25px 0 60px;
}

.hq-side{
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:18px;
    padding:14px;
    height:max-content;
    position:sticky;
    top:95px;
}

.hq-side-title{
    padding:13px 12px 18px;
    color:var(--muted);
    font-size:12px;
    font-weight:900;
    letter-spacing:1.2px;
    line-height:1.5;
}


/* ============================================================
   HQ BOX MENU
   ============================================================ */

.hq-menu{
    display:grid;
    gap:9px;
}

.hq-menu a{
    display:block;
    padding:13px 14px;
    border:1px solid var(--border);
    border-radius:11px;
    background:#0d0f12;
    color:#e5e7eb;
    font-weight:800;
    transition:.18s;
}

.hq-menu a:hover{
    border-color:var(--red);
    color:white;
    background:#1b1013;
    transform:translateX(2px);
}

.hq-menu a.active{
    background:var(--red);
    border-color:var(--red);
    color:white;
}

.hq-menu a.external{
    border-color:#343840;
}


/* ============================================================
   HQ CONTENT
   ============================================================ */

.hq-main{
    min-width:0;
}

.hq-card{
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:18px;
    padding:24px;
    margin-bottom:18px;
}

.stats{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:14px;
}

.stat{
    background:#0d0f12;
    border:1px solid var(--border);
    border-radius:14px;
    padding:20px;
}

.stat .num{
    font-size:30px;
    font-weight:900;
    margin-top:8px;
}

.stat .label{
    color:var(--muted);
    font-size:13px;
    margin:0;
}


/* ============================================================
   TABLE
   ============================================================ */

.table-wrap{
    overflow-x:auto;
}

table{
    width:100%;
    border-collapse:collapse;
    min-width:700px;
}

th,
td{
    text-align:left;
    padding:13px;
    border-bottom:1px solid var(--border);
}

th{
    color:#cdd1d7;
    font-size:13px;
}

td{
    color:#aeb4be;
}

.actions{
    display:flex;
    flex-wrap:wrap;
    gap:8px;
}

.small-btn{
    display:inline-block;
    padding:8px 10px;
    border:1px solid var(--border);
    background:#0d0f12;
    border-radius:8px;
    font-size:12px;
    font-weight:800;
    color:white;
    cursor:pointer;
}

.small-btn:hover{
    border-color:var(--red);
}

.danger:hover{
    border-color:#ff4b59;
    color:#ff6d79;
}


/* ============================================================
   MEDIA
   ============================================================ */

.media-grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:16px;
}

.media-item{
    background:#0d0f12;
    border:1px solid var(--border);
    border-radius:14px;
    overflow:hidden;
}

.media-item img{
    width:100%;
    height:190px;
    object-fit:cover;
    display:block;
}

.media-body{
    padding:14px;
}

.badge{
    display:inline-block;
    padding:5px 8px;
    border-radius:7px;
    background:#241015;
    color:#ff7c87;
    font-size:11px;
    font-weight:900;
}


/* ============================================================
   SEARCH
   ============================================================ */

.search-row{
    display:flex;
    gap:10px;
}

.search-row input{
    flex:1;
}

.empty{
    padding:30px;
    text-align:center;
    color:var(--muted);
    border:1px dashed var(--border);
    border-radius:12px;
}


/* ============================================================
   MOBILE
   ============================================================ */


/* Workout Library Search */
.workout-search{
    margin:18px 0 6px;
    max-width:720px;
}
.workout-search input{
    width:100%;
    background:#0b0d10;
    color:white;
    border:1px solid var(--border);
    border-radius:11px;
    padding:13px 15px;
    outline:none;
}
.workout-search input:focus{
    border-color:var(--red);
}
.exercise-empty{
    display:none;
    margin-top:18px;
}

@media(max-width:850px){

    .nav-inner{
        min-height:auto;
        padding:14px 0;
        align-items:flex-start;
        flex-direction:column;
        gap:12px;
    }

    .nav-links{
        display:flex;
        width:100%;
        gap:9px;
        overflow-x:auto;
        padding-bottom:5px;
        -webkit-overflow-scrolling:touch;
        scrollbar-width:thin;
    }

    .nav-links a{
        white-space:nowrap;
        font-size:13px;
        padding:8px 10px;
        background:#111317;
        border:1px solid #25262a;
        border-radius:8px;
    }

    .hero{
        grid-template-columns:1fr;
        padding:55px 0;
    }

    .cards,
    .blog-grid,
    .exercise-grid{
        grid-template-columns:1fr;
    }

    .hq-layout{
        grid-template-columns:1fr;
    }

    .hq-side{
        position:static;
    }

    .hq-menu{
        grid-template-columns:repeat(2,1fr);
    }

    .stats{
        grid-template-columns:repeat(2,1fr);
    }

    .media-grid{
        grid-template-columns:1fr 1fr;
    }
}


@media(max-width:520px){

    section{
        padding:55px 0;
    }

    .hero h1{
        font-size:46px;
    }

    .hq-menu{
        grid-template-columns:1fr;
    }

    .stats{
        grid-template-columns:1fr 1fr;
    }

    .media-grid{
        grid-template-columns:1fr;
    }

    .hq-top-inner{
        align-items:flex-start;
        flex-direction:column;
    }
}

</style>
"""


# ============================================================
# HOME PAGE
# ============================================================

HOME_HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
{{ settings["website_title"] }}
</title>
<meta name="google-site-verification" content="7CFx_7zMu-jWZEj4ESqGEBugXHCKxxEtxN3NJAV4itM" />

<meta name="description" content="Abhinandan Fitness — fitness knowledge, workout exercises, motivation and fitness articles by Abhinandan Kumar.">

<meta name="keywords" content="Abhinandan Fitness, fitness, workout, exercises, gym, fitness motivation, fitness articles">

<meta name="theme-color" content="#070707">

{{ style|safe }}

</head>


<body>


<nav class="nav">

<div class="container nav-inner">

<a
    class="brand"
    href="/"
>
    ABHINANDAN <span>FITNESS</span>
      [ GYM ]
</a>


<div class="nav-links">

<a href="#about">
    About
</a>

<a href="#knowledge">
    Knowledge
</a>

<a href="#workout">
    Workout
</a>

<a href="#blog">
    Blog
</a>

<a href="#creator">
    Creator
</a>

<a
    class="instagram-btn"
    href="{{ creator['instagram'] }}"
    target="_blank"
    rel="noopener noreferrer"
>
    📸 Instagram
</a>

<a href="/login">
    Ritesh HQ
</a>

</div>

</div>

</nav>



<main>


<section class="container hero">


<div>

<div class="kicker">
FITNESS • KNOWLEDGE • MOTIVATION
</div>


<h1>

BUILD YOUR

<br>

<span style="color:var(--red)">
STRONGER SELF
</span>

</h1>


<p>

{{ settings["website_description"] }}

</p>


<div class="btns">

<a
    class="btn primary"
    href="#workout"
>
    Explore Workout
</a>


<a
    class="btn"
    href="#blog"
>
    Read Articles
</a>

</div>

</div>



<div class="hero-card">

<img
    class="heroImg"
    src="{{ url_for('static', filename='abhinandan.jpg') }}"
    alt="Abhinandan Fitness"
>

</div>


</section>



<section id="about">

<div class="container">

<h2 class="section-title">
About Abhinandan
</h2>


<p class="section-sub">

Abhinandan Kumar is a fitness content creator
sharing gym motivation, fitness knowledge
and his journey through training and consistency.

</p>

</div>

</section>



<section id="knowledge">

<div class="container">

<h2 class="section-title">
Fitness Knowledge
</h2>


<p class="section-sub">

Simple fitness principles for learning
and building healthy habits.

</p>



<div class="cards">

{% for item in knowledge %}

<div class="card">

<h3>
{{ item[0] }}
</h3>

<p>
{{ item[1] }}
</p>

</div>

{% endfor %}

</div>

</div>

</section>



<section id="workout">

<div class="container">

<h2 class="section-title">
Workout Library
</h2>

<p class="section-sub">
Explore exercises by training area. Open any exercise for basic guidance and safety notes.
</p>

<div class="filter-row">
{% for category in exercise_categories %}
<button class="filter-btn {{ 'active' if category == 'All' else '' }}" type="button" data-filter="{{ category }}">{{ category }}</button>
{% endfor %}
</div>

<div class="workout-search">
    <input
        id="exerciseSearch"
        type="search"
        placeholder="Search exercises... e.g. Bench Press, Squat, Core"
        autocomplete="off"
        aria-label="Search exercises"
    >
</div>

<div class="exercise-grid" id="exerciseGrid">
{% for exercise in exercise_data %}
<div class="exercise" data-category="{{ exercise['category'] }}">
    <div class="exercise-top">
        <div class="exercise-name">{{ exercise['name'] }}</div>
        <div class="exercise-category">{{ exercise['category'] }}</div>
    </div>
    <div class="exercise-description">{{ exercise['description'] }}</div>
    <div class="exercise-actions">
        <a class="btn" href="{{ url_for('exercise_detail', exercise_name=exercise['name']) }}">View Exercise →</a>
    </div>
</div>
{% endfor %}
</div>

<div class="empty exercise-empty" id="exerciseEmpty">
    No matching exercises found.
</div>

</div>

</section>



<section id="creator">

<div class="container">

<div class="creator-box">

<h2 class="section-title">
Website
</h2>


<h3>
Abhinandan Fitness
</h3>


<p class="section-sub">

Abhinandan Fitness is a digital fitness platform
for fitness knowledge, articles, motivation
and useful workout information.

</p>


<a
    class="btn primary"
    href="/login"
>
    Open Ritesh HQ →
</a>

</div>

</div>

</section>



<section id="blog">

<div class="container">

<h2 class="section-title">
Fitness Articles
</h2>


<p class="section-sub">

Read the latest articles from Abhinandan Fitness.

</p>



<form
    class="search-row"
    method="get"
    action="/"
>

<input
    name="q"
    value="{{ q }}"
    placeholder="Search articles..."
>


<button
    class="btn primary"
    type="submit"
>
    Search
</button>

</form>



<div class="blog-grid">


{% for post in posts %}

<div class="article-card">


<div class="meta">

{{ post["category"] }}

•

{{ post["views"] }}

views

</div>


<h3>

{{ post["title"] }}

</h3>


<p>

{{ post["content"][:220] }}

{% if post["content"]|length > 220 %}

...

{% endif %}

</p>


<a
    class="btn"
    href="/article/{{ post['id'] }}"
>
    Read Article →
</a>


</div>


{% else %}

<div class="empty">

No articles published yet.

</div>

{% endfor %}


</div>

</div>

</section>


</main>

<section id="software-creator">

    <div class="container">

        <div class="creator-box">

            <div class="kicker">
                CREATOR OF THIS SOFTWARE
            </div>

            <h2 class="section-title">
                Ritesh Kumar Prajapati
            </h2>

            <h3>
                Software
            </h3>

            <p class="section-sub">
                Created by Ritesh Kumar Prajapati,
                a young aspiring AI developer passionate
                about building smart and useful software.
            </p>

            <p class="section-sub">
                “Created by Ritesh Kumar Prajapati,
                a young aspiring AI developer passionate
                about building smart and useful software.”
            </p>

        </div>

    </div>

</section>


<section id="connect">

    <div class="container">

        <div class="creator-box">

            <h2 class="section-title">
                Connect With Abhinandan
            </h2>

            <p class="section-sub">
                Follow the latest fitness content and updates.
            </p>

            <div class="btns">

                <a
                    class="btn primary"
                    href="{{ creator['instagram'] }}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    📸 Follow on Instagram
                </a>

            </div>

        </div>

    </div>

</section>

<footer class="footer">

<div class="container">

Abhinandan Fitness • Website Management through Ritesh HQ

</div>

</footer>

<footer class="footer">

    <div class="container">

        © 2026 Abhinandan Fitness. All Rights Reserved.

    </div>

</footer>
<script>
(function(){
    var activeFilter = "All";
    var searchInput = document.getElementById("exerciseSearch");
    var cards = document.querySelectorAll("#exerciseGrid .exercise");
    var emptyMessage = document.getElementById("exerciseEmpty");

    function applyExerciseFilters(){
        var query = (searchInput.value || "").trim().toLowerCase();
        var visibleCount = 0;

        cards.forEach(function(card){
            var category = (card.dataset.category || "").toLowerCase();
            var cardText = (card.textContent || "").toLowerCase();

            var categoryMatch =
                activeFilter === "All" ||
                category === activeFilter.toLowerCase();

            var searchMatch =
                query === "" ||
                cardText.indexOf(query) !== -1;

            var show = categoryMatch && searchMatch;
            card.style.display = show ? "block" : "none";

            if(show){ visibleCount++; }
        });

        if(emptyMessage){
            emptyMessage.style.display = visibleCount === 0 ? "block" : "none";
        }
    }

    document.querySelectorAll(".filter-btn").forEach(function(button){
        button.addEventListener("click", function(){
            document.querySelectorAll(".filter-btn").forEach(function(b){
                b.classList.remove("active");
            });
            button.classList.add("active");
            activeFilter = button.dataset.filter || "All";
            applyExerciseFilters();
        });
    });

    if(searchInput){
        searchInput.addEventListener("input", applyExerciseFilters);
    }

    applyExerciseFilters();
})();
</script>

</body>

</html>
"""


# ============================================================
# LOGIN PAGE
# ============================================================

LOGIN_HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Ritesh HQ
</title>

{{ style|safe }}

</head>


<body>


<div class="container">


<div class="form-card">


<div class="kicker">
ABHINANDAN FITNESS
</div>


<h1>
Ritesh HQ
</h1>


<p class="section-sub">

Website management access.

</p>


{% if error %}

<div class="alert">

{{ error }}

</div>

{% endif %}


<form method="post">


<label>
Creator ID
</label>


<input
    type="text"
    name="username"
    autocomplete="username"
    required
>


<label>
Access Key
</label>


<input
    type="password"
    name="password"
    autocomplete="current-password"
    required
>


<button
    class="btn primary"
    style="margin-top:18px"
    type="submit"
>
    Enter HQ
</button>


</form>


<div style="margin-top:20px">

<a
    class="btn"
    href="/"
>
    ← Website
</a>

</div>


</div>


</div>


</body>

</html>
"""


# ============================================================
# HQ PAGE
# ============================================================

HQ_HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Ritesh HQ
</title>

{{ style|safe }}

</head>


<body>


<div class="hq-wrap">


<div class="hq-top">


<div class="container hq-top-inner">


<div>

<div class="kicker">
ABHINANDAN FITNESS
</div>


<h2 style="margin:5px 0">
Ritesh HQ
</h2>


<div style="color:var(--muted)">
Abhinandan Fitness / Website Management
</div>

</div>



<div class="actions">


<a
    class="small-btn"
    href="/"
    target="_blank"
>
    🌐 View Website
</a>


<a
    class="small-btn"
    href="/logout"
>
    🔐 Logout
</a>


</div>


</div>

</div>



<div class="container hq-layout">


<aside class="hq-side">


<div class="hq-side-title">

ABHINANDAN FITNESS

<br>

WEBSITE MANAGEMENT

</div>



<nav class="hq-menu">


<a
    class="{{ 'active' if active=='overview' else '' }}"
    href="/admin"
>
    📊 Overview
</a>


<a
    class="{{ 'active' if active=='articles' else '' }}"
    href="/admin#articles"
>
    ✍️ Articles
</a>


<a
    class="{{ 'active' if active=='featured' else '' }}"
    href="/admin#featured"
>
    ⭐ Featured
</a>


<a
    class="{{ 'active' if active=='profile' else '' }}"
    href="/profile"
>
    👤 Profile
</a>


<a
    class="{{ 'active' if active=='social' else '' }}"
    href="/social"
>
    🔗 Social Links
</a>


<a
    class="{{ 'active' if active=='media' else '' }}"
    href="/media"
>
    🖼️ Media
</a>


<a
    class="{{ 'active' if active=='settings' else '' }}"
    href="/settings"
>
    ⚙️ Settings
</a>


<a
    class="external"
    href="/"
    target="_blank"
>
    🌐 View Website
</a>


<a
    class="external"
    href="/logout"
>
    🔐 Logout
</a>


</nav>


</aside>



<main class="hq-main">


<div class="hq-card">

<h1 style="margin-top:0">
Overview
</h1>


<p class="section-sub">

Manage the Abhinandan Fitness website
from one place.

</p>

</div>



<div class="stats">


<div class="stat">

<div class="label">
Website Views
</div>

<div class="num">
{{ stats.website_views }}
</div>

</div>


<div class="stat">

<div class="label">
Article Views
</div>

<div class="num">
{{ stats.article_views }}
</div>

</div>


<div class="stat">

<div class="label">
Published Articles
</div>

<div class="num">
{{ stats.published }}
</div>

</div>


<div class="stat">

<div class="label">
Featured Articles
</div>

<div class="num">
{{ stats.featured }}
</div>

</div>


</div>



<div
    class="hq-card"
    id="articles"
    style="margin-top:18px"
>


<div
    style="
    display:flex;
    justify-content:space-between;
    gap:12px;
    align-items:center;
    flex-wrap:wrap;
    "
>


<div>

<h2 style="margin:0">
Articles
</h2>


<p class="section-sub">

Create, edit, feature or remove
website articles.

</p>

</div>


<a
    class="btn primary"
    href="/edit/0"
>
    + New Article
</a>


</div>



<form
    method="get"
    action="/admin"
    class="search-row"
    style="margin-top:20px"
>


<input
    name="q"
    value="{{ q }}"
    placeholder="Search articles..."
>


<button
    class="btn"
    type="submit"
>
    Search
</button>


</form>



<div
    class="table-wrap"
    style="margin-top:20px"
>


<table>


<thead>

<tr>

<th>
Title
</th>

<th>
Category
</th>

<th>
Views
</th>

<th>
Featured
</th>

<th>
Actions
</th>

</tr>

</thead>



<tbody>


{% for post in posts %}

<tr>


<td>
{{ post["title"] }}
</td>


<td>
{{ post["category"] }}
</td>


<td>
{{ post["views"] }}
</td>


<td>

{{ "Yes" if post["featured"] else "No" }}

</td>


<td>


<div class="actions">


<a
    class="small-btn"
    href="/article/{{ post['id'] }}"
    target="_blank"
>
    View
</a>


<a
    class="small-btn"
    href="/edit/{{ post['id'] }}"
>
    Edit
</a>


{% if post["featured"] %}


<a
    class="small-btn"
    href="/unfeature/{{ post['id'] }}"
>
    Unfeature
</a>


{% else %}


<a
    class="small-btn"
    href="/feature/{{ post['id'] }}"
>
    Feature
</a>


{% endif %}



<form
    method="post"
    action="/delete/{{ post['id'] }}"
    onsubmit="return confirm('Delete this article?')"
>


<button
    class="small-btn danger"
    type="submit"
>
    Delete
</button>


</form>


</div>


</td>


</tr>


{% else %}


<tr>

<td colspan="5">

No articles found.

</td>

</tr>


{% endfor %}


</tbody>

</table>

</div>

</div>



<div
    class="hq-card"
    id="featured"
>


<h2>
Most Read Articles
</h2>


<div class="table-wrap">


<table>


<thead>

<tr>

<th>
Title
</th>

<th>
Views
</th>

</tr>

</thead>


<tbody>


{% for post in most_read %}


<tr>

<td>
{{ post["title"] }}
</td>

<td>
{{ post["views"] }}
</td>

</tr>


{% else %}


<tr>

<td colspan="2">

No article data yet.

</td>

</tr>


{% endfor %}


</tbody>

</table>

</div>

</div>


</main>


</div>


</div>


</body>

</html>
"""


# ============================================================
# ARTICLE PAGE
# ============================================================

ARTICLE_HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
{{ post["title"] }} • Abhinandan Fitness
</title>

{{ style|safe }}

</head>


<body>


<nav class="nav">

<div class="container nav-inner">


<a
    class="brand"
    href="/"
>
    ABHINANDAN <span>FITNESS</span>
</a>


<div class="nav-links">


<a href="/">
    Home
</a>


<a href="/#blog">
    Blog
</a>


<a href="/#workout">
    Workout
</a>


<a
    class="instagram-btn"
    href="{{ creator['instagram'] }}"
    target="_blank"
>
    📸 Instagram
</a>


<a href="/login">
    Ritesh HQ
</a>


</div>


</div>

</nav>



<main class="container">


<section>


<div class="article-card">


<div class="meta">

{{ post["category"] }}

•

{{ post["views"] }}

views

</div>


<h1
    style="
    font-size:clamp(35px,6vw,60px)
    "
>

{{ post["title"] }}

</h1>


<p
    style="
    white-space:pre-wrap;
    font-size:18px;
    line-height:1.9;
    color:#c2c7cf
    "
>

{{ post["content"] }}

</p>


<a
    class="btn"
    href="/#blog"
>
    ← Back to Articles
</a>


</div>


</section>


</main>


</body>

</html>
"""


# ============================================================
# EDIT ARTICLE
# ============================================================

EDIT_HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
{{ "New Article" if is_new else "Edit Article" }}
</title>

{{ style|safe }}

</head>


<body>


<div class="container">


<div class="form-card">


<div class="kicker">
ABHINANDAN FITNESS
</div>


<h1>

{{ "New Article" if is_new else "Edit Article" }}

</h1>



<form method="post">


<label>
Article Title
</label>


<input
    name="title"
    value="{{ post['title'] if post else '' }}"
    required
>



<label>
Category
</label>


<select name="category">


{% for category in categories %}


<option
    value="{{ category }}"
    {% if post and post["category"]==category %}
    selected
    {% endif %}
>

{{ category }}

</option>


{% endfor %}


</select>



<label>
Content
</label>


<textarea
    name="content"
    required
>{{ post["content"] if post else "" }}</textarea>



<label
    style="
    display:flex;
    gap:8px;
    align-items:center
    "
>


<input
    style="width:auto"
    type="checkbox"
    name="featured"
    {% if post and post["featured"] %}
    checked
    {% endif %}
>


Featured article


</label>



<button
    class="btn primary"
    style="margin-top:18px"
    type="submit"
>


{{ "Publish Article" if is_new else "Save Changes" }}


</button>


<a
    class="btn"
    href="/admin"
>
    Cancel
</a>


</form>


</div>


</div>


</body>

</html>
"""


# ============================================================
# PROFILE
# ============================================================

PROFILE_HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Profile • Ritesh HQ
</title>

{{ style|safe }}

</head>


<body>


<div class="container">


<div class="form-card">


<div class="kicker">
ABHINANDAN FITNESS
</div>


<h1>
Profile
</h1>


<p class="section-sub">
Website information.
</p>



<form method="post">


<label>
Name
</label>


<input
    name="name"
    value="{{ creator['name'] }}"
    required
>



<label>
Role
</label>


<input
    name="role"
    value="{{ creator['role'] }}"
    required
>



<label>
Bio
</label>


<textarea
    name="bio"
    required
>{{ creator['bio'] }}</textarea>



<button
    class="btn primary"
    type="submit"
>
    Save Profile
</button>


<a
    class="btn"
    href="/admin"
>
    Back to HQ
</a>


</form>


</div>


</div>


</body>

</html>
"""


# ============================================================
# SOCIAL
# ============================================================

SOCIAL_HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Social Links • Ritesh HQ
</title>

{{ style|safe }}

</head>


<body>


<div class="container">


<div class="form-card">


<div class="kicker">
ABHINANDAN FITNESS
</div>


<h1>
Social Links
</h1>


<p class="section-sub">

Manage the Instagram link
shown on the website.

</p>



<form method="post">


<label>
Instagram URL
</label>


<input
    name="instagram"
    value="{{ creator['instagram'] }}"
    required
>


<button
    class="btn primary"
    type="submit"
>
    Save Social Link
</button>


<a
    class="btn"
    href="/admin"
>
    Back to HQ
</a>


</form>


</div>


</div>


</body>

</html>
"""


# ============================================================
# SETTINGS
# ============================================================

SETTINGS_HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Settings • Ritesh HQ
</title>

{{ style|safe }}

</head>


<body>


<div class="container">


<div class="form-card">


<div class="kicker">
ABHINANDAN FITNESS
</div>


<h1>
Settings
</h1>



<form method="post">


<label>
Website Title
</label>


<input
    name="website_title"
    value="{{ settings['website_title'] }}"
    required
>



<label>
Website Description
</label>


<textarea
    name="website_description"
    required
>{{ settings['website_description'] }}</textarea>



<button
    class="btn primary"
    type="submit"
>
    Save Settings
</button>


<a
    class="btn"
    href="/admin"
>
    Back to HQ
</a>


</form>


</div>


</div>


</body>

</html>
"""


# ============================================================
# MEDIA
# ============================================================

MEDIA_HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Media • Ritesh HQ
</title>

{{ style|safe }}

</head>


<body>


<div class="container">


<section>


<div class="hq-card">


<div class="kicker">
ABHINANDAN FITNESS
</div>


<h1>
Media
</h1>


<p class="section-sub">

Manage website images.

</p>



<form
    method="post"
    action="/media/upload"
    enctype="multipart/form-data"
>


<input
    type="file"
    name="image"
    accept=".jpg,.jpeg,.png,.webp"
    required
>


<button
    class="btn primary"
    style="margin-top:12px"
    type="submit"
>
    Upload Image
</button>


</form>


</div>



<div class="media-grid">


{% for item in media %}


<div class="media-item">


{% if item["filename"] == "abhinandan.jpg" %}


<img
    src="{{ url_for('static', filename='abhinandan.jpg') }}"
    alt="{{ item['original_name'] }}"
>


{% else %}


<img
    src="/media/public/{{ item['filename'] }}"
    alt="{{ item['original_name'] }}"
>


{% endif %}



<div class="media-body">


<strong>
{{ item["original_name"] }}
</strong>


<br>


{% if item["is_main"] %}

<span class="badge">
MAIN IMAGE
</span>

{% endif %}



<div
    class="actions"
    style="margin-top:12px"
>


{% if not item["is_main"] %}


<a
    class="small-btn"
    href="/media/set-main/{{ item['id'] }}"
>
    Set Main
</a>


{% endif %}



{% if item["filename"] != "abhinandan.jpg" %}


<form
    method="post"
    action="/media/delete/{{ item['id'] }}"
    onsubmit="return confirm('Delete this image?')"
>


<button
    class="small-btn danger"
    type="submit"
>
    Delete
</button>


</form>


{% endif %}


</div>


</div>


</div>


{% else %}


<div class="empty">
No media uploaded.
</div>


{% endfor %}


</div>



<div style="margin-top:22px">


<a
    class="btn"
    href="/admin"
>
    ← Back to HQ
</a>


</div>


</section>


</div>


</body>

</html>
"""


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    db = get_db()

    db.execute("""
        UPDATE site_settings
        SET website_views = website_views + 1
        WHERE id=1
    """)

    db.commit()


    settings = db.execute(
        "SELECT * FROM site_settings WHERE id=1"
    ).fetchone()


    creator = db.execute(
        "SELECT * FROM creator WHERE id=1"
    ).fetchone()


    q = clean(
        request.args.get("q")
    )


    if q:

        posts = db.execute("""
            SELECT *
            FROM posts

            WHERE
                title LIKE ?
                OR content LIKE ?
                OR category LIKE ?

            ORDER BY
                featured DESC,
                id DESC

        """, (
            f"%{q}%",
            f"%{q}%",
            f"%{q}%"
        )).fetchall()

    else:

        posts = db.execute("""
            SELECT *
            FROM posts

            ORDER BY
                featured DESC,
                id DESC
        """).fetchall()


    db.close()


    return render_template_string(
        HOME_HTML,
        style=STYLE,
        settings=settings,
        creator=creator,
        posts=posts,
        q=q,
        knowledge=KNOWLEDGE,
        exercises=EXERCISES,
        exercise_data=EXERCISE_DATA,
        exercise_categories=EXERCISE_CATEGORIES,
    )


# ============================================================
# EXERCISE DETAIL
# ============================================================

EXERCISE_DETAIL_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ exercise["name"] }} • Abhinandan Fitness</title>
{{ style|safe }}
</head>
<body>
<nav class="nav">
<div class="container nav-inner">
<a class="brand" href="/">ABHINANDAN <span>FITNESS</span></a>
<div class="nav-links">
<a href="/">Home</a>
<a href="/#workout">Workout</a>
<a href="/#blog">Blog</a>
<a class="instagram-btn" href="{{ creator['instagram'] }}" target="_blank" rel="noopener noreferrer">📸 Instagram</a>
<a href="/login">Ritesh HQ</a>
</div>
</div>
</nav>

<main class="container">
<section class="exercise-detail">
<div class="creator-box">
<div class="kicker">{{ exercise["category"] }} • {{ exercise["level"] }}</div>
<h1 class="section-title">{{ exercise["name"] }}</h1>
<p class="section-sub">{{ exercise["description"] }}</p>

<h2>How to Perform</h2>
<ol class="step-list">
{% for step in exercise["steps"] %}<li>{{ step }}</li>{% endfor %}
</ol>

<h2>Safety Note</h2>
<p class="section-sub">{{ exercise["safety"] }}</p>

<div class="btns">
<a class="btn primary" href="/#workout">← Back to Workout Library</a>
</div>
</div>
</section>
</main>
</body>
</html>
"""

@app.route("/exercise/<path:exercise_name>")
def exercise_detail(exercise_name):
    exercise = next((item for item in EXERCISE_DATA if item["name"] == exercise_name), None)
    if not exercise:
        abort(404)
    db = get_db()
    creator = db.execute("SELECT * FROM creator WHERE id=1").fetchone()
    db.close()
    return render_template_string(
        EXERCISE_DETAIL_HTML,
        style=STYLE,
        exercise=exercise,
        creator=creator
    )


# ============================================================
# ARTICLE
# ============================================================

@app.route("/article/<int:post_id>")
def article(post_id):

    db = get_db()


    post = db.execute(
        "SELECT * FROM posts WHERE id=?",
        (post_id,)
    ).fetchone()


    if not post:

        db.close()

        abort(404)


    db.execute("""
        UPDATE posts
        SET views = COALESCE(views,0) + 1
        WHERE id=?
    """, (post_id,))


    db.commit()


    creator = db.execute(
        "SELECT * FROM creator WHERE id=1"
    ).fetchone()


    db.close()


    return render_template_string(
        ARTICLE_HTML,
        style=STYLE,
        post=post,
        creator=creator
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = clean(
            request.form.get("username")
        )

        password = request.form.get(
            "password",
            ""
        )


        if (
            username == USERNAME
            and password == PASSWORD
        ):

            session.clear()

            session["creator_logged_in"] = True

            return redirect(
                url_for("admin")
            )


        return render_template_string(
            LOGIN_HTML,
            style=STYLE,
            error="Incorrect Creator ID or Access Key."
        )


    return render_template_string(
        LOGIN_HTML,
        style=STYLE,
        error=None
    )


# ============================================================
# ADMIN
# ============================================================

@app.route("/admin")
def admin():

    check = login_required()

    if check:
        return check


    db = get_db()


    q = clean(
        request.args.get("q")
    )


    if q:

        posts = db.execute("""
            SELECT *
            FROM posts

            WHERE
                title LIKE ?
                OR content LIKE ?
                OR category LIKE ?

            ORDER BY id DESC

        """, (
            f"%{q}%",
            f"%{q}%",
            f"%{q}%"
        )).fetchall()

    else:

        posts = db.execute("""
            SELECT *
            FROM posts
            ORDER BY id DESC
        """).fetchall()


    stats = db.execute("""
        SELECT

            (
                SELECT website_views
                FROM site_settings
                WHERE id=1
            ) AS website_views,

            COALESCE(
                (
                    SELECT SUM(views)
                    FROM posts
                ),
                0
            ) AS article_views,

            (
                SELECT COUNT(*)
                FROM posts
            ) AS published,

            (
                SELECT COUNT(*)
                FROM posts
                WHERE featured=1
            ) AS featured

    """).fetchone()


    most_read = db.execute("""
        SELECT *
        FROM posts

        ORDER BY
            views DESC,
            id DESC

        LIMIT 5
    """).fetchall()


    db.close()


    return render_template_string(
        HQ_HTML,
        style=STYLE,
        posts=posts,
        q=q,
        most_read=most_read,
        stats=stats,
        active="overview"
    )


# ============================================================
# EDIT / CREATE ARTICLE
# ============================================================

@app.route(
    "/edit/<int:post_id>",
    methods=["GET", "POST"]
)
def edit(post_id):

    check = login_required()

    if check:
        return check


    db = get_db()


    post = None


    if post_id != 0:

        post = db.execute(
            "SELECT * FROM posts WHERE id=?",
            (post_id,)
        ).fetchone()


        if not post:

            db.close()

            abort(404)


    if request.method == "POST":

        title = clean(
            request.form.get("title")
        )

        content = clean(
            request.form.get("content")
        )

        category = clean(
            request.form.get(
                "category"
            ),
            "Fitness Knowledge"
        )

        featured = (
            1
            if request.form.get("featured")
            else 0
        )


        if not title or not content:

            db.close()

            return render_template_string(
                EDIT_HTML,
                style=STYLE,
                post=post,
                categories=CATEGORIES,
                is_new=(post_id == 0)
            )


        if post_id == 0:

            if featured:

                db.execute(
                    "UPDATE posts SET featured=0"
                )


            db.execute("""
                INSERT INTO posts
                (
                    title,
                    content,
                    category,
                    featured,
                    views
                )

                VALUES
                (?, ?, ?, ?, 0)

            """, (
                title,
                content,
                category,
                featured
            ))


        else:

            if featured:

                db.execute("""
                    UPDATE posts
                    SET featured=0
                    WHERE id != ?
                """, (post_id,))


            db.execute("""
                UPDATE posts

                SET
                    title=?,
                    content=?,
                    category=?,
                    featured=?

                WHERE id=?

            """, (
                title,
                content,
                category,
                featured,
                post_id
            ))


        db.commit()

        db.close()


        return redirect(
            url_for("admin")
        )


    db.close()


    return render_template_string(
        EDIT_HTML,
        style=STYLE,
        post=post,
        categories=CATEGORIES,
        is_new=(post_id == 0)
    )


# ============================================================
# DELETE
# ============================================================

@app.post(
    "/delete/<int:post_id>"
)
def delete(post_id):

    check = login_required()

    if check:
        return check


    db = get_db()


    db.execute(
        "DELETE FROM posts WHERE id=?",
        (post_id,)
    )


    db.commit()

    db.close()


    return redirect(
        url_for("admin")
    )


# ============================================================
# FEATURE
# ============================================================

@app.route(
    "/feature/<int:post_id>"
)
def feature(post_id):

    check = login_required()

    if check:
        return check


    db = get_db()


    db.execute(
        "UPDATE posts SET featured=0"
    )


    db.execute(
        "UPDATE posts SET featured=1 WHERE id=?",
        (post_id,)
    )


    db.commit()

    db.close()


    return redirect(
        url_for("admin")
    )


# ============================================================
# UNFEATURE
# ============================================================

@app.route(
    "/unfeature/<int:post_id>"
)
def unfeature(post_id):

    check = login_required()

    if check:
        return check


    db = get_db()


    db.execute(
        "UPDATE posts SET featured=0 WHERE id=?",
        (post_id,)
    )


    db.commit()

    db.close()


    return redirect(
        url_for("admin")
    )


# ============================================================
# PROFILE
# ============================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    check = login_required()

    if check:
        return check


    db = get_db()


    if request.method == "POST":

        db.execute("""
            UPDATE creator

            SET
                name=?,
                role=?,
                bio=?

            WHERE id=1

        """, (
            clean(
                request.form.get("name")
            ),
            clean(
                request.form.get("role")
            ),
            clean(
                request.form.get("bio")
            )
        ))


        db.commit()


        return redirect(
            url_for("profile")
        )


    creator = db.execute(
        "SELECT * FROM creator WHERE id=1"
    ).fetchone()


    db.close()


    return render_template_string(
        PROFILE_HTML,
        style=STYLE,
        creator=creator
    )


# ============================================================
# SOCIAL
# ============================================================

@app.route(
    "/social",
    methods=["GET", "POST"]
)
def social():

    check = login_required()

    if check:
        return check


    db = get_db()


    if request.method == "POST":

        db.execute("""
            UPDATE creator
            SET instagram=?
            WHERE id=1
        """, (
            clean(
                request.form.get("instagram")
            ),
        ))


        db.commit()


        return redirect(
            url_for("social")
        )


    creator = db.execute(
        "SELECT * FROM creator WHERE id=1"
    ).fetchone()


    db.close()


    return render_template_string(
        SOCIAL_HTML,
        style=STYLE,
        creator=creator
    )


# ============================================================
# SETTINGS
# ============================================================

@app.route(
    "/settings",
    methods=["GET", "POST"]
)
def settings():

    check = login_required()

    if check:
        return check


    db = get_db()


    if request.method == "POST":

        db.execute("""
            UPDATE site_settings

            SET
                website_title=?,
                website_description=?

            WHERE id=1

        """, (
            clean(
                request.form.get(
                    "website_title"
                )
            ),
            clean(
                request.form.get(
                    "website_description"
                )
            )
        ))


        db.commit()


        return redirect(
            url_for("settings")
        )


    settings_row = db.execute(
        "SELECT * FROM site_settings WHERE id=1"
    ).fetchone()


    db.close()


    return render_template_string(
        SETTINGS_HTML,
        style=STYLE,
        settings=settings_row
    )


# ============================================================
# MEDIA PAGE
# ============================================================

@app.route("/media")
def media():

    check = login_required()

    if check:
        return check


    db = get_db()


    media_rows = db.execute("""
        SELECT *
        FROM media

        ORDER BY
            is_main DESC,
            id DESC
    """).fetchall()


    db.close()


    return render_template_string(
        MEDIA_HTML,
        style=STYLE,
        media=media_rows
    )


# ============================================================
# MEDIA UPLOAD
# ============================================================

@app.post(
    "/media/upload"
)
def media_upload():

    check = login_required()

    if check:
        return check


    file = request.files.get(
        "image"
    )


    if not file or not file.filename:

        return redirect(
            url_for("media")
        )


    original = os.path.basename(
        file.filename
    )


    extension = os.path.splitext(
        original
    )[1].lower()


    allowed = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }


    if extension not in allowed:

        return redirect(
            url_for("media")
        )


    stamp = datetime.now().strftime(
        "%Y%m%d%H%M%S%f"
    )


    filename = (
        "image_"
        + stamp
        + extension
    )


    path = os.path.join(
        MEDIA_DIR,
        filename
    )


    file.save(path)


    db = get_db()


    db.execute("""
        INSERT INTO media
        (
            filename,
            original_name,
            uploaded_at,
            is_main
        )

        VALUES
        (?, ?, ?, 0)

    """, (
        filename,
        original,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))


    db.commit()

    db.close()


    return redirect(
        url_for("media")
    )


# ============================================================
# SET MAIN IMAGE
# ============================================================

@app.route(
    "/media/set-main/<int:media_id>"
)
def set_main(media_id):

    check = login_required()

    if check:
        return check


    db = get_db()


    item = db.execute("""
        SELECT *
        FROM media
        WHERE id=?
    """, (media_id,)).fetchone()


    if item:

        db.execute(
            "UPDATE media SET is_main=0"
        )


        db.execute("""
            UPDATE media
            SET is_main=1
            WHERE id=?
        """, (media_id,))


        db.commit()


    db.close()


    return redirect(
        url_for("media")
    )


# ============================================================
# DELETE MEDIA
# ============================================================

@app.post(
    "/media/delete/<int:media_id>"
)
def media_delete(media_id):

    check = login_required()

    if check:
        return check


    db = get_db()


    item = db.execute("""
        SELECT *
        FROM media
        WHERE id=?
    """, (media_id,)).fetchone()


    if item and item["filename"] != MAIN_IMAGE:

        path = os.path.join(
            MEDIA_DIR,
            item["filename"]
        )


        if os.path.exists(path):

            os.remove(path)


        db.execute(
            "DELETE FROM media WHERE id=?",
            (media_id,)
        )


        db.commit()


    db.close()


    return redirect(
        url_for("media")
    )


# ============================================================
# PUBLIC MEDIA
# ============================================================

@app.route(
    "/media/public/<path:filename>"
)
def media_public(filename):

    return send_from_directory(
        MEDIA_DIR,
        filename
    )


# ============================================================
# IMAGE CHECK
# ============================================================

@app.route("/image-check")
def image_check():

    path = os.path.join(
        STATIC_DIR,
        MAIN_IMAGE
    )


    return {
        "exists": os.path.exists(path),
        "image": MAIN_IMAGE,
        "path": path,
        "static_url": (
            "/static/"
            + MAIN_IMAGE
        )
    }


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# START
# ============================================================
init_database()

if __name__ == "__main__":




    print()
    print("==============================================")
    print("             ABHINANDAN FITNESS")
    print("                  RITESH HQ")
    print("==============================================")
    print()
    print("Website:")
    print("http://127.0.0.1:5001")
    print()
    print("Ritesh HQ:")
    print("http://127.0.0.1:5001/login")
    print()
    print("Media:")
    print("http://127.0.0.1:5001/media")
    print()
    print("Creator ID:")
    print(USERNAME)
    print()
    print("==============================================")
    print()


    # Local testing.
    # Before public deployment, debug should be False.
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False
    )