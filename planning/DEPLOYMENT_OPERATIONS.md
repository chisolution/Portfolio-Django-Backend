# Deployment & Operations Guide

## Pre-Deployment Checklist

### Development Environment
- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed from requirements.txt
- [ ] .env file configured with local database
- [ ] All tests passing (pytest)
- [ ] Code coverage 85%+
- [ ] No linting errors (flake8/pylint)

### External Services Setup
- [ ] Supabase or Neon account created
- [ ] PostgreSQL database provisioned
- [ ] Database credentials obtained
- [ ] Database connection tested locally
- [ ] Alembic migrations prepared

### Code Quality
- [ ] All endpoints documented in Swagger
- [ ] Error handling comprehensive
- [ ] Input validation complete
- [ ] Security review completed
- [ ] Performance benchmarks met
- [ ] Load testing completed

---

## Render Deployment

### Step 1: Prepare Repository
```bash
# Ensure .gitignore includes:
# - venv/
# - .env
# - __pycache__/
# - *.pyc
# - .pytest_cache/

# Create .env.example (no secrets)
DATABASE_URL=postgresql://user:password@host:port/dbname
FRONTEND_URL=https://portfolio.example.com
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 2: Create Render Service
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: Django-portfolio-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Step 3: Environment Variables
In Render dashboard, add environment variables:
```
DATABASE_URL=postgresql://user:password@host:port/dbname
FRONTEND_URL=https://your-portfolio.vercel.app
ENVIRONMENT=production
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
```

### Step 4: Deploy
- Push code to GitHub
- Render automatically deploys on push
- Monitor deployment logs in Render dashboard

---

## Database Setup (Supabase Example)

### Step 1: Create Supabase Project
1. Go to https://supabase.com
2. Create new project
3. Wait for database provisioning

### Step 2: Get Connection String
1. In Supabase dashboard, go to Settings → Database
2. Copy connection string (PostgreSQL)
3. Format: `postgresql://user:password@host:port/dbname`

### Step 3: Run Migrations
```bash
# Locally first
alembic upgrade head

# On Render (via SSH or deployment script)
# Add to Render "Pre-deployment command":
alembic upgrade head
```

### Step 4: Seed Initial Data
```bash
# Create seed script: scripts/seed_projects.py
python scripts/seed_projects.py
```

---

## Monitoring & Maintenance

### Health Checks
- Render automatically monitors `/api/health` endpoint
- Configure health check in Render dashboard:
  - **Path**: /api/health
  - **Interval**: 5 minutes
  - **Timeout**: 30 seconds

### Logging
- All requests logged to stdout
- Render captures logs automatically
- Access logs in Render dashboard

### Performance Monitoring
- Monitor response times
- Track error rates
- Monitor database connection pool
- Alert on anomalies

### Database Backups
- Supabase/Neon provide automatic backups
- Configure backup retention policy
- Test restore procedures regularly

---

## Troubleshooting

### Service Won't Start
**Symptoms**: Deployment fails or service crashes immediately

**Diagnosis**:
1. Check Render logs for error messages
2. Verify environment variables are set
3. Test database connection locally

**Solutions**:
```bash
# Test locally
python -m uvicorn app.main:app --reload

# Check database connection
python -c "from app.config.database import engine; print(engine)"

# Verify all dependencies installed
pip install -r requirements.txt
```

### Database Connection Errors
**Symptoms**: 503 Service Unavailable, database connection refused

**Diagnosis**:
1. Verify DATABASE_URL is correct
2. Check database is running
3. Verify network connectivity

**Solutions**:
```bash
# Test connection string
psql "postgresql://user:password@host:port/dbname"

# Check connection pool settings
# Adjust in config/database.py if needed
```

### High Response Times
**Symptoms**: Requests taking > 200ms

**Diagnosis**:
1. Check database query performance
2. Monitor connection pool
3. Check Render CPU/memory usage

**Solutions**:
- Add database indexes
- Optimize queries
- Increase connection pool size
- Consider upgrading Render plan

### Data Loss on Restart
**Symptoms**: Data disappears after service restart

**Diagnosis**:
- Verify data is being persisted to external database
- Check database connection is maintained

**Solutions**:
- Ensure DATABASE_URL points to external provider
- Verify Alembic migrations ran successfully
- Check database backups

---

## Scaling Considerations

### Current Limitations (Free Tier)
- Render: 0.5 CPU, 512 MB RAM
- Supabase: 2 concurrent connections (free tier)
- Response time: < 200ms for GET, < 500ms for POST

### When to Scale
- If response times exceed SLA
- If error rates increase
- If database connection pool exhausted

### Scaling Options
1. **Render**: Upgrade to paid plan for more resources
2. **Database**: Upgrade Supabase/Neon plan for more connections
3. **Caching**: Implement Redis for frequently accessed data
4. **CDN**: Use Cloudflare for static content

---

## Security Hardening

### HTTPS/TLS
- Render provides free SSL certificate
- All traffic encrypted automatically
- Verify certificate in browser

### CORS Configuration
- Only allow requests from frontend domain
- Verify in production:
```bash
curl -H "Origin: https://portfolio.example.com" \
     -H "Access-Control-Request-Method: POST" \
     https://api.portfolio.example.com/api/contact
```

### Rate Limiting
- Verify rate limiting is enabled
- Monitor for abuse patterns
- Adjust limits if needed

### Secrets Management
- Never commit .env file
- Use Render environment variables
- Rotate secrets regularly
- Use strong database passwords

---

## Rollback Procedures

### If Deployment Fails
1. Render automatically keeps previous version
2. Click "Rollback" in Render dashboard
3. Service reverts to previous working version

### If Database Migration Fails
1. SSH into Render instance (if available)
2. Run `alembic downgrade -1` to rollback migration
3. Fix migration script
4. Redeploy

### If Data Corruption Occurs
1. Restore from Supabase/Neon backup
2. Verify data integrity
3. Redeploy application

---

## Maintenance Schedule

### Daily
- Monitor error rates and response times
- Check health check status

### Weekly
- Review logs for patterns
- Verify backups completed
- Check for security updates

### Monthly
- Performance analysis
- Database optimization review
- Security audit
- Dependency updates

### Quarterly
- Full system review
- Capacity planning
- Disaster recovery drill
- Documentation update

---

## Disaster Recovery Plan

### Backup Strategy
- Database: Automatic backups by Supabase/Neon
- Code: GitHub repository
- Configuration: Render environment variables

### Recovery Time Objectives (RTO)
- Service restart: < 5 minutes
- Database restore: < 30 minutes
- Full system recovery: < 1 hour

### Recovery Procedures
1. **Service Restart**: Render handles automatically
2. **Database Restore**: Use Supabase/Neon restore feature
3. **Code Rollback**: Use Render rollback feature
4. **Full Recovery**: Redeploy from GitHub + restore database

---

## Cost Optimization

### Current Setup (Free Tier)
- Render: $0 (free tier)
- Supabase: $0 (free tier, 2 concurrent connections)
- Total: $0/month

### Cost Monitoring
- Monitor Render usage
- Monitor Supabase usage
- Alert if approaching limits

### Cost Reduction
- Use free tier services
- Optimize database queries
- Implement caching
- Monitor for unused resources

