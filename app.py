import flet as ft
import db_operations as db
from datetime import datetime

def main(page: ft.Page):
    page.title = "SAP EWM & Advanced Inventory Analytics Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.bgcolor = "#f4f6f9"

    # Professional App Bar featuring system ownership metadata
    page.appbar = ft.AppBar(
        leading=ft.Icon("warehouse", color="white"),
        leading_width=40,
        title=ft.Row([
            ft.Text("SAP EWM Enterprise Control Center", color="white", weight=ft.FontWeight.BOLD),
            ft.VerticalDivider(width=20),
            ft.Text("Lead Architect: Adil Rafique", color="#b0c4de", size=13, italic=True)
        ]),
        bgcolor="#1f4e78",
    )

    material_input = ft.TextField(label="Material ID (e.g., MAT-1002)", width=250, bgcolor="white")
    qty_input = ft.TextField(label="Quantity", width=120, bgcolor="white")
    
    status_text = ft.Text("System ready. Perform inbound or outbound transaction.", size=13, weight=ft.FontWeight.BOLD, color="blue")
    
    capital_kpi = ft.Text("€0.00", size=18, weight=ft.FontWeight.BOLD, color="#1f4e78")
    sku_kpi = ft.Text("0", size=18, weight=ft.FontWeight.BOLD, color="#1f4e78")
    alert_kpi = ft.Text("0", size=18, weight=ft.FontWeight.BOLD, color="red")

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

    audit_log_list = ft.ListView(expand=1, spacing=5, padding=10, auto_scroll=True)

    class_a_bar = ft.ProgressBar(value=0.0, width=400, color="red", bgcolor="#eeeeee")
    class_b_bar = ft.ProgressBar(value=0.0, width=400, color="orange", bgcolor="#eeeeee")
    class_c_bar = ft.ProgressBar(value=0.0, width=400, color="green", bgcolor="#eeeeee")
    
    class_a_text = ft.Text("Class A (High Value / Strict Control): €0.00", weight=ft.FontWeight.BOLD)
    class_b_text = ft.Text("Class B (Medium Value / Moderate Control): €0.00", weight=ft.FontWeight.BOLD)
    class_c_text = ft.Text("Class C (Low Value / Automated Control): €0.00", weight=ft.FontWeight.BOLD)

    def log_audit(action_type, details):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = ft.Text(f"[{timestamp}] {action_type}: {details}", size=12, font_family="monospace")
        audit_log_list.controls.insert(0, log_entry)

    def load_data():
        table.rows.clear()
        total_inventory_value = 0.0
        total_skus = 0
        critical_alerts = 0
        abc_totals = {"A": 0.0, "B": 0.0, "C": 0.0}
        
        for row in db.get_all_inventory():
            total_skus += 1
            stock = row[2]
            reorder = row[3]
            cost = row[4]
            abc_class = row[5]
            item_total_value = stock * cost
            total_inventory_value += item_total_value
            
            if abc_class in abc_totals:
                abc_totals[abc_class] += item_total_value
            
            if stock <= reorder:
                critical_alerts += 1
                status_badge = ft.Container(
                    content=ft.Text("⚠️ CRITICAL LOW", color="white", weight=ft.FontWeight.BOLD, size=11),
                    bgcolor="red",
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=ft.border_radius.all(4)
                )
            else:
                status_badge = ft.Container(
                    content=ft.Text("OPTIMAL", color="green", weight=ft.FontWeight.BOLD, size=11),
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
                        ft.DataCell(ft.Text(str(abc_class), weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(row[6]), weight=ft.FontWeight.BOLD)),
                        ft.DataCell(status_badge),
                    ]
                )
            )
        
        capital_kpi.value = f"€{total_inventory_value:,.2f}"
        sku_kpi.value = str(total_skus)
        alert_kpi.value = str(critical_alerts)
        
        if total_inventory_value > 0:
            class_a_bar.value = abc_totals["A"] / total_inventory_value
            class_b_bar.value = abc_totals["B"] / total_inventory_value
            class_c_bar.value = abc_totals["C"] / total_inventory_value
        else:
            class_a_bar.value = class_b_bar.value = class_c_bar.value = 0.0

        class_a_text.value = f"Class A (High Capital Impact): €{abc_totals['A']:,.2f}"
        class_b_text.value = f"Class B (Medium Capital Impact): €{abc_totals['B']:,.2f}"
        class_c_text.value = f"Class C (Low Capital Impact): €{abc_totals['C']:,.2f}"
        
        page.update()

    def handle_inbound(e):
        if material_input.value and qty_input.value:
            mat_id = material_input.value.strip().upper()
            qty = int(qty_input.value)
            db.goods_receipt(mat_id, qty)
            log_audit("INBOUND (GR)", f"Received {qty} units of {mat_id}")
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
            log_audit("OUTBOUND (GI)", f"Issued {qty} units of {mat_id}")
            material_input.value = ""
            qty_input.value = ""
            load_data()
            if db.check_reorder_level(mat_id):
                status_text.value = f"CRITICAL WARNING: Material {mat_id} breached JIT threshold! Restock required."
                status_text.color = "red"
                log_audit("JIT ALERT", f"Material {mat_id} breached reorder threshold!")
            else:
                status_text.value = f"Success: Goods Issue processed for {mat_id}. Stock levels optimal."
                status_text.color = "blue"
            page.update()

    inbound_btn = ft.ElevatedButton("Goods Receipt (Inbound)", on_click=handle_inbound, color="white", bgcolor="green")
    outbound_btn = ft.ElevatedButton("Goods Issue (Outbound)", on_click=handle_outbound, color="white", bgcolor="red")

    kpi_row = ft.Row([
        ft.Card(content=ft.Container(content=ft.Column([
            ft.Text("Total Inventory Capital", size=12, color="grey", weight=ft.FontWeight.BOLD),
            capital_kpi
        ]), padding=15), expand=True, elevation=2),
        ft.Card(content=ft.Container(content=ft.Column([
            ft.Text("Active Master SKUs", size=12, color="grey", weight=ft.FontWeight.BOLD),
            sku_kpi
        ]), padding=15), expand=True, elevation=2),
        ft.Card(content=ft.Container(content=ft.Column([
            ft.Text("Critical Stock Alerts", size=12, color="grey", weight=ft.FontWeight.BOLD),
            alert_kpi
        ]), padding=15), expand=True, elevation=2),
    ], spacing=15)

    dashboard_tab = ft.Tab(
        text="Operations & Master Grid",
        icon="dashboard",
        content=ft.Column([
            kpi_row,
            ft.Card(content=ft.Container(content=ft.Column([
                ft.Text("Warehouse Transaction Operations", size=15, weight=ft.FontWeight.BOLD),
                ft.Row([material_input, qty_input]),
                ft.Row([inbound_btn, outbound_btn]),
                status_text
            ], tight=True, spacing=10), padding=15), elevation=2),
            ft.Card(content=ft.Container(content=ft.Column([
                ft.Text("Material Master & Analytics Inventory Grid", size=15, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                table
            ]), padding=15), elevation=2),
            ft.Card(content=ft.Container(content=ft.Column([
                ft.Text("Real-Time Warehouse Audit & Transaction Log", size=15, weight=ft.FontWeight.BOLD),
                ft.Text("Tracks historical movement telemetry for compliance and audit logging.", size=11, color="grey"),
                ft.Divider(),
                ft.Container(content=audit_log_list, height=120, bgcolor="#fafafa", padding=5, border_radius=4)
            ]), padding=15), elevation=2),
            
            # Professional Footer Metadata Signature
            ft.Container(
                content=ft.Row([
                    ft.Text("SAP EWM Simulation Engine v2.4", size=11, color="grey"),
                    ft.Text("Developed by Adil Rafique", size=11, weight=ft.FontWeight.BOLD, color="#1f4e78")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.symmetric(horizontal=10, vertical=5)
            )
        ], scroll=ft.ScrollMode.AUTO, spacing=15)
    )

    analytics_tab = ft.Tab(
        text="ABC Capital Analytics & Graphs",
        icon="analytics",
        content=ft.Column([
            ft.Card(content=ft.Container(content=ft.Column([
                ft.Text("Inventory Capital Distribution by ABC Classification", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Visualizing capital allocation across Pareto inventory tiers (SAP MM standard).", size=12, color="grey"),
                ft.Divider(),
                class_a_text,
                class_a_bar,
                ft.Container(height=10),
                class_b_text,
                class_b_bar,
                ft.Container(height=10),
                class_c_text,
                class_c_bar,
            ], spacing=15), padding=20), elevation=2),
            
            # Analytics Tab Footer Signature
            ft.Container(
                content=ft.Row([
                    ft.Text("SAP EWM Simulation Engine v2.4", size=11, color="grey"),
                    ft.Text("Developed by Adil Rafique", size=11, weight=ft.FontWeight.BOLD, color="#1f4e78")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.symmetric(horizontal=10, vertical=5)
            )
        ], scroll=ft.ScrollMode.AUTO, spacing=15)
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[dashboard_tab, analytics_tab],
        expand=True
    )

    page.add(tabs)
    log_audit("SYSTEM", "SAP EWM Enterprise Control Center initialized successfully.")
    load_data()

ft.app(target=main)
