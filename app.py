import sqlite3
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="PriorityOS",
    page_icon="⚡",
    layout="wide"
)

# -----------------------------
# CUSTOM DARK UI
# -----------------------------
st.markdown("""
<style>
:root {
    --bg: #0b1020;
    --panel: rgba(255,255,255,0.06);
    --panel-2: rgba(255,255,255,0.03);
    --border: rgba(255,255,255,0.12);
    --text: #f3f4f6;
    --muted: #9ca3af;
    --accent: #7c3aed;
    --accent2: #06b6d4;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

.stApp {
    background: linear-gradient(135deg, #0b1020 0%, #111827 50%, #0f172a 100%);
    color: var(--text);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4, h5, h6, p, label, div {
    color: var(--text) !important;
}

[data-testid="stSidebar"] {
    background: rgba(17, 24, 39, 0.95);
    border-right: 1px solid rgba(255,255,255,0.08);
}

.card {
    background: var(--panel);
    backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.hero {
    padding: 28px;
    border-radius: 24px;
    background:
        radial-gradient(circle at top right, rgba(124,58,237,0.30), transparent 25%),
        radial-gradient(circle at bottom left, rgba(6,182,212,0.20), transparent 30%),
        rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 8px 22px rgba(0,0,0,0.20);
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    margin-top: 6px;
}

.metric-label {
    color: #cbd5e1 !important;
    font-size: 0.95rem;
}

.small-muted {
    color: #94a3b8 !important;
    font-size: 0.92rem;
}

.priority-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.85rem;
    margin-top: 8px;
}

.critical { background: rgba(239,68,68,0.18); border: 1px solid rgba(239,68,68,0.35); }
.high { background: rgba(245,158,11,0.18); border: 1px solid rgba(245,158,11,0.35); }
.medium { background: rgba(6,182,212,0.18); border: 1px solid rgba(6,182,212,0.35); }
.low { background: rgba(16,185,129,0.18); border: 1px solid rgba(16,185,129,0.35); }

div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03);
    border-radius: 18px;
    padding: 10px;
    border: 1px solid rgba(255,255,255,0.07);
}

.stButton > button {
    width: 100%;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.10);
    background: linear-gradient(135deg, rgba(124,58,237,0.95), rgba(6,182,212,0.85));
    color: white;
    font-weight: 600;
    padding: 0.7rem 1rem;
}

.stSelectbox div[data-baseweb="select"],
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background: rgba(255,255,255,0.04) !important;
    color: white !important;
    border-radius: 12px !important;
}

hr {
    border-color: rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE
# -----------------------------
DB_NAME = "tasks.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    category TEXT,
    urgency INTEGER,
    importance INTEGER,
    due_date TEXT,
    estimated_hours REAL,
    status TEXT,
    created_at TEXT
)
""")
conn.commit()

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def days_left(due_date_str: str) -> int:
    due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    return (due - date.today()).days

def deadline_pressure(days: int) -> int:
    if days <= 0:
        return 10
    if days == 1:
        return 9
    if days <= 3:
        return 8
    if days <= 7:
        return 6
    if days <= 14:
        return 4
    return 2

def calculate_priority_score(urgency: int, importance: int, due_date_str: str, estimated_hours: float) -> float:
    d_left = days_left(due_date_str)
    d_pressure = deadline_pressure(d_left)
    workload_factor = min(estimated_hours, 10)

    score = (
        urgency * 0.35 +
        importance * 0.35 +
        d_pressure * 0.20 +
        workload_factor * 0.10
    )
    return round(score, 2)

def recommend_daily_hours(estimated_hours: float, due_date_str: str) -> float:
    d_left = days_left(due_date_str)
    if d_left <= 0:
        return round(estimated_hours, 2)
    return round(estimated_hours / d_left, 2)

def priority_label(score: float) -> str:
    if score >= 7.5:
        return "Critical"
    if score >= 5.5:
        return "High"
    if score >= 4.0:
        return "Medium"
    return "Low"

def priority_class(label: str) -> str:
    return {
        "Critical": "critical",
        "High": "high",
        "Medium": "medium",
        "Low": "low"
    }.get(label, "low")

def load_tasks() -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM tasks ORDER BY id DESC", conn)

def add_task(task_name, category, urgency, importance, due_date, estimated_hours, status):
    cursor.execute("""
        INSERT INTO tasks (
            task_name, category, urgency, importance, due_date,
            estimated_hours, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task_name,
        category,
        urgency,
        importance,
        due_date,
        estimated_hours,
        status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()

def delete_task(task_id: int):
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

def mark_completed(task_id: int):
    cursor.execute("UPDATE tasks SET status = 'Completed' WHERE id = ?", (task_id,))
    conn.commit()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.markdown("## ⚙️ Add Task")

with st.sidebar.form("task_form", clear_on_submit=True):
    task_name = st.text_input("Task name")
    category = st.selectbox("Category", ["Study", "Project", "Work", "Personal", "Health", "Other"])
    urgency = st.slider("Urgency", 1, 5, 3)
    importance = st.slider("Importance", 1, 5, 3)
    due_date = st.date_input("Due date", min_value=date.today())
    estimated_hours = st.number_input("Estimated total hours", min_value=0.5, max_value=100.0, value=2.0, step=0.5)
    status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])

    submit = st.form_submit_button("Add Task")

    if submit:
        if task_name.strip():
            add_task(
                task_name.strip(),
                category,
                urgency,
                importance,
                due_date.strftime("%Y-%m-%d"),
                estimated_hours,
                status
            )
            st.sidebar.success("Task added successfully.")
        else:
            st.sidebar.error("Enter a task name.")

# -----------------------------
# DATA
# -----------------------------
df = load_tasks()

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div class="hero">
    <h1 style="margin-bottom: 8px;">⚡ PriorityOS</h1>
    <p class="small-muted" style="font-size: 1.05rem;">
        A smart task-priority dashboard that ranks work by urgency, importance, deadline pressure, and workload.
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

if df.empty:
    st.markdown("""
<div class="card">
    <h3>Welcome</h3>
    <p class="small-muted">
        Start by adding a few tasks from the sidebar. The app will automatically rank them
        and recommend how many hours you should work on each one per day.
    </p>
    <p>
        Try sample tasks like:
        <br>• Python Assignment — due tomorrow — 6 hours
        <br>• Portfolio Project — due in 4 days — 8 hours
        <br>• Gym Plan — due in 7 days — 2 hours
    </p>
</div>
""", unsafe_allow_html=True)
else:
    df["Days Left"] = df["due_date"].apply(days_left)
    df["Priority Score"] = df.apply(
        lambda row: calculate_priority_score(
            row["urgency"], row["importance"], row["due_date"], row["estimated_hours"]
        ),
        axis=1
    )
    df["Recommended Daily Hours"] = df.apply(
        lambda row: recommend_daily_hours(row["estimated_hours"], row["due_date"]),
        axis=1
    )
    df["Priority Level"] = df["Priority Score"].apply(priority_label)

    df = df.sort_values(by=["Priority Score", "Days Left"], ascending=[False, True]).reset_index(drop=True)
    active_df = df[df["status"] != "Completed"].copy()

    total_tasks = len(df)
    pending_tasks = len(df[df["status"] == "Pending"])
    progress_tasks = len(df[df["status"] == "In Progress"])
    total_daily_hours = round(active_df["Recommended Daily Hours"].sum(), 2)

    # -----------------------------
    # METRICS
    # -----------------------------
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Tasks</div>
            <div class="metric-value">{total_tasks}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Pending</div>
            <div class="metric-value">{pending_tasks}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">In Progress</div>
            <div class="metric-value">{progress_tasks}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Daily Focus Time</div>
            <div class="metric-value">{total_daily_hours}h</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # -----------------------------
    # TOP PRIORITY
    # -----------------------------
    if not active_df.empty:
        top = active_df.iloc[0]
        pill_class = priority_class(top["Priority Level"])
        st.markdown(f"""
        <div class="card">
            <h3>🔥 Today’s Top Priority</h3>
            <h2 style="margin-bottom: 0;">{top["task_name"]}</h2>
            <div class="priority-pill {pill_class}">{top["Priority Level"]} Priority</div>
            <p style="margin-top: 16px;">
                Due in <b>{top["Days Left"]} day(s)</b> · Recommended work:
                <b>{top["Recommended Daily Hours"]} hrs/day</b> · Score:
                <b>{top["Priority Score"]}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # -----------------------------
    # CHARTS
    # -----------------------------
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Priority Score by Task")
        chart_df = active_df.sort_values("Priority Score", ascending=True)
        fig1 = px.bar(
            chart_df,
            x="Priority Score",
            y="task_name",
            orientation="h",
            template="plotly_dark",
            text="Priority Score"
        )
        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=420
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Status Overview")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig2 = px.pie(
            status_counts,
            names="Status",
            values="Count",
            hole=0.55,
            template="plotly_dark"
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=420
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # -----------------------------
    # TABLE + DEADLINES
    # -----------------------------
    left, right = st.columns([1.6, 1])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Task Dashboard")
        display_df = df[[
            "id", "task_name", "category", "urgency", "importance",
            "due_date", "Days Left", "estimated_hours",
            "Recommended Daily Hours", "Priority Score",
            "Priority Level", "status"
        ]].rename(columns={
            "id": "ID",
            "task_name": "Task",
            "category": "Category",
            "urgency": "Urgency",
            "importance": "Importance",
            "due_date": "Due Date",
            "estimated_hours": "Estimated Hours",
            "status": "Status"
        })
        st.dataframe(display_df, use_container_width=True, height=380)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Upcoming Deadlines")
        deadline_df = active_df[[
            "task_name", "due_date", "Days Left", "Recommended Daily Hours", "Priority Level"
        ]].sort_values(by="due_date").rename(columns={
            "task_name": "Task",
            "due_date": "Due Date"
        })
        st.dataframe(deadline_df, use_container_width=True, height=380)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # -----------------------------
    # INSIGHTS
    # -----------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("AI Insights")

    for _, row in active_df.head(5).iterrows():
        st.markdown(
            f"""
            **{row['task_name']}** is ranked **{row['Priority Level']}**
            because it combines urgency **{row['urgency']}/5**, importance **{row['importance']}/5**,
            deadline in **{row['Days Left']} day(s)**, and workload of **{row['estimated_hours']} hour(s)**.
            Recommended daily effort: **{row['Recommended Daily Hours']} hrs/day**.
            """
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # -----------------------------
    # ACTIONS
    # -----------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Quick Actions")

    task_ids = df["id"].tolist()
    selected_id = st.selectbox("Select Task ID", task_ids)

    a1, a2 = st.columns(2)
    with a1:
        if st.button("Mark Selected Task Completed"):
            mark_completed(selected_id)
            st.success("Task marked as completed.")
            st.rerun()

    with a2:
        if st.button("Delete Selected Task"):
            delete_task(selected_id)
            st.warning("Task deleted.")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
