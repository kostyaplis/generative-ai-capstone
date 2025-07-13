# database.py
import sqlite3
import os
import random


def employees_database():
    # Ensure data/databases directory exists
    db_dir = "data/databases"
    os.makedirs(db_dir, exist_ok=True)

    # Connect to database in the correct location
    db_path = os.path.join(db_dir, "employees.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Drop table if exists
    c.execute("DROP TABLE IF EXISTS employees;")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL,
            age INTEGER NOT NULL
        )
        """
    )

    # Sample employees data
    first_names = [
        "John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa",
        "William", "Mary", "James", "Patricia", "Richard", "Linda", "Thomas", "Susan",
        "Daniel", "Jennifer", "Matthew", "Elizabeth", "Christopher", "Margaret", "Andrew", "Nancy",
        "Joseph", "Karen", "Edward", "Betty", "Brian", "Dorothy"
    ]

    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
        "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
        "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee",
        "Walker", "Hall", "Allen", "Young", "King", "Wright"
    ]

    departments = [
        "Engineering", "Marketing", "Finance", "Human Resources", "Sales",
        "Research & Development", "Customer Service", "IT", "Operations", "Legal"
    ]

    # Generate 30 employees
    employees = []
    for i in range(30):
        first_name = first_names[i]
        last_name = last_names[i]
        department = random.choice(departments)
        salary = round(random.uniform(50000, 150000), 2)
        age = random.randint(22, 65)

        employees.append((first_name, last_name, department, salary, age))

    c.executemany(
        "INSERT INTO employees (first_name, last_name, department, salary, age) VALUES (?,?,?,?,?)",
        employees
    )

    conn.commit()
    print(f"Created employees database with {len(employees)} sample records")

    # Query the employees table to verify data
    c.execute("SELECT * FROM employees LIMIT 10")
    rows = c.fetchall()

    print("\nSample Employee Records:")
    # Print results to stdout
    for row in rows:
        print(row)

    conn.close()


def events_database():
    # Ensure data/databases directory exists
    db_dir = "data/databases"
    os.makedirs(db_dir, exist_ok=True)

    # Connect to database in the correct location
    db_path = os.path.join(db_dir, "events.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Drop table if exists
    c.execute("DROP TABLE IF EXISTS events;")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            name TEXT,
            indoor BOOLEAN,  -- 'indoor' or 'outdoor'
            description TEXT,
            location TEXT,
            city TEXT,
            date TEXT
        )
    """
    )

    # Sample events for Singapore from July 12-20, 2025
    events = [
        # July 12
        (
            "Singapore Night Festival",
            False,
            "Annual light art installations and performances",
            "Bras Basah.Bugis",
            "Singapore",
            "2025-07-12",
        ),
        (
            "Jazz by the Bay",
            False,
            "Outdoor jazz concert featuring local musicians",
            "Marina Bay Sands Event Plaza",
            "Singapore",
            "2025-07-12",
        ),
        (
            "Singapore Botanic Gardens Concert",
            False,
            "Classical music in the gardens",
            "Singapore Botanic Gardens",
            "Singapore",
            "2025-07-12",
        ),
        # July 13
        (
            "ArtScience Museum Exhibition",
            True,
            "Interactive digital art installation",
            "ArtScience Museum",
            "Singapore",
            "2025-07-13",
        ),
        (
            "Gardens by the Bay Light Show",
            False,
            "Spectacular light and sound show at the Supertree Grove",
            "Gardens by the Bay",
            "Singapore",
            "2025-07-13",
        ),
        (
            "Esplanade Free Concert",
            True,
            "Local indie bands performing live",
            "Esplanade Outdoor Theatre",
            "Singapore",
            "2025-07-13",
        ),
        # July 14
        (
            "Singapore Food Festival",
            False,
            "Celebration of local cuisine with top chefs",
            "Sentosa Island",
            "Singapore",
            "2025-07-14",
        ),
        (
            "National Gallery Exhibition",
            True,
            "Southeast Asian modern art showcase",
            "National Gallery Singapore",
            "Singapore",
            "2025-07-14",
        ),
        # July 15
        (
            "Marina Bay Carnival",
            False,
            "Rides, games, and food stalls",
            "Marina Bay",
            "Singapore",
            "2025-07-15",
        ),
        (
            "Esplanade Theatre Performance",
            True,
            "Award-winning international theatre production",
            "Esplanade Theatre",
            "Singapore",
            "2025-07-15",
        ),
        # July 16
        (
            "Singapore Sports Hub Event",
            True,
            "International basketball championship",
            "Singapore Indoor Stadium",
            "Singapore",
            "2025-07-16",
        ),
        (
            "Night Safari Special Tour",
            False,
            "Extended night wildlife experience",
            "Night Safari",
            "Singapore",
            "2025-07-16",
        ),
        # July 17
        (
            "Singapore Symphony Orchestra",
            True,
            "Classical music performance",
            "Victoria Theatre and Concert Hall",
            "Singapore",
            "2025-07-17",
        ),
        (
            "Sentosa Beach Party",
            False,
            "DJs and dancing on the beach",
            "Siloso Beach",
            "Singapore",
            "2025-07-17",
        ),
        # July 18
        (
            "Singapore Film Festival",
            True,
            "Screening of award-winning local films",
            "The Projector",
            "Singapore",
            "2025-07-18",
        ),
        (
            "Singapore Flyer Night Experience",
            True,
            "Special evening rides with champagne",
            "Singapore Flyer",
            "Singapore",
            "2025-07-18",
        ),
        # July 19
        (
            "Clarke Quay River Festival",
            False,
            "Riverside celebration with performances and food",
            "Clarke Quay",
            "Singapore",
            "2025-07-19",
        ),
        (
            "Science Centre Exhibition",
            True,
            "Interactive technology showcase",
            "Science Centre Singapore",
            "Singapore",
            "2025-07-19",
        ),
        # July 20
        (
            "Singapore Zoo Family Day",
            False,
            "Special animal presentations and activities",
            "Singapore Zoo",
            "Singapore",
            "2025-07-20",
        ),
        (
            "Universal Studios Special Event",
            False,
            "Extended hours and special performances",
            "Universal Studios Singapore",
            "Singapore",
            "2025-07-20",
        ),
    ]

    c.executemany(
        "INSERT OR IGNORE INTO events (name, indoor, description, location, city, date) VALUES (?,?,?,?,?,?)",
        events,
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    events_database()
    employees_database()
    print("All databases created successfully")
