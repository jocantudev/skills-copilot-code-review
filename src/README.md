# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- View active school announcements
- Manage announcements while signed in as a teacher

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | Get announcements currently visible to all visitors                 |
| GET    | `/announcements/manage?teacher_username={username}`               | Get all announcements for a signed-in teacher                       |
| POST   | `/announcements?teacher_username={username}`                      | Create an announcement for a signed-in teacher                     |
| PUT    | `/announcements/{id}?teacher_username={username}`                 | Update an announcement for a signed-in teacher                     |
| DELETE | `/announcements/{id}?teacher_username={username}`                 | Delete an announcement for a signed-in teacher                     |

Announcement create and update requests use this JSON body. `start_date` is optional; `expiration_date` is required and must not precede it.

```json
{
   "message": "Activity registration is open.",
   "start_date": "2026-09-01",
   "expiration_date": "2026-09-30"
}
```

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

3. **Announcements** - Uses a generated identifier:
   - Message
   - Optional start date
   - Required expiration date

All data is stored in MongoDB. The application seeds example data, including an announcement, when its collection is empty.
