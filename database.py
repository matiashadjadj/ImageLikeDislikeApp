import sqlite3
import os

def setup_database():
    conn = sqlite3.connect('dating_app.db')
    cursor = conn.cursor()
    
    # Create images table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        filename TEXT NOT NULL UNIQUE,
        liked INTEGER DEFAULT 0
    )
    ''')
    
    # Create user_actions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_actions (
        id INTEGER PRIMARY KEY,
        filename TEXT NOT NULL,
        liked INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def load_images_to_db(directory):
    """Load images from the specified directory into the database."""
    conn = sqlite3.connect('dating_app.db')
    cursor = conn.cursor()
    
    image_files = os.listdir(directory)
    for f in image_files:
        if f.endswith(('.png', '.jpg', '.jpeg')):  # Check for valid image formats
            cursor.execute('INSERT OR IGNORE INTO images (filename, liked) VALUES (?, ?)', (f, None))
    
    conn.commit()
    conn.close()

def add_image_to_db(new_image_path):
    """Add a new image to the database."""
    conn = sqlite3.connect('dating_app.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO images (filename, liked) VALUES (?, ?)', (os.path.basename(new_image_path), None))  # Save only the filename
    conn.commit()
    conn.close()

def fetch_images_from_db():
    """Fetch all image filenames from the database."""
    conn = sqlite3.connect('dating_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM images')
    image_files = cursor.fetchall()
    conn.close()
    return [f[0] for f in image_files]

def update_image_status(filename, liked):
    """Update the liked status of an image in the database."""
    conn = sqlite3.connect('dating_app.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE images SET liked = ? WHERE filename = ?', (liked, filename))
    conn.commit()
    conn.close()

def fetch_user_actions():
    """Fetch all user actions from the database."""
    conn = sqlite3.connect('dating_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT filename, liked, timestamp FROM user_actions')
    user_actions = cursor.fetchall()
    conn.close()
    return user_actions