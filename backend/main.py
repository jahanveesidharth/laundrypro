"""
LaundryPro - AI-First Laundry Order Management System
Backend: FastAPI + SQLite
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, timedelta
import sqlite3
import uuid
import re
import os

# ── App Setup ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="LaundryPro API",
    description="AI-First Laundry Order Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Database ───────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "laundry.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS orders (
            id          TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            phone       TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'RECEIVED',
            total_bill  REAL NOT NULL DEFAULT 0,
            estimated_delivery TEXT,
            notes       TEXT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    TEXT NOT NULL,
            garment     TEXT NOT NULL,
            quantity    INTEGER NOT NULL,
            price_per_item REAL NOT NULL,
            subtotal    REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS status_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    TEXT NOT NULL,
            from_status TEXT,
            to_status   TEXT NOT NULL,
            changed_at  TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
    """)
    conn.commit()
    conn.close()

init_db()

# ── Pricing Config ─────────────────────────────────────────────────────────────
GARMENT_PRICES = {
    "Shirt":        40,
    "T-Shirt":      35,
    "Pants":        50,
    "Jeans":        60,
    "Saree":        120,
    "Suit":         200,
    "Jacket":       150,
    "Kurta":        60,
    "Dress":        100,
    "Blanket":      180,
    "Bedsheet":     80,
    "Curtain":      90,
    "Sweater":      70,
    "Blazer":       140,
    "Lehenga":      200,
    "Dupatta":      40,
    "Salwar Kameez":90,
    "Coat":         160,
    "Tie":          30,
    "Skirt":        70,
    "Shorts":       40,
    "Scarf":        30,
    "Bath Towel":   50,
    "Pillow Cover": 20,
    "Trackpants":   50,
    "Undergarment": 20,
    "Socks":        10,
    "Hand Towel":   20,
    "Cap":          30,
    "Hoodie":       80,
    "Cardigan":     70,
    "Shawl":        60,
    "Gloves":       25,
    "Table Cloth":  40,
    "Nightgown":    60,
    "Pajamas":      50,
    "Uniform":      90,
    "Apron":        30,
    "Vest":         40,
}

STATUS_FLOW = ["RECEIVED", "PROCESSING", "READY", "DELIVERED"]

def estimate_delivery(status: str) -> str:
    days = {"RECEIVED": 3, "PROCESSING": 2, "READY": 0, "DELIVERED": 0}
    d = days.get(status, 2)
    return (datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d")

# ── Pydantic Models ────────────────────────────────────────────────────────────
class GarmentItem(BaseModel):
    garment: str
    quantity: int
    price_per_item: Optional[float] = None  # auto-filled if not given

    @field_validator("quantity")
    def qty_positive(cls, v):
        if v < 1:
            raise ValueError("Quantity must be ≥ 1")
        return v

class CreateOrderRequest(BaseModel):
    customer_name: str
    phone: str
    garments: List[GarmentItem]
    notes: Optional[str] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        digits = re.sub(r"\D", "", v)
        if len(digits) < 10:
            raise ValueError("Phone must have at least 10 digits")
        return v

    @field_validator("garments")
    def at_least_one(cls, v):
        if len(v) == 0:
            raise ValueError("At least one garment required")
        return v

class UpdateStatusRequest(BaseModel):
    status: str

    @field_validator("status")
    def valid_status(cls, v):
        v = v.upper()
        if v not in STATUS_FLOW:
            raise ValueError(f"Status must be one of {STATUS_FLOW}")
        return v

class BulkUpdateStatusRequest(BaseModel):
    order_ids: List[str]
    status: str

    @field_validator("status")
    def valid_status(cls, v):
        v = v.upper()
        if v not in STATUS_FLOW:
            raise ValueError(f"Status must be one of {STATUS_FLOW}")
        return v

# ── Helpers ────────────────────────────────────────────────────────────────────
def order_to_dict(row, items, history=None):
    d = dict(row)
    d["items"] = [dict(i) for i in items]
    if history is not None:
        d["status_history"] = [dict(h) for h in history]
    return d

def generate_order_id():
    ts = datetime.now().strftime("%y%m%d")
    uid = str(uuid.uuid4()).upper()[:6]
    return f"ORD-{ts}-{uid}"

# ── API Routes ─────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root():
    frontend = os.path.join(os.path.dirname(__file__), "..", "frontend", "templates", "index.html")
    return FileResponse(os.path.abspath(frontend))

@app.get("/api/prices", tags=["Config"])
def get_prices():
    """Get all garment types and their default prices."""
    return {"prices": GARMENT_PRICES}

# ── Create Order ───────────────────────────────────────────────────────────────
@app.post("/api/orders", status_code=201, tags=["Orders"])
def create_order(req: CreateOrderRequest, db: sqlite3.Connection = Depends(get_db)):
    order_id = generate_order_id()
    now = datetime.now().isoformat()
    total = 0.0
    items_data = []

    for g in req.garments:
        price = g.price_per_item if g.price_per_item else GARMENT_PRICES.get(g.garment, 50)
        subtotal = price * g.quantity
        total += subtotal
        items_data.append((order_id, g.garment, g.quantity, price, subtotal))

    est = estimate_delivery("RECEIVED")

    db.execute(
        "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)",
        (order_id, req.customer_name, req.phone, "RECEIVED", round(total, 2), est, req.notes, now, now)
    )
    db.executemany(
        "INSERT INTO order_items (order_id, garment, quantity, price_per_item, subtotal) VALUES (?,?,?,?,?)",
        items_data
    )
    db.execute(
        "INSERT INTO status_history (order_id, from_status, to_status, changed_at) VALUES (?,?,?,?)",
        (order_id, None, "RECEIVED", now)
    )
    db.commit()

    return {
        "success": True,
        "order_id": order_id,
        "total_bill": round(total, 2),
        "estimated_delivery": est,
        "message": f"Order {order_id} created successfully!"
    }

# ── List / Filter Orders ───────────────────────────────────────────────────────
@app.get("/api/orders", tags=["Orders"])
def list_orders(
    status: Optional[str] = Query(None),
    customer_name: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    garment: Optional[str] = Query(None),
    db: sqlite3.Connection = Depends(get_db)
):
    query = "SELECT DISTINCT o.* FROM orders o"
    joins = ""
    conditions = []
    params = []

    if garment:
        joins += " JOIN order_items oi ON o.id = oi.order_id"
        conditions.append("LOWER(oi.garment) LIKE ?")
        params.append(f"%{garment.lower()}%")

    if status:
        conditions.append("UPPER(o.status) = ?")
        params.append(status.upper())
    if customer_name:
        conditions.append("LOWER(o.customer_name) LIKE ?")
        params.append(f"%{customer_name.lower()}%")
    if phone:
        conditions.append("o.phone LIKE ?")
        params.append(f"%{phone}%")

    full_query = query + joins
    if conditions:
        full_query += " WHERE " + " AND ".join(conditions)
    full_query += " ORDER BY o.created_at DESC"

    rows = db.execute(full_query, params).fetchall()
    result = []
    for row in rows:
        items = db.execute("SELECT * FROM order_items WHERE order_id=?", (row["id"],)).fetchall()
        result.append(order_to_dict(row, items))

    return {"orders": result, "count": len(result)}

# ── Bulk Update Status ─────────────────────────────────────────────────────────
@app.patch("/api/orders/bulk-status", tags=["Orders"])
def bulk_update_status(req: BulkUpdateStatusRequest, db: sqlite3.Connection = Depends(get_db)):
    new_status = req.status
    now = datetime.now().isoformat()
    est = estimate_delivery(new_status)
    
    if not req.order_ids:
        return {"success": True, "updated_count": 0, "message": "No orders provided"}

    placeholders = ",".join("?" for _ in req.order_ids)
    rows = db.execute(f"SELECT id, status FROM orders WHERE id IN ({placeholders})", req.order_ids).fetchall()
    
    found_ids = [r["id"] for r in rows]
    missing = set(req.order_ids) - set(found_ids)
    if missing:
        raise HTTPException(404, f"Orders not found: {missing}")

    history_data = []
    for r in rows:
        history_data.append((r["id"], r["status"], new_status, now))

    db.execute(
        f"UPDATE orders SET status=?, estimated_delivery=?, updated_at=? WHERE id IN ({placeholders})",
        (new_status, est, now, *req.order_ids)
    )
    db.executemany(
        "INSERT INTO status_history (order_id, from_status, to_status, changed_at) VALUES (?,?,?,?)",
        history_data
    )
    db.commit()
    return {
        "success": True,
        "updated_count": len(req.order_ids),
        "new_status": new_status,
        "message": f"{len(req.order_ids)} orders updated to {new_status}"
    }

# ── Get Single Order ───────────────────────────────────────────────────────────
@app.get("/api/orders/{order_id}", tags=["Orders"])
def get_order(order_id: str, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Order {order_id} not found")
    items = db.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,)).fetchall()
    history = db.execute(
        "SELECT * FROM status_history WHERE order_id=? ORDER BY changed_at", (order_id,)
    ).fetchall()
    return order_to_dict(row, items, history)

# ── Update Status ──────────────────────────────────────────────────────────────
@app.patch("/api/orders/{order_id}/status", tags=["Orders"])
def update_status(order_id: str, req: UpdateStatusRequest, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Order {order_id} not found")

    old_status = row["status"]
    new_status = req.status
    now = datetime.now().isoformat()
    est = estimate_delivery(new_status)

    db.execute(
        "UPDATE orders SET status=?, estimated_delivery=?, updated_at=? WHERE id=?",
        (new_status, est, now, order_id)
    )
    db.execute(
        "INSERT INTO status_history (order_id, from_status, to_status, changed_at) VALUES (?,?,?,?)",
        (order_id, old_status, new_status, now)
    )
    db.commit()
    return {
        "success": True,
        "order_id": order_id,
        "old_status": old_status,
        "new_status": new_status,
        "estimated_delivery": est,
        "message": f"Status updated to {new_status}"
    }

# ── Delete Order ───────────────────────────────────────────────────────────────
@app.delete("/api/orders/{order_id}", tags=["Orders"])
def delete_order(order_id: str, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT id FROM orders WHERE id=?", (order_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Order {order_id} not found")
    db.execute("DELETE FROM orders WHERE id=?", (order_id,))
    db.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
    db.execute("DELETE FROM status_history WHERE order_id=?", (order_id,))
    db.commit()
    return {"success": True, "message": f"Order {order_id} deleted"}

# ── Dashboard ──────────────────────────────────────────────────────────────────
@app.get("/api/dashboard", tags=["Dashboard"])
def dashboard(db: sqlite3.Connection = Depends(get_db)):
    total_orders = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total_revenue = db.execute("SELECT COALESCE(SUM(total_bill),0) FROM orders").fetchone()[0]
    delivered_rev = db.execute(
        "SELECT COALESCE(SUM(total_bill),0) FROM orders WHERE status='DELIVERED'"
    ).fetchone()[0]

    status_counts = {}
    for s in STATUS_FLOW:
        cnt = db.execute("SELECT COUNT(*) FROM orders WHERE status=?", (s,)).fetchone()[0]
        status_counts[s] = cnt

    popular = db.execute("""
        SELECT garment, SUM(quantity) as total_qty, COUNT(*) as order_count
        FROM order_items GROUP BY garment ORDER BY total_qty DESC LIMIT 5
    """).fetchall()

    today = datetime.now().strftime("%Y-%m-%d")
    today_orders = db.execute(
        "SELECT COUNT(*) FROM orders WHERE created_at LIKE ?", (f"{today}%",)
    ).fetchone()[0]
    today_revenue = db.execute(
        "SELECT COALESCE(SUM(total_bill),0) FROM orders WHERE created_at LIKE ?", (f"{today}%",)
    ).fetchone()[0]

    recent = db.execute(
        "SELECT id, customer_name, phone, status, total_bill, created_at FROM orders ORDER BY created_at DESC LIMIT 5"
    ).fetchall()

    seven_days_ago = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
    trend = db.execute(
        """SELECT substr(created_at, 1, 10) as date, COALESCE(SUM(total_bill), 0) as rev
           FROM orders WHERE created_at >= ? GROUP BY date ORDER BY date""",
        (seven_days_ago,)
    ).fetchall()
    
    trend_dict = {r["date"]: r["rev"] for r in trend}
    revenue_trend = []
    for i in range(7):
        d = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        revenue_trend.append({"date": d, "revenue": trend_dict.get(d, 0)})

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "delivered_revenue": round(delivered_rev, 2),
        "pending_revenue": round(total_revenue - delivered_rev, 2),
        "orders_by_status": status_counts,
        "popular_garments": [dict(r) for r in popular],
        "today": {
            "orders": today_orders,
            "revenue": round(today_revenue, 2)
        },
        "revenue_trend": revenue_trend,
        "recent_orders": [dict(r) for r in recent]
    }

# ── Static Frontend ────────────────────────────────────────────────────────────
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
app.mount("/static", StaticFiles(directory=os.path.abspath(static_dir)), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
