🧺 LaundryPro - AI-First Laundry Order Management System

A full-stack Laundry Order Management System built using FastAPI + SQLite + Modern UI, designed for real-world POS workflows with analytics and automated order tracking.

🚀 Live Demo

👉 https://laundrypro-0ocn.onrender.com

🔹 Setup Instructions (Local Development)

Follow these steps to run the project locally:

1. Clone the Repository
cd C:\laundry-system
2. Activate Virtual Environment
Windows (PowerShell)
.\venv\Scripts\Activate.ps1
3. Install Dependencies
pip install -r requirements.txt
4. Start Backend Server
cd backend
python main.py
5. Open Application

Visit:

http://localhost:8000
🔹 Features Implemented
🧾 Order Management System
Create, update, and track laundry orders
Full lifecycle tracking:
RECEIVED → PROCESSING → READY → DELIVERED
👕 Dynamic Garment Pricing System
35+ garment types supported
Auto pricing per item
Custom pricing override supported
📊 Real-Time Dashboard Analytics
Total orders tracking
Revenue insights
Popular garments analysis
Status distribution charts
🗄️ Database Integration (SQLite)
Persistent order storage
Order item mapping
Status history tracking
Relational schema design
🎨 Modern UI/UX Design
Glassmorphism UI effects
Responsive layout
Smooth micro-interactions
Clean POS dashboard interface
🔹 AI Development Assistance
🧠 Tools Used
ChatGPT / Claude: Backend logic, debugging, architecture design
Google Gemini: UI refinement, feature brainstorming, workflow optimization
💡 Example Prompts Used
“Build a FastAPI backend for laundry order management system”
“Create dashboard analytics for revenue and order tracking”
“Improve UI design to look like a premium POS system”
⚠️ Challenges Faced & Fixes
1. Environment Issues
Problem: Dependency errors due to virtual environment mismatch
Fix: Standardized setup with requirements.txt
2. UI Design Consistency
Problem: Basic UI generated initially
Fix: Upgraded to modern glassmorphism design system
3. Database Integrity
Problem: Missing relational constraints
Fix: Added proper foreign keys + cascade deletion logic
🔹 Tradeoffs
❌ Skipped Features (MVP Scope)
Authentication system (login/signup)
Payment gateway integration
Email/SMS notifications
Role-based access control
🚀 Future Improvements
PostgreSQL migration (scalability upgrade)
PWA / Mobile app support
AI-based demand forecasting
Admin & Staff dashboards
Barcode/QR-based order tracking
Docker deployment setup
🏆 Project Summary

LaundryPro is a production-ready MVP-level system that demonstrates:

Full-stack development skills
API design (FastAPI)
Database design (SQLite)
Frontend integration
Deployment (Render)
Real-world business logic implementation