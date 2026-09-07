import flet as ft
import db_operations as db

def main(page: ft.Page):
    page.title = "SAP EWM & Advanced Inventory Analytics Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30

    material_input = ft.TextField(label="Material ID (e.g., MAT-1001)", width=300)
    qty_input = ft.TextField(label="Quantity", width=150)
    
    # Expanded table columns to include analytical classifications
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
            db.goods_receipt(material_input.value, int(qty_input.value))
            material_input.value = ""
            qty_input.value = ""
            load_data()
            page.snack_bar = ft.SnackBar(ft.Text("Goods Receipt successful! Stock updated."), bgcolor="green")
            page.snack_bar.open = True
            page.update()

    def handle_outbound(e):
        if material_input.value and qty_input.value:
            mat_id = material_input.value
            db.goods_issue(mat_id, int(qty_input.value))
            material_input.value = ""
            qty_input.value = ""
            load_data()
            
            if db.check_reorder_level(mat_id):
                page.snack_bar = ft.SnackBar(ft.Text(f"WARNING: JIT Reorder threshold reached for {mat_id}! Restock immediately."), bgcolor="red")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Goods Issue successful!"), bgcolor="blue")
                
            page.snack_bar.open = True
            page.update()

    inbound_btn = ft.ElevatedButton("Goods Receipt (Inbound)", on_click=handle_inbound, color="green")
    outbound_btn = ft.ElevatedButton("Goods Issue (Outbound)", on_click=handle_outbound, color="red")

    page.add(
        ft.Text("SAP EWM - Advanced Material & ABC/XYZ Analytics", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([material_input, qty_input]),
        ft.Row([inbound_btn, outbound_btn]),
        ft.Divider(),
        table
    )
    
    load_data()

ft.app(target=main)