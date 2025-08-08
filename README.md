# Calendar Scheduling App

This is a simple Flask‑based calendar application that allows a user to create events, share a unique link with collaborators to collect their availability, and review all responses.  When the user desires, they can also view all of their scheduled events on a dedicated calendar page.

## Features

* **Create events** with a title, description and date/time.
* **Share a link** with collaborators so they can mark their availability and leave a note.
* **View event details** including all availability responses.
* **Calendar view** that lists all events (activated via the home page).

## Setup

1. Install Python 3.8+.
2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python3 app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`.

> **Note:** The first time the application runs, it will automatically create an SQLite database file (`calendar.db`) in the project directory to store events and responses.

## Usage

* On the home page (`/`) you can see a list of events and links to create a new event or view your calendar.
* On the **Create New Event** page, fill in the form and submit.  A unique link will be generated; share this with collaborators.
* The **Invitation** page allows collaborators to enter their name, availability and any notes.  Responses are stored in the database.
* The **Event Details** page displays the event information and all collected availability responses.
* The **Calendar** page (accessed via the home page) lists all of your events.  This view is activated by you as the user and is not shared by default.