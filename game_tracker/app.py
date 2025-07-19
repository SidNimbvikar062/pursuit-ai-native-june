import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os

# --- Database Configuration ---
DATABASE_DIR = r'C:\Users\snimb\Documents\AI_Native_Repo\game_tracker'
DATABASE_NAME = os.path.join(DATABASE_DIR, 'game_tracker.db')

# Ensure the database directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)


# IMPORTANT: Replace with your actual Steam Web API Key
STEAM_API_KEY = '8AA8DCE881024DB064ABD4B4EAA82201'


# --- Database Utility Functions ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserName TEXT UNIQUE NOT NULL,
            Email TEXT UNIQUE NOT NULL,
            PasswordHash TEXT NOT NULL,
            RegistrationDate TEXT NOT NULL,
            SteamID TEXT UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Games (
            GameID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL,
            Developer TEXT NOT NULL,
            Platform TEXT NOT NULL,
            Genre TEXT,
            ReleaseYear INTEGER,
            PlaytimeEstimateHours INTEGER,
            SteamAppID TEXT,
            Description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserGames (
            UserGameID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            GameID INTEGER NOT NULL,
            Status TEXT NOT NULL, -- ENUM: 'Owned - Backlog', 'Playing', 'Completed', 'Dropped'
            Rating INTEGER, -- NULLABLE (1-10 scale)
            DateAdded TEXT NOT NULL, -- Date game was added to library
            LastPlayed TEXT, -- Date game was last played
            PlaytimeHours INTEGER, -- NULLABLE
            Notes TEXT, -- NULLABLE
            LastUpdated TEXT NOT NULL, -- YYYY-MM-DD HH:MM:SS (metadata for our system)
            FOREIGN KEY (UserID) REFERENCES Users(UserID),
            FOREIGN KEY (GameID) REFERENCES Games(GameID)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database tables created successfully or already exist.")

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here_a_very_long_and_random_string'

create_tables()

@app.after_request
def add_no_cache_headers(response):
    if request.method == 'POST':
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('my_library'))
    return render_template('index.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        steam_id = request.form.get('steam_id', '').strip()

        if steam_id and not steam_id.isdigit():
            flash("SteamID must contain only digits if provided.", 'error')
            return render_template('register.html', username=username, email=email, steam_id=steam_id)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Users (UserName, Email, PasswordHash, RegistrationDate, SteamID) VALUES (?, ?, ?, ?, ?)",
                           (username, email, password, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), steam_id if steam_id else None))
            conn.commit()
            session['user_id'] = cursor.lastrowid
            session['username'] = username
            flash('Registration successful and you are logged in!', 'success')

            if steam_id:
                success, message = import_steam_games_for_user(session['user_id'], steam_id)
                if success:
                    flash(f"Steam games imported successfully! {message}", 'info')
                else:
                    flash(f"Failed to import Steam games: {message}", 'warning')

            return redirect(url_for('my_library'))
        except sqlite3.IntegrityError:
            conn.rollback()
            flash("Username, Email, or SteamID already exists. Please choose different ones.", 'error')
            return render_template('register.html', username=username, email=email, steam_id=steam_id, error="Username, Email, or SteamID already exists.")
        except Exception as e:
            conn.rollback()
            flash(f"An unexpected error occurred during registration: {e}", 'error')
            return render_template('register.html', username=username, email=email, steam_id=steam_id)
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT UserID, UserName, PasswordHash FROM Users WHERE UserName = ?", (username,)).fetchone()
        conn.close()

        if user and user['PasswordHash'] == password:
            session['user_id'] = user['UserID']
            session['username'] = user['UserName']
            flash('Login successful!', 'success')
            return redirect(url_for('my_library'))
        else:
            flash("Invalid username or password.", 'error')
            return render_template('login.html', error="Invalid username or password.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/add_game', methods=('GET', 'POST'))
def add_game():
    if 'user_id' not in session:
        flash('Please log in to add a game.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        developer = request.form['developer'].strip()
        platform = request.form['platform']
        genre = request.form.get('genre', '').strip()
        release_year = request.form.get('release_year', type=int)
        playtime_estimate = request.form.get('playtime_estimate', type=int)
        steam_appid = request.form.get('steam_appid', '').strip()
        description = request.form.get('description', '').strip()

        conn = get_db_connection()
        game_id = None
        try:
            existing_game = conn.execute("SELECT GameID FROM Games WHERE Title = ? AND Developer = ?", (title, developer)).fetchone()
            if existing_game:
                game_id = existing_game['GameID']
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Games (Title, Developer, Platform, Genre, ReleaseYear, PlaytimeEstimateHours, SteamAppID, Description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, developer, platform, genre, release_year, playtime_estimate, steam_appid if steam_appid else None, description))
                conn.commit()
                game_id = cursor.lastrowid

            user_has_game = conn.execute("SELECT UserGameID FROM UserGames WHERE UserID = ? AND GameID = ?", (session['user_id'], game_id)).fetchone()
            if user_has_game:
                flash(f'You already have "{title}" in your library!', 'info')
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO UserGames (UserID, GameID, Status, DateAdded, LastUpdated)
                    VALUES (?, ?, ?, ?, ?)
                """, (session['user_id'], game_id, 'Owned - Backlog', datetime.datetime.now().strftime('%Y-%m-%d'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                flash(f'"{title}" added to your library!', 'success')

            return redirect(url_for('my_library'))

        except sqlite3.IntegrityError as e:
            conn.rollback()
            flash(f"Error adding game: A unique constraint failed. This might happen if you tried to add a game with a Steam App ID that already exists for another game in the database, or identical Title/Developer.", 'error')
        except Exception as e:
            conn.rollback()
            flash(f"An unexpected error occurred while adding game: {e}", 'error')
        finally:
            conn.close()

    return render_template('add_game.html', now=datetime.datetime.now())

@app.route('/my_library')
def my_library():
    if 'user_id' not in session:
        flash('Please log in to view your library.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user_id = session['user_id']

    recently_played_games = conn.execute("""
        SELECT
            ug.UserGameID, g.Title, g.Developer, g.Platform, g.Genre, g.SteamAppID, g.Description,
            ug.Status, ug.Rating, ug.PlaytimeHours, ug.Notes, ug.DateAdded, ug.LastPlayed
        FROM UserGames ug
        JOIN Games g ON ug.GameID = g.GameID
        WHERE ug.UserID = ? AND ug.LastPlayed IS NOT NULL
        ORDER BY ug.LastPlayed DESC, g.Title ASC
    """, (user_id,)).fetchall()

    unplayed_games = conn.execute("""
        SELECT
            ug.UserGameID, g.Title, g.Developer, g.Platform, g.Genre, g.SteamAppID, g.Description,
            ug.Status, ug.Rating, ug.PlaytimeHours, ug.Notes, ug.DateAdded, ug.LastPlayed
        FROM UserGames ug
        JOIN Games g ON ug.GameID = g.GameID
        WHERE ug.UserID = ? AND ug.LastPlayed IS NULL
        ORDER BY g.Title ASC
    """, (user_id,)).fetchall()

    conn.close()
    return render_template('my_library.html',
                           recently_played_games=recently_played_games,
                           unplayed_games=unplayed_games,
                           username=session['username'])

@app.route('/edit_user_game/<int:user_game_id>', methods=('GET', 'POST'))
def edit_user_game(user_game_id):
    if 'user_id' not in session:
        flash('Please log in to edit games.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user_game = conn.execute("""
        SELECT
            ug.UserGameID, ug.UserID, ug.GameID, ug.Status, ug.Rating,
            ug.DateAdded, ug.LastPlayed, ug.PlaytimeHours, ug.Notes,
            g.Title, g.Developer, g.Platform, g.Genre, g.ReleaseYear,
            g.PlaytimeEstimateHours, g.SteamAppID, g.Description
        FROM UserGames ug
        JOIN Games g ON ug.GameID = g.GameID
        WHERE ug.UserGameID = ? AND ug.UserID = ?
    """, (user_game_id, session['user_id'])).fetchone()

    if not user_game:
        conn.close()
        flash('Game not found in your library or you do not have permission to edit.', 'error')
        return redirect(url_for('my_library'))

    if request.method == 'POST':
        status = request.form['status']
        rating = request.form.get('rating', type=int)
        playtime_hours = request.form.get('playtime_hours', type=int)
        notes = request.form.get('notes', '').strip()
        
        # When a game is manually edited, assume it's "last played" now if playtime or status changed to 'Playing'
        last_played = None
        if playtime_hours is not None and playtime_hours > 0: # If playtime is explicitly set, assume it was played
            last_played = datetime.datetime.now().strftime('%Y-%m-%d')
        elif status == 'Playing': # If status is set to Playing, assume it was played
            last_played = datetime.datetime.now().strftime('%Y-%m-%d')
        elif user_game['LastPlayed']: # Otherwise, preserve existing LastPlayed date if it exists
            last_played = user_game['LastPlayed']


        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE UserGames
                SET Status = ?, Rating = ?, LastPlayed = ?,
                    PlaytimeHours = ?, Notes = ?, LastUpdated = ?
                WHERE UserGameID = ? AND UserID = ?
            """, (status, rating, last_played, playtime_hours, notes,
                  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  user_game_id, session['user_id']))

            conn.commit()
            flash(f'"{user_game["Title"]}" updated successfully!', 'success')
            return redirect(url_for('my_library'))

        except Exception as e:
            conn.rollback()
            flash(f"Error updating game: {e}", 'error')
        finally:
            conn.close()
    
    conn.close()
    return render_template('edit_user_game.html', game=user_game)

@app.route('/delete_user_game/<int:user_game_id>', methods=('POST',))
def delete_user_game(user_game_id):
    if 'user_id' not in session:
        flash('Please log in to delete games.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        game_title_row = conn.execute("SELECT g.Title FROM UserGames ug JOIN Games g ON ug.GameID = g.GameID WHERE ug.UserGameID = ? AND ug.UserID = ?", (user_game_id, session['user_id'])).fetchone()
        game_title = game_title_row['Title'] if game_title_row else "a game"

        cursor = conn.cursor()
        cursor.execute("DELETE FROM UserGames WHERE UserGameID = ? AND UserID = ?",
                       (user_game_id, session['user_id']))
        conn.commit()

        if cursor.rowcount > 0:
            flash(f'"{game_title}" successfully removed from your library!', 'success')
        else:
            flash('Game not found in your library or you do not have permission to delete.', 'error')

    except Exception as e:
        conn.rollback()
        flash(f"Error deleting game: {e}", 'error')
    finally:
        conn.close()

    return redirect(url_for('my_library'))

def calculate_steam_game_status(playtime_hours, last_played_timestamp):
    """
    Calculates the status of a Steam game based on playtime and last played date.
    
    Args:
        playtime_hours (int): Total playtime in hours.
        last_played_timestamp (int): Unix timestamp of last played time from Steam API.
    
    Returns:
        str: The calculated status ('Playing', 'Completed', 'Dropped', 'Owned - Backlog').
        str: The formatted 'LastPlayed' date (YYYY-MM-DD) or None.
    """
    if playtime_hours is None:
        playtime_hours = 0

    current_date = datetime.datetime.now()
    last_played_date_str = None
    last_played_dt = None

    if last_played_timestamp and last_played_timestamp > 0:
        last_played_dt = datetime.datetime.fromtimestamp(last_played_timestamp)
        last_played_date_str = last_played_dt.strftime('%Y-%m-%d')

    # Default status
    status = 'Owned - Backlog'

    if playtime_hours > 0 and last_played_dt:
        # Played in the last month
        if (current_date - last_played_dt).days <= 30:
            status = 'Playing'
        # Played in the last year, more than 5 hours
        elif (current_date - last_played_dt).days <= 365 and playtime_hours >= 5:
            status = 'Completed'
        # Played in the last year, less than 5 hours
        elif (current_date - last_played_dt).days <= 365 and playtime_hours < 5:
            status = 'Dropped'
        # Played over a year ago, regardless of playtime
        else:
            status = 'Owned - Backlog'
    elif playtime_hours == 0 or last_played_dt is None:
        status = 'Owned - Backlog'

    return status, last_played_date_str


@app.route('/import_steam', methods=['GET', 'POST'])
def import_steam():
    if 'user_id' not in session:
        flash('Please log in to import Steam games.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user_steam_id_row = conn.execute("SELECT SteamID FROM Users WHERE UserID = ?", (session['user_id'],)).fetchone()
    conn.close()
    
    initial_steam_id = user_steam_id_row['SteamID'] if user_steam_id_row and user_steam_id_row['SteamID'] else ''

    if request.method == 'POST':
        steam_id_input = request.form['steam_id'].strip()
        if not steam_id_input:
            flash("Please enter your SteamID64.", 'error')
            return render_template('import_steam.html', initial_steam_id=initial_steam_id)
        
        if not steam_id_input.isdigit():
            flash("SteamID must contain only digits.", 'error')
            return render_template('import_steam.html', initial_steam_id=initial_steam_id)

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET SteamID = ? WHERE UserID = ?", (steam_id_input, session['user_id']))
            conn.commit()
            flash("Your SteamID has been linked!", 'success')

            success, message = import_steam_games_for_user(session['user_id'], steam_id_input)
            if success:
                flash(f"Steam games imported successfully! {message}", 'success')
            else:
                flash(f"Failed to import Steam games: {message}", 'warning')

            return redirect(url_for('my_library'))
        except sqlite3.IntegrityError:
            conn.rollback()
            flash("This SteamID is already linked to another user account.", 'error')
        except Exception as e:
            conn.rollback()
            flash(f"An unexpected error occurred while linking SteamID: {e}", 'error')
        finally:
            conn.close()

    return render_template('import_steam.html', initial_steam_id=initial_steam_id)


def import_steam_games_for_user(user_id, steam_id):
    if not STEAM_API_KEY or STEAM_API_KEY == 'YOUR_STEAM_API_KEY_HERE':
        return False, "Steam API Key is not configured. Please get one from steamcommunity.com/dev/apikey."
    if not steam_id:
        return False, "No SteamID provided."

    owned_games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id}&format=json&include_appinfo=1&include_played_free_games=1"
    
    try:
        response = requests.get(owned_games_url)
        response.raise_for_status()
        data = response.json()

        if not data or 'response' not in data or 'games' not in data['response']:
            return False, "Could not retrieve games from Steam API. Check if your SteamID is correct and your profile is public (Game Details in privacy settings)."

        games_data = data['response']['games']
        imported_count = 0
        updated_playtime_count = 0
        skipped_count = 0
        
        conn = get_db_connection()
        current_date_str = datetime.datetime.now().strftime('%Y-%m-%d')

        for game_steam in games_data:
            game_title = game_steam.get('name')
            steam_appid = str(game_steam.get('appid'))
            playtime_forever_minutes = game_steam.get('playtime_forever', 0)
            playtime_hours = round(playtime_forever_minutes / 60)
            # Steam's last_played is a Unix timestamp (seconds since epoch)
            rtime_last_played = game_steam.get('rtime_last_played', 0)

            if not game_title:
                skipped_count += 1
                continue

            # Determine status and LastPlayed date based on Steam data
            calculated_status, calculated_last_played_date_str = \
                calculate_steam_game_status(playtime_hours, rtime_last_played)

            game_record = conn.execute("SELECT GameID FROM Games WHERE SteamAppID = ?", (steam_appid,)).fetchone()
            game_id = None

            if game_record:
                game_id = game_record['GameID']
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Games (Title, Developer, Platform, Genre, ReleaseYear, PlaytimeEstimateHours, SteamAppID, Description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (game_title, "Steam User", "PC (Steam)", "Unknown", None, None, steam_appid, f"Imported from Steam. Steam App ID: {steam_appid}"))
                conn.commit()
                game_id = cursor.lastrowid
            
            if game_id:
                user_game_entry = conn.execute("SELECT UserGameID FROM UserGames WHERE UserID = ? AND GameID = ?", (user_id, game_id)).fetchone()
                
                if user_game_entry:
                    # Update existing entry with new playtime and calculated status/last_played
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE UserGames
                        SET PlaytimeHours = ?, LastPlayed = ?, Status = ?, LastUpdated = ?
                        WHERE UserGameID = ?
                    """, (playtime_hours, calculated_last_played_date_str, calculated_status,
                          datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_game_entry['UserGameID']))
                    conn.commit()
                    updated_playtime_count += 1
                else:
                    # Add new entry for the user. DateAdded is current date.
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO UserGames (UserID, GameID, Status, PlaytimeHours, DateAdded, LastPlayed, LastUpdated)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, game_id, calculated_status, playtime_hours, current_date_str,
                          calculated_last_played_date_str, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    conn.commit()
                    imported_count += 1
        
        conn.close()
        return True, f"Successfully imported {imported_count} new games and updated playtime for {updated_playtime_count} existing games. Skipped {skipped_count} invalid entries."

    except requests.exceptions.RequestException as e:
        return False, f"Network or API error while connecting to Steam: {e}. Please check your internet connection and API key."
    except Exception as e:
        return False, f"An unexpected error occurred during Steam import: {e}"


if __name__ == '__main__':
    app.run(debug=True)