Advanced SAP EWM & ABC/XYZ Inventory Analytics Dashboard

Project Overview
This project is an advanced, custom-built Warehouse Management System (WMS) simulation dashboard engineered to replicate core SAP Extended Warehouse Management (EWM) and Materials Management (MM) workflows alongside analytical inventory classification. It bridges technical data architecture with practical supply chain control.

The application allows users to execute simulated Inbound (Goods Receipts) and Outbound (Goods Issues) while monitoring capital valuation, inventory turnover indicators, and automated reorder triggers in real time.

Core Features & Lean Manufacturing Logic
Advanced Database Schema:Built on a relational SQLite database featuring Material Master Data, unit cost fields, annual consumption values, and classification metrics.
ABC/XYZ Inventory Analysis:Categorizes inventory based on financial impact (ABC analysis for capital binding) and demand predictability/fluctuation patterns (XYZ analysis), mirroring professional ERP analytical practices.
Operational Inbound/Outbound Workflows:Simulates physical supply chain movements with immediate backend SQL execution and UI refreshing.
Just-In-Time (JIT) Threshold Alerts:Automatically monitors stock levels against defined reorder points, firing visual UI warning banners to trigger pull-based replenishment.

Technical Stack
Backend:Python, SQLite3
Frontend:Flet (Python Reactive UI Framework)
Concepts: Relational Database Architecture, Lean Manufacturing, SAP EWM/MM Logic, Inventory Optimization

How to Run
1. Clone or download this repository.
2. Ensure you have Python and the required UI library installed: `pip install flet`
3. Run `database.py` once to set up the SQLite database and seed the analytical data.
4. Run `app.py` to launch the interactive analytics dashboard.

(Note: Keep all files, including `ewm_inventory.db`, in the same root directory so the relative database paths resolve properly).
