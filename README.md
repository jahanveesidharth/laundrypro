# 🧺 LaundryPro — AI-First Order Management System

> A production-grade dry cleaning management system built with FastAPI + SQLite + Vanilla JS

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/laundrypro.git
cd laundrypro

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Server
```bash
cd backend
python main.py
```

### 3. Open the App
Visit: **http://localhost:8000**

API Docs: **http://localhost:8000/docs** (Swagger UI)

---

## ✨ Features Implemented

### Core Features
| Feature | Status |
|---|---|
| Create Order with garments + auto-pricing | ✅ |
| Unique Order ID generation (e.g. ORD-250615-A3B2C1) | ✅ |
| Order status: RECEIVED → PROCESSING → READY → DELIVERED | ✅ |
| Update order status with history tracking | ✅ |
| List all orders with filters | ✅ |
| Filter by: status, customer name, phone, garment type | ✅ |
| Dashboard: total orders, revenue, per-status count | ✅ |
| Bill calculation (auto + custom pricing) | ✅ |
| Estimated delivery date (dynamic by status) | ✅ |
| Delete orders | ✅ |
| Status history timeline | ✅ |

### Bonus Features
| Feature | Status |
|---|---|
| Full React-like SPA frontend (Vanilla JS) | ✅ |
| SQLite persistent database | ✅ |
| Popular garments analytics | ✅ |
| Today's revenue + orders stats | ✅ |
| Real-time bill preview while creating order | ✅ |
| Toast notifications | ✅ |
| Responsive design | ✅ |
| Swagger / ReDoc API docs | ✅ |
| Search by garment type | ✅ |

---

## 📡 API Reference

### Orders
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/orders` | Create new order |
| GET | `/api/orders` | List/filter orders |
| GET | `/api/orders/{id}` | Get order details |
| PATCH | `/api/orders/{id}/status` | Update status |
| DELETE | `/api/orders/{id}` | Delete order |

### Dashboard & Config
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard` | Dashboard analytics |
| GET | `/api/prices` | Garment price catalog |

### Sample: Create Order
```json
POST /api/orders
{
  "customer_name": "Priya Sharma",
  "phone": "9876543210",
  "garments": [
    { "garment": "Saree", "quantity": 2 },
    { "garment": "Shirt", "quantity": 3 }
  ],
  "notes": "Handle dupatta carefully"
}
```

### Response
```json
{
  "success": true,
  "order_id": "ORD-250615-A3B2C1",
  "total_bill": 360.0,
  "estimated_delivery": "2025-06-18",
  "message": "Order ORD-250615-A3B2C1 created successfully!"
}
```

---

## 🤖 AI Usage Report

### Tools Used
- **Claude (Anthropic)** — Primary AI used throughout

---

### Sample Prompts Used

**1. Architecture Design**
> "I need to build a laundry order management system with FastAPI and SQLite. Design the database schema with orders, order_items, and status_history tables. Include proper foreign keys and constraints."

**2. API Route Generation**
> "Write a FastAPI endpoint to create an order. It should accept customer_name, phone, a list of garments with quantity and optional price, auto-calculate total, generate a unique order ID with date prefix, save to SQLite, and return the order ID and total bill."

**3. Filter Query Building**
> "Write a dynamic SQLite query builder in Python that filters orders by optional parameters: status, customer_name (partial match), phone (partial), and garment type (JOIN on order_items). Must prevent SQL injection using parameterized queries."

**4. Frontend Dashboard**
> "Build a dark-themed SPA dashboard for a laundry management app with sidebar navigation, stat cards, status pills, a popular garments bar chart, and recent orders list. Use CSS variables and vanilla JS with fetch() calls. No frameworks."

**5. Bill Preview Widget**
> "Create an interactive bill preview in HTML that updates in real-time as the user adds/removes garments. Each row has a garment selector (populated from an API), quantity input, auto-filled price, and a running total."

---

### What AI Got Right ✅
- Complete FastAPI boilerplate with Pydantic validation
- SQLite schema with proper foreign keys and PRAGMA
- Dynamic query building with parameterized queries
- Full CRUD endpoints with proper HTTP codes
- CSS variable theming and responsive grid layout
- Toast notification system

### What I Had to Fix / Improve 🔧
- **Pydantic v2 compatibility**: AI generated v1-style validators (`@validator`) which needed minor adjustment for the installed version
- **CORS + Static Files**: AI placed `StaticFiles` mount before routes — reordered to avoid conflicts
- **Order ID uniqueness**: AI used `uuid4()[:6]` which occasionally collides — added timestamp prefix `ORD-YYMMDD-XXXXXX`
- **Garment price lookup**: AI returned `None` instead of default price when garment not in catalog — added `.get(garment, 50)` fallback
- **Modal close behavior**: Click-outside to close wasn't working — fixed event target comparison
- **Bill preview display/hide**: `display:none` toggle wasn't reactive — moved to `updateBill()` function

### What I Skipped (Time Constraints)
- JWT Authentication (would add with `python-jose` + bcrypt)
- Deployment to Railway/Render
- Unit tests (would use `pytest` + `httpx` for async testing)
- Email/SMS notifications on status change

### What I'd Improve With More Time
1. **Authentication** — JWT with role-based access (owner vs staff)
2. **PostgreSQL** — Replace SQLite for production multi-user
3. **Analytics Page** — Revenue charts (Chart.js), weekly trends
4. **Print Receipt** — PDF invoice generation per order
5. **WhatsApp Notifications** — Twilio API for status updates to customer
6. **Mobile App** — React Native wrapper for counter staff
7. **Bulk Status Update** — Select multiple orders and update together

---

## 🗂 Project Structure

```
laundrypro/
├── backend/
│   ├── main.py          # FastAPI app, routes, models
│   └── laundry.db       # SQLite database (auto-created)
├── frontend/
│   └── templates/
│       └── index.html   # Full SPA frontend
├── requirements.txt
└── README.md
```

---

## 💰 Garment Price Catalog (Default)

| Garment | Price (₹) |
|---|---|
| Shirt | 40 |
| T-Shirt | 35 |
| Pants | 50 |
| Jeans | 60 |
| Saree | 120 |
| Suit | 200 |
| Jacket | 150 |
| Kurta | 60 |
| Dress | 100 |
| Blanket | 180 |
| Bedsheet | 80 |
| Lehenga | 200 |

*Prices are configurable in `backend/main.py` → `GARMENT_PRICES` dict*

---

## 📸 Screenshots / Demo

Run locally and visit `http://localhost:8000` to see:
- **Dashboard** — Live stats, status counts, popular garments
- **Create Order** — Smart form with real-time bill preview
- **All Orders** — Filterable table with quick status update
- **Order Detail** — Full timeline, bill breakdown, status controls

---

## 🧪 Testing with curl

```bash
# Create order
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Test User","phone":"9999999999","garments":[{"garment":"Shirt","quantity":2}]}'

# Get all orders
curl http://localhost:8000/api/orders

# Update status
curl -X PATCH http://localhost:8000/api/orders/ORD-XXXXXX/status \
  -H "Content-Type: application/json" \
  -d '{"status":"PROCESSING"}'

# Dashboard
curl http://localhost:8000/api/dashboard
```

---

## 📝 License
MIT — free to use, modify, and distribute.
