import flet as ft
import db_operations as db

def main(page: ft.Page):
    page.title = "SAP EWM & Advanced Inventory Analytics Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30

    material_input = ft.TextField(label="Material ID (e.g., MAT-1002)", width=300)
    qty_input = ft.TextField(label="Quantity", width=150)
    
    status_text = ft.Text("System ready. Perform inbound or outbound transaction.", size=14, weight=ft.FontWeight.BOLD, color="blue")
    
    # KPI Card for Total Stock Capital Valuation
    capital_kpi = ft.Text("Total Stock Capital: €0.00", size=18, weight=ft.FontWeight.BOLD, color="#1f4e78")

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Material ID")),
            ft.DataColumn(ft.Text("Description")),
            ft.DataColumn(ft.Text("Stock")),
            ft.DataColumn(ft.Text("Reorder")),
            ft.DataColumn(ft.Text("Cost (€)")),
            ft.DataColumn(ft.Text("Total Value (€)")),
            ft.DataColumn(ft.Text("ABC")),
            ft.DataColumn(ft.Text("XYZ")),
            ft.DataColumn(ft.Text("Stock Status")),
        ],
        rows=[]
    )

    def load_data():
        table.rows.clear()
        total_inventory_value = 0.0
        
        for row in db.get_all_inventory():
            stock = row[2]
            reorder = row[3]
            cost = row[4]
            item_total_value = stock * cost
            total_inventory_value += item_total_value
            
            # High-visibility status badge
            if stock <= reorder:
                status_badge = ft.Container(
                    content=ft.Text("⚠️ CRITICAL LOW", color="white", weight=ft.FontWeight.BOLD, size=12),
                    bgcolor="red",
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=ft.border_radius.all(4)
                )
            else:
                status_badge = ft.Container(
                    content=ft.Text("OPTIMAL", color="green", weight=ft.FontWeight.BOLD, size=12),
                    bgcolor="#e6f4ea",
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=ft.border_radius.all(4)
                )

            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(str(row[1]))),
                        ft.DataCell(ft.Text(str(stock), color="red" if stock <= reorder else "black", weight=ft.FontWeight.BOLD if stock <= reorder else ft.FontWeight.NORMAL)),
                        ft.DataCell(ft.Text(str(reorder))),
                        ft.DataCell(ft.Text(f"€{cost:.2f}")),
                        ft.DataCell(ft.Text(f"€{item_total_value:,.2f}", weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(row[5]), weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(row[6]), weight=ft.FontWeight.BOLD)),
                        ft.DataCell(status_badge),
                    ]
                )
            )
        
        # Update the top KPI display with the total sum
        capital_kpi.value = f"Total Capital Bound in Inventory: €{total_inventory_value:,.2f}"
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
        capital_kpi,  # Prominent executive KPI card at the top
        ft.Row([material_input, qty_input]),
        ft.Row([inbound_btn, outbound_btn]),
        status_text,
        ft.Divider(),
        table
    )
    
    load_data()

ft.app(target=main)
