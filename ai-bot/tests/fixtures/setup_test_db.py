"""
Create comprehensive mock Campfire database for testing and initial deployment.

This database serves dual purpose:
1. Test database for TDD (local development)
2. Initial "production" database (since real Campfire has no data yet)

Based on Campfire schema from DESIGN.md
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def create_test_database(db_path: str = "./tests/fixtures/test.db"):
    """Create mock Campfire database with realistic test data"""

    # Remove existing database
    Path(db_path).unlink(missing_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Creating test database at {db_path}...")

    # Create tables (based on Campfire schema)

    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email_address TEXT,
            role INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Rooms table
    cursor.execute('''
        CREATE TABLE rooms (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT NOT NULL,
            creator_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Messages table
    cursor.execute('''
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY,
            room_id INTEGER NOT NULL,
            creator_id INTEGER NOT NULL,
            client_message_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
    ''')

    # Action Text Rich Texts table (stores message bodies)
    cursor.execute('''
        CREATE TABLE action_text_rich_texts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            body TEXT,
            record_type TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Memberships table (user-room relationships)
    cursor.execute('''
        CREATE TABLE memberships (
            id INTEGER PRIMARY KEY,
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            unread_at TEXT,
            involvement TEXT DEFAULT 'mentions',
            connections INTEGER DEFAULT 0,
            connected_at TEXT,
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Message search index (FTS5 - optional for now)
    try:
        cursor.execute('''
            CREATE VIRTUAL TABLE message_search_index
            USING fts5(body, tokenize=porter)
        ''')
    except:
        # FTS5 might not be available, skip
        pass

    # Insert test users
    now = datetime.now().isoformat()

    users = [
        (1, 'WU HENG', 'heng.woo@gmail.com', 0, 1, now, now),
        (2, 'John Smith', 'john@smartice.ai', 0, 1, now, now),
        (3, 'Sarah Chen', 'sarah@smartice.ai', 0, 1, now, now),
        (4, '财务分析师', None, 1, 1, now, now),  # Bot user (role=1)
    ]

    cursor.executemany('''
        INSERT INTO users (id, name, email_address, role, active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', users)

    print(f"✅ Created {len(users)} users")

    # Insert test rooms
    rooms = [
        (1, 'All Talk', 'Rooms::Open', 1, now, now),
        (2, 'Finance Team', 'Rooms::Closed', 1, now, now),
        (3, 'Engineering', 'Rooms::Closed', 2, now, now),
        (4, None, 'Rooms::Direct', 1, now, now),  # Direct message room
    ]

    cursor.executemany('''
        INSERT INTO rooms (id, name, type, creator_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', rooms)

    print(f"✅ Created {len(rooms)} rooms")

    # Insert memberships (who's in which rooms)
    memberships = [
        # All Talk room - everyone
        (1, 1, 1, now, now),
        (2, 1, 2, now, now),
        (3, 1, 3, now, now),
        (4, 1, 4, now, now),  # Bot in All Talk
        # Finance Team - WU HENG, Sarah, Bot
        (5, 2, 1, now, now),
        (6, 2, 3, now, now),
        (7, 2, 4, now, now),  # Bot in Finance
        # Engineering - John, Sarah
        (8, 3, 2, now, now),
        (9, 3, 3, now, now),
        # Direct Message - WU HENG and Bot
        (10, 4, 1, now, now),
        (11, 4, 4, now, now),
    ]

    cursor.executemany('''
        INSERT INTO memberships (id, room_id, user_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    ''', memberships)

    print(f"✅ Created {len(memberships)} memberships")

    # Insert test messages with realistic conversation
    base_time = datetime.now() - timedelta(days=2)

    messages_data = [
        # All Talk room (room_id=1)
        (1, 1, 1, 'msg-001', (base_time + timedelta(hours=0)).isoformat()),
        (2, 1, 2, 'msg-002', (base_time + timedelta(hours=1)).isoformat()),
        (3, 1, 3, 'msg-003', (base_time + timedelta(hours=2)).isoformat()),
        (4, 1, 1, 'msg-004', (base_time + timedelta(hours=3)).isoformat()),

        # Finance Team room (room_id=2) - Revenue discussion
        (5, 2, 1, 'msg-005', (base_time + timedelta(hours=10)).isoformat()),
        (6, 2, 3, 'msg-006', (base_time + timedelta(hours=10, minutes=15)).isoformat()),
        (7, 2, 1, 'msg-007', (base_time + timedelta(hours=10, minutes=30)).isoformat()),
        (8, 2, 3, 'msg-008', (base_time + timedelta(hours=11)).isoformat()),
        (9, 2, 1, 'msg-009', (base_time + timedelta(hours=12)).isoformat()),

        # Engineering room (room_id=3)
        (10, 3, 2, 'msg-010', (base_time + timedelta(hours=20)).isoformat()),
        (11, 3, 3, 'msg-011', (base_time + timedelta(hours=21)).isoformat()),

        # Direct Message (room_id=4)
        (12, 4, 1, 'msg-012', (base_time + timedelta(hours=24)).isoformat()),
    ]

    for msg_id, room_id, creator_id, client_msg_id, created_at in messages_data:
        cursor.execute('''
            INSERT INTO messages (id, room_id, creator_id, client_message_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (msg_id, room_id, creator_id, client_msg_id, created_at, created_at))

    print(f"✅ Created {len(messages_data)} messages")

    # Insert message bodies (action_text_rich_texts)
    message_bodies = [
        # All Talk
        (1, 'body', '<p>Welcome to Campfire! Let\'s get started with our team chat.</p>', 'Message', 1),
        (2, 'body', '<p>Thanks! Excited to be here. What projects are we working on?</p>', 'Message', 2),
        (3, 'body', '<p>Currently focused on Q3 financial analysis and product development.</p>', 'Message', 3),
        (4, 'body', '<p>Great! I\'ll be looking at the Q3 revenue trends this week.</p>', 'Message', 4),

        # Finance Team - Detailed revenue discussion
        (5, 'body', '<p>Team, we need to analyze Q3 revenue performance. The preliminary numbers show 12% growth YoY.</p>', 'Message', 5),
        (6, 'body', '<p>That\'s impressive! What are the main drivers? Is it across all regions?</p>', 'Message', 6),
        (7, 'body', '<p>Primary growth from Enterprise sales (+18%) and APAC region (+25%). Consumer segment up 8%.</p>', 'Message', 7),
        (8, 'body', '<p>Excellent. What about profit margins? Are we maintaining our 32% target?</p>', 'Message', 8),
        (9, 'body', '<p>Actually exceeded - margins improved to 35% due to cost optimization initiatives. Very positive quarter overall.</p>', 'Message', 9),

        # Engineering
        (10, 'body', '<p>Deployment scheduled for Friday 3pm. All tests passing.</p>', 'Message', 10),
        (11, 'body', '<p>Perfect timing. I\'ll monitor the rollout.</p>', 'Message', 11),

        # Direct Message
        (12, 'body', '<p>@财务分析师 Can you help me understand the Q3 revenue trends?</p>', 'Message', 12),
    ]

    for body_id, name, body_html, record_type, record_id in message_bodies:
        timestamp = messages_data[body_id - 1][4]  # Use same timestamp as message
        cursor.execute('''
            INSERT INTO action_text_rich_texts (id, name, body, record_type, record_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (body_id, name, body_html, record_type, record_id, timestamp, timestamp))

    print(f"✅ Created {len(message_bodies)} message bodies")

    # Commit and close
    conn.commit()
    conn.close()

    print(f"\n✅ Test database created successfully at {db_path}")
    print(f"   - {len(users)} users (including bot)")
    print(f"   - {len(rooms)} rooms")
    print(f"   - {len(messages_data)} messages")
    print(f"   - Rich conversation history in Finance Team room")
    print(f"\nDatabase ready for testing!\n")

    return db_path


if __name__ == '__main__':
    create_test_database()
