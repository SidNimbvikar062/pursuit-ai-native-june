import sqlite3
import datetime

DATABASE_NAME = 'game_tracker.db'

def create_tables():
    """
    Connects to the SQLite database and creates the necessary tables
    (Users, Games, UserGames) if they don't already exist.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Create USERS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserName TEXT UNIQUE NOT NULL,
            Email TEXT UNIQUE NOT NULL,
            RegistrationDate TEXT NOT NULL
        )
    ''')

    # Create GAMES table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Games (
            GameID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL,
            Developer TEXT NOT NULL,
            Platform TEXT NOT NULL,
            Genre TEXT,
            ReleaseYear INTEGER,
            PlaytimeEstimateHours INTEGER,
            SteamAppID TEXT UNIQUE,
            Description TEXT
        )
    ''')

    # Create USER_GAMES table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserGames (
            UserGameID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            GameID INTEGER NOT NULL,
            Status TEXT NOT NULL, -- ENUM: 'Owned - Backlog', 'Playing', 'Completed', 'Dropped'
            Rating INTEGER, -- NULLABLE (1-10 scale)
            StartDate TEXT, -- NULLABLE (YYYY-MM-DD)
            CompletionDate TEXT, -- NULLABLE (YYYY-MM-DD)
            PlaytimeHours INTEGER, -- NULLABLE
            Notes TEXT, -- NULLABLE
            LastUpdated TEXT NOT NULL, -- YYYY-MM-DD HH:MM:SS
            FOREIGN KEY (UserID) REFERENCES Users(UserID),
            FOREIGN KEY (GameID) REFERENCES Games(GameID)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database tables created successfully or already exist.")

# Main execution block
if __name__ == "__main__":
    create_tables()
    print("Welcome to the Video Game Tracker!")
    # We'll add more functionality here later