import flet as ft
import db_operations as db

def main(page: ft.Page):
    page.title = "SAP EWM & Advanced Inventory Analytics Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30

    material_input = ft.TextField(label="Material ID (e.g., MAT-1002)", width=300)
    qty_input = ft.TextField(label="Quantity", width=150)
    
    # Status text box to display operational messages directly on screen
    status_text = ft.Text("System ready. Perform inbound or outbound transaction.", size=14, weight=ft.FontWeight.BOLD, color="blue")

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Material ID")),
            ft.DataColumn(ft.Text("Description")),
            ft.DataColumn(ft.Text("Stock")),
            ft.DataColumn(ft.Text("Reorder")),
            ft.DataColumn(ft.Text("Cost (€)")),
            ft.DataColumn(ft.Text("ABC")),
            ft.DataColumn(ft.Text("XYZ")),
        ],
        rows=[]
    )

    def load_data():
        table.rows.clear()
        for row in db.get_all_inventory():
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(str(row[1]))),
                        ft.DataCell(ft.Text(str(row[2]))),
                        ft.DataCell(ft.Text(str(row[3]))),
                        ft.DataCell(ft.Text(f"€{row[4]:.2f}")),
                        ft.DataCell(ft.Text(str(row[5]), weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(row[6]), weight=ft.FontWeight.BOLD)),
                    ]
                )
            )
        page.update()

    def handle_inbound(e):
        if material_input.value and qty_input.value:
            mat_id = material_input.value.strip().upper()
            qty = int(qty_input.value)
            db.goods_receipt(mat_id, qty)
            material_input.value = ""
            qty_input.value = ""
            load_data()
            
            status_text.value = f"Success: Goods Receipt processed for {mat_id}. Stock replenished."
            status_text.color = "green"
            page.update()

    def handle_outbound(e):
        if material_input.value and qty_input.value:
            mat_id = material_input.value.strip().upper()
            qty = int(qty_input.value)
            
            db.goods_issue(mat_id, qty)
            material_input.value = ""
            qty_input.value = ""
            load_data()
            
            # Check reorder status and display clear on-screen warning
            if db.check_reorder_level(mat_id):
                status_text.value = f"CRITICAL WARNING: Material {mat_id} breached JIT threshold! Restock required."
                status_text.color = "red"
            else:
                status_text.value = f"Success: Goods Issue processed for {mat_id}. Stock levels optimal."
                status_text.color = "blue"
                
            page.update()

    inbound_btn = ft.ElevatedButton("Goods Receipt (Inbound)", on_click=handle_inbound, color="green")
    outbound_btn = ft.ElevatedButton("Goods Issue (Outbound)", on_click=handle_outbound, color="red")

    page.add(
        ft.Text("SAP EWM - Advanced Material & ABC/XYZ Analytics", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([material_input, qty_input]),
        ft.Row([inbound_btn, outbound_btn]),
        status_text,  # Permanently visible status display right on screen
        ft.Divider(),
        table
    )
    
    load_data()

ft.app(target=main)
