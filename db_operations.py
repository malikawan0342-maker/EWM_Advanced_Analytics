import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'ewm_inventory.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_all_inventory():
    conn = get_connection()
    cursor = conn.cursor()
    # Fetches all 8 columns now
    cursor.execute("SELECT Material_ID, Description, Current_Stock, Reorder_Point, Unit_Cost, ABC_Class, XYZ_Class FROM Inventory")
    rows = cursor.fetchall()
    conn.close()
    return rows

def goods_receipt(material_id, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Inventory 
        SET Current_Stock = Current_Stock + ? 
        WHERE Material_ID = ?
    ''', (quantity, material_id))
    conn.commit()
    conn.close()

def goods_issue(material_id, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Inventory 
        SET Current_Stock = Current_Stock - ? 
        WHERE Material_ID = ?
    ''', (quantity, material_id))
    conn.commit()
    conn.close()

def check_reorder_level(material_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Current_Stock, Reorder_Point FROM Inventory WHERE Material_ID = ?", (material_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        current_stock, reorder_point = result
        if current_stock <= reorder_point:
            return True
            
    return False