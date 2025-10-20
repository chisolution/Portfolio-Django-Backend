# Django Portfolio Backend - Project Overview

## Project Vision
Build a professional, high-performance personal portfolio backend using Django that serves as a standout asset for job hunting. The backend operates as a stateless API gateway deployed on Render's free tier, with persistent data stored in an external PostgreSQL provider (Supabase/Neon).

## Strategic Objectives
1. **Data Persistence**: Reliably store contact form submissions and project metadata in an external, persistent PostgreSQL database
2. **Stateless Architecture**: Design the Django service to be entirely stateless, robust against arbitrary service restarts
3. **Performance**: Minimize response times and resource consumption to operate efficiently on Render's free tier
4. **Security**: Implement proper validation, sanitization, and secure communication with the frontend
5. **Scalability**: Design with N-tier architecture to support future enhancements

## Key Constraints
- **Render Free Tier**: No persistent disks, arbitrary restarts, fast startup required
- **External Database**: Must use Supabase/Neon (not Render's 90-day expiring database)
- **Stateless Design**: No session storage, temporary files, or cache within the container
- **API Contract**: Secure communication with Next.js frontend via CORS

## Core API Endpoints
1. **POST /api/contact** - Handle contact form submissions with validation and sanitization
2. **GET /api/projects** - Retrieve curated project metadata for dynamic frontend consumption
3. **GET /api/health** - Health check endpoint for monitoring

## Technology Stack
- **Framework**: Django (async, high-performance)
- **Server**: Uvicorn
- **Database**: PostgreSQL (external: Supabase/Neon)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Testing**: pytest, pytest-asyncio
- **Deployment**: Render (free tier)

## Project Duration
6 weeks (3 sprints of 2 weeks each)

## Success Criteria
- ✅ All endpoints functional and tested
- ✅ Contact form submissions persisted in external database
- ✅ WCAG AA compliance for all API responses
- ✅ Sub-200ms response times for GET endpoints
- ✅ Zero data loss due to service restarts
- ✅ Successful deployment on Render free tier

