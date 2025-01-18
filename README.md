# organizeAIO
organizeAIO is an all-in-one platform to manage your hackathon. 

## Features
- Attendee Management
    - View as a table
    - CRUD ops
    - Download as CSV
- Registration Form
    - CRUD ops
    - Customizable with 10 input options
    - Customize question order
- Event schedule
    - CRUD ops
    - Publicly viewable
- Finances
    - Read only view from HCB
- Projects
    - Public gallery
    - public submit page
    - CRUD ops
- Judging
    - CRUD ops
    - Judges can leave comments
    - Avg. and cumulative automatically calculated
- Public pages
    - Event description
    - Schedule
    - Judging criteria
    - registration page
    - project gallery/submission

## Tech Stack
- Frontend
    - Tailwind + Franken UI
- Backend
    - Flask
- Database, Auth, File Storage
    - Appwrite
- Deployment
    - Eventlet, WSGI

## Self Hosting
- Clone the repo
- Install the dependencies
```pip install -r requirements.txt```
- Setup Appwrite separately (Create a project)
- Fill out `.env` from `.env.example`
- Run the app
```python3 main.py```