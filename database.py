import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'ewm_inventory.db')

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop the old table to upgrade schema with ABC/XYZ metrics
    cursor.execute('DROP TABLE IF EXISTS Inventory')

    cursor.execute('''
        CREATE TABLE Inventory (
            Material_ID TEXT PRIMARY KEY,
            Description TEXT,
            Current_Stock INTEGER,
            Reorder_Point INTEGER,
            Unit_Cost REAL,
            Annual_Consumption INTEGER,
            ABC_Class TEXT,
            XYZ_Class TEXT
        )
    ''')

    # Enhanced dummy data including cost and consumption for classification
    dummy_data = [
        ('MAT-1001', 'Steel Screws (10mm)', 650, 100, 0.50, 12000, 'C', 'X'),
        ('MAT-1002', 'Drive Belt (Type A)', 15, 20, 45.00, 800, 'A', 'Y'),
        ('MAT-1003', 'Copper Wire (Spool)', 120, 50, 120.00, 1500, 'A', 'X'),
        ('MAT-1004', 'Hydraulic Valve', 12, 15, 350.00, 300, 'B', 'Z'),
        ('MAT-1005', 'Electric Motor (5HP)', 4, 5, 850.00, 120, 'A', 'Z')
    ]

    cursor.executemany('''
        INSERT INTO Inventory (Material_ID, Description, Current_Stock, Reorder_Point, Unit_Cost, Annual_Consumption, ABC_Class, XYZ_Class)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', dummy_data)

    conn.commit()
    conn.close()
    print(f"Advanced ABC/XYZ Database created successfully at: {DB_PATH}")

setup_database()