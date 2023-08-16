import sqlite3
from flask import session

def user_image_context_processor():
    user_image = None
    username = None  # Initialize username to None
    if 'username' in session:
        username = session['username']
        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT image_url FROM users WHERE username = ?", (username,))
        user_image_result = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_image_result:
            user_image = user_image_result[0]
    return {'user_image': user_image, 'username': username}  # Include 'username' in the returned context
