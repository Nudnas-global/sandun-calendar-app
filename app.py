from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import uuid
from datetime import datetime

def get_db_connection():
    """Create a connection to the SQLite database and configure row_factory for dict-like access."""
    conn = sqlite3.connect('calendar.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite database with tables for events and responses if they do not already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Table for events: stores basic information about each event
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            datetime TEXT
        );
        """
    )
    # Table for responses: stores availability entries submitted by collaborators
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT,
            name TEXT,
            available_start TEXT,
            available_end TEXT,
            description TEXT,
            FOREIGN KEY (event_id) REFERENCES events(id)
        );
        """
    )
    conn.commit()
    conn.close()


def create_app():
    """Application factory for creating the Flask app."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'a-very-secret-key'  # needed for flash messages

    # Initialize the database immediately when the app is created. Flask 3 removed
    # ``before_first_request``, so we call our init function here.
    init_db()

    @app.route('/')
    def index():
        """Home page: lists all created events and provides link to calendar and creation page."""
        conn = get_db_connection()
        events = conn.execute('SELECT * FROM events ORDER BY datetime').fetchall()
        conn.close()
        return render_template('index.html', events=events)

    @app.route('/create', methods=('GET', 'POST'))
    def create_event():
        """Page to create a new event. On POST, saves the event and displays share link."""
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            event_datetime = request.form['datetime']

            # Validate that a date/time was provided
            if not title or not event_datetime:
                flash('Title and date/time are required.')
                return render_template('create_event.html')

            event_id = str(uuid.uuid4())
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO events (id, title, description, datetime) VALUES (?, ?, ?, ?)',
                (event_id, title, description, event_datetime),
            )
            conn.commit()
            conn.close()

            # Show page with link for collaborator
            return render_template('create_success.html', event_id=event_id)

        return render_template('create_event.html')

    @app.route('/event/<event_id>')
    def event_details(event_id):
        """Display an individual event and all recorded availabilities for it."""
        conn = get_db_connection()
        event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
        responses = conn.execute('SELECT * FROM responses WHERE event_id = ? ORDER BY id', (event_id,)).fetchall()
        conn.close()
        if event is None:
            return 'Event not found', 404
        return render_template('event_details.html', event=event, responses=responses)

    @app.route('/invite/<event_id>', methods=('GET', 'POST'))
    def invite(event_id):
        """Page for collaborators to mark their availability and provide a description."""
        conn = get_db_connection()
        event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
        conn.close()
        if event is None:
            return 'Event not found', 404
        if request.method == 'POST':
            name = request.form['name']
            available_start = request.form['start']
            available_end = request.form['end']
            description = request.form['description']
            # Save response in database
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO responses (event_id, name, available_start, available_end, description) VALUES (?, ?, ?, ?, ?)',
                (event_id, name, available_start, available_end, description),
            )
            conn.commit()
            conn.close()
            return render_template('invite_success.html', event=event)
        # GET: show form
        return render_template('invite.html', event=event)

    @app.route('/calendar')
    def calendar():
        """Display all events in the calendar. This functionality is activated from the home page."""
        conn = get_db_connection()
        events = conn.execute('SELECT * FROM events ORDER BY datetime').fetchall()
        conn.close()
        return render_template('calendar.html', events=events)
    
    @app.route('/delete/<event_id>', methods=('POST',))
    def delete_event(event_id):
        """Delete an event and all its responses."""
        conn = get_db_connection()
        
        # Check if event exists
        event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
        if event is None:
            conn.close()
            return 'Event not found', 404
        
        # Delete all responses for this event first
        conn.execute('DELETE FROM responses WHERE event_id = ?', (event_id,))
        
        # Delete the event
        conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
        
        conn.commit()
        conn.close()
        
        flash(f'Event "{event["title"]}" has been deleted.')
        return redirect(url_for('index'))

    return app


if __name__ == '__main__':
    # The app only runs when executed directly. It is configured to listen on all interfaces for demonstration.
    app = create_app()
    app.run(debug=True)
else:
    # For production (Render)
    app = create_app()