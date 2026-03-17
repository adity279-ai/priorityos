# PriorityOS — Smart Task Priority Dashboard

PriorityOS is a premium dark-themed productivity dashboard built with **Python, Streamlit, Pandas, Plotly, and SQLite**.

It helps users:
- rank tasks automatically
- organize work by urgency and importance
- estimate daily focus time
- track deadlines
- visualize task status with charts

## Features

- Smart priority scoring
- Daily work-time recommendation
- Dark modern SaaS-style UI
- SQLite database for task storage
- Priority chart and status chart
- Upcoming deadlines panel
- Quick actions for completing and deleting tasks

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- SQLite

## Project Structure

```text
priorityos/
│
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
└── tasks.db   # created automatically when app runs
```

## How It Works

Each task gets ranked using:
- urgency
- importance
- deadline pressure
- estimated workload

### Priority Logic

The app calculates a weighted score so that:
- tasks with close deadlines move up
- highly important tasks move up
- urgent tasks move up
- larger workload tasks get extra weight

### Daily Recommendation

The app also recommends:

`daily hours = estimated total hours / days left`

This helps users know how much time they should work on a task each day.

## Installation

Clone the repository or download the files, then run:

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## Example Tasks

Try these sample inputs:

### 1. Python Assignment
- Urgency: 5
- Importance: 5
- Due: Tomorrow
- Estimated Hours: 6

### 2. Portfolio Project
- Urgency: 4
- Importance: 5
- Due: In 4 days
- Estimated Hours: 8

### 3. Gym Plan
- Urgency: 2
- Importance: 3
- Due: In 7 days
- Estimated Hours: 2

## Why This Project Is Good for Portfolio

This project shows:
- Python programming
- real app development
- UI design
- data handling with Pandas
- visualization with Plotly
- local database integration with SQLite

## Resume Description

Built a premium dark-themed task management dashboard using Python, Streamlit, Plotly, Pandas, and SQLite that automatically ranks tasks by urgency, importance, deadline pressure, and workload while recommending daily focus hours.

## Future Improvements

- Login system
- Cloud sync
- Calendar integration
- AI-generated productivity suggestions
- Mobile responsive layout
- Export tasks to CSV or PDF

## License

This project is open for learning and portfolio use.
