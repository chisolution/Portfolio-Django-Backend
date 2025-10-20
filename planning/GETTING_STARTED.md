# Getting Started - Django Portfolio Backend

Welcome! This guide will help you get up and running with the Django portfolio backend project.

---

## 📋 What Has Been Created

### ✅ Complete Planning Documentation
- **8 comprehensive planning documents** covering all aspects of the project
- Business rules, user stories, sprint planning, system design, coding standards, API contract, and deployment guide
- Located in `planning/` directory

### ✅ Django Backend Project
- **N-tier architecture** with proper separation of concerns
- **Database models** for Contact and Project
- **API endpoints** for contact form, project retrieval, and health checks
- **Configuration management** with environment variables
- **Project structure** ready for development

### ✅ Configuration Files
- `requirements.txt` - All Python dependencies
- `.env.example` - Environment variables template
- `README.md` - Backend documentation

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Set Up Python Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env with your database URL
```

### Step 4: Run the Application
```bash
uvicorn app.main:app --reload
```

### Step 5: Access the API
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📚 Documentation Guide

### Start Here
1. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Visual overview of what was created
2. **[planning/README.md](planning/README.md)** - Index of all planning documents

### For Understanding the Project
- **[planning/PROJECT_OVERVIEW.md](planning/PROJECT_OVERVIEW.md)** - Vision and objectives
- **[planning/BUSINESS_RULES.md](planning/BUSINESS_RULES.md)** - Business constraints
- **[planning/USER_STORIES.md](planning/USER_STORIES.md)** - Feature requirements

### For Development
- **[planning/SYSTEM_DESIGN.md](planning/SYSTEM_DESIGN.md)** - Architecture and design
- **[planning/CODING_STANDARDS.md](planning/CODING_STANDARDS.md)** - Code style guide
- **[planning/API_CONTRACT.md](planning/API_CONTRACT.md)** - API specification

### For Operations
- **[planning/DEPLOYMENT_OPERATIONS.md](planning/DEPLOYMENT_OPERATIONS.md)** - Deployment guide
- **[planning/SPRINT_PLAN.md](planning/SPRINT_PLAN.md)** - Sprint breakdown

---

## 🏗️ Project Architecture

The backend follows a **4-layer N-tier architecture**:

```
Routes (Presentation)
    ↓
Services (Business Logic)
    ↓
Repositories (Data Access)
    ↓
Models & Schemas (Data)
```

### Key Layers

**1. Presentation Layer** (`app/routes/`)
- HTTP endpoints
- Request/response handling
- Input validation

**2. Business Logic Layer** (`app/services/`)
- Business rules
- Validation and sanitization
- Rate limiting
- Orchestration

**3. Data Access Layer** (`app/repositories/`)
- Database queries
- Transaction management
- Connection pooling

**4. Data Layer** (`app/models/` and `app/schemas/`)
- SQLAlchemy ORM models
- Pydantic validation schemas

---

## 🔑 Key Features

### Contact Form Submission
- **Endpoint**: `POST /api/contact`
- **Validation**: Email, name, subject, message
- **Rate Limiting**: 5 submissions per IP per hour
- **Storage**: Persistent external PostgreSQL database

### Project Metadata Retrieval
- **Endpoint**: `GET /api/projects`
- **Format**: PPIR (Problem, Process, Impact, Results)
- **Caching**: 1-hour cache for performance
- **Curated**: Top 3-5 projects only

### Health Monitoring
- **Endpoint**: `GET /api/health`
- **Purpose**: Service status and database connectivity
- **Used by**: Render for monitoring

---

## 📦 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Django | 5.2.7 |
| Server | Uvicorn | 0.24.0 |
| Database | PostgreSQL | Latest |
| ORM | SQLAlchemy | 2.0.23 |
| Validation | Pydantic | 2.5.0 |
| Testing | pytest | 7.4.3 |

---

## 🗄️ Database Setup

### Option 1: Local PostgreSQL
```bash
# Install PostgreSQL locally
# Create database
createdb portfolio

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/portfolio
```

### Option 2: Supabase (Recommended for Production)
1. Go to https://supabase.com
2. Create new project
3. Copy connection string
4. Update .env with connection string

### Option 3: Neon
1. Go to https://neon.tech
2. Create new project
3. Copy connection string
4. Update .env with connection string

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app
```

### Run Specific Test File
```bash
pytest tests/unit/test_contact_service.py
```

---

## 📝 API Examples

### Submit Contact Form
```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Interested in your work",
    "message": "I would like to discuss opportunities..."
  }'
```

### Get Projects
```bash
curl -X GET http://localhost:8000/api/projects
```

### Health Check
```bash
curl -X GET http://localhost:8000/api/health
```

---

## 🚀 Deployment

### Deploy to Render

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial Django backend"
   git push origin main
   ```

2. **Create Render Service**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Configure:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

3. **Set Environment Variables**
   - DATABASE_URL (from Supabase/Neon)
   - FRONTEND_URL
   - ENVIRONMENT=production

4. **Deploy**
   - Click "Deploy"
   - Monitor logs in Render dashboard

See [planning/DEPLOYMENT_OPERATIONS.md](planning/DEPLOYMENT_OPERATIONS.md) for detailed instructions.

---

## 📊 Project Timeline

### Sprint 1 (Weeks 1-2): Foundation
- ✅ Project structure created
- ✅ Planning documentation complete
- ⏭️ Implement service layer
- ⏭️ Implement repository layer
- ⏭️ Write tests

### Sprint 2 (Weeks 3-4): Integration
- ⏭️ Complete business logic
- ⏭️ Database migrations
- ⏭️ Integration testing
- ⏭️ Frontend integration

### Sprint 3 (Weeks 5-6): Deployment
- ⏭️ Performance optimization
- ⏭️ Security hardening
- ⏭️ Final testing
- ⏭️ Production deployment

---

## ❓ Common Questions

### Q: Where do I start?
**A**: Read `planning/PROJECT_OVERVIEW.md` first, then `planning/SYSTEM_DESIGN.md`.

### Q: How do I set up the database?
**A**: See "Database Setup" section above. Use Supabase or Neon for production.

### Q: How do I run the application?
**A**: Follow "Quick Start" section above.

### Q: Where is the API documentation?
**A**: Visit http://localhost:8000/docs when the app is running.

### Q: How do I deploy to production?
**A**: See [planning/DEPLOYMENT_OPERATIONS.md](planning/DEPLOYMENT_OPERATIONS.md).

### Q: What are the coding standards?
**A**: See [planning/CODING_STANDARDS.md](planning/CODING_STANDARDS.md).

### Q: What are the business rules?
**A**: See [planning/BUSINESS_RULES.md](planning/BUSINESS_RULES.md).

---

## 🔗 Important Links

- **Planning Documentation**: `planning/README.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Backend README**: `backend/README.md`
- **API Contract**: `planning/API_CONTRACT.md`
- **System Design**: `planning/SYSTEM_DESIGN.md`
- **Deployment Guide**: `planning/DEPLOYMENT_OPERATIONS.md`

---

## ✅ Checklist for Getting Started

- [ ] Read this file (GETTING_STARTED.md)
- [ ] Read PROJECT_STRUCTURE.md
- [ ] Read planning/README.md
- [ ] Set up Python virtual environment
- [ ] Install dependencies
- [ ] Set up external PostgreSQL (Supabase/Neon)
- [ ] Create .env file
- [ ] Run application locally
- [ ] Access Swagger docs at /docs
- [ ] Test API endpoints
- [ ] Read planning/CODING_STANDARDS.md
- [ ] Review planning/SYSTEM_DESIGN.md
- [ ] Ready to start Sprint 1!

---

## 🎯 Next Steps

1. **Set up your development environment** (5 minutes)
2. **Read the planning documentation** (30 minutes)
3. **Understand the architecture** (30 minutes)
4. **Run the application locally** (5 minutes)
5. **Start implementing Sprint 1 tasks** (see planning/SPRINT_PLAN.md)

---

## 📞 Need Help?

- Check the relevant planning document
- Review the code comments
- Look at the API documentation at /docs
- Check the backend README

---

**Status**: ✅ Ready for Development  
**Last Updated**: October 19, 2025  
**Next Step**: Set up development environment and read planning documentation

