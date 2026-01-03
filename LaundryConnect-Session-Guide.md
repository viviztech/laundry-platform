# LaundryConnect Project - Session Continuation Guide

**Date Created**: December 30, 2025
**Project**: LaundryConnect Platform - On-Demand Laundry Aggregator

---

## **Project Files Location**

### **1. Client Presentation** (50+ pages)
```
/Users/ganeshthangavel/LaundryConnect-Client-Presentation.md
```
- Professional business proposal
- Ready to convert to PDF
- Use for client meetings

### **2. Technical Implementation Plan** (Detailed Roadmap)
```
/Users/ganeshthangavel/.claude/plans/swirling-snuggling-dawn.md
```
- Complete 20-week development roadmap
- Technical architecture details
- Database schema
- 7 Claude Skills specifications

### **3. This Guide**
```
/Users/ganeshthangavel/LaundryConnect-Session-Guide.md
```
- Quick reference for continuing work
- Commands to get started
- Session continuation instructions

---

## **How to Continue Coding Sessions**

### **Starting a New Claude Session**

When you open a new Claude Code session, say:

```
"I want to continue building LaundryConnect.
The plan is at ~/.claude/plans/swirling-snuggling-dawn.md.
I'm ready to start Phase 1."
```

Or simply:

```
"Let's build the LaundryConnect platform from the saved plan"
```

---

## **Project Overview (Quick Reference)**

### **What We're Building**
- Web and mobile laundry aggregator platform (like DhobiG/TumbleDry)
- AI-powered garment recognition
- Dynamic pricing engine
- Real-time tracking
- Partner marketplace

### **Technology Stack**
- **Backend**: Django + Django REST Framework (Python)
- **Frontend**: React 18 + TypeScript
- **Mobile**: React Native + Expo
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **AI**: OpenAI Vision API
- **Payment**: Razorpay

### **Timeline**
- 20 weeks total (5 months)
- 7 development phases
- MVP ready in Phase 6

---

## **Development Phases**

### **Phase 1: Foundation (Weeks 1-2)** ← START HERE
- Django project setup
- PostgreSQL + Redis configuration
- User authentication (JWT)
- Docker development environment
- CI/CD pipeline

### **Phase 2: Claude Skills (Weeks 3-4)**
- 7 specialized AI skills for development
- Order management automation
- Pricing calculation automation

### **Phase 3: Core Features (Weeks 5-8)**
- Data models and pricing engine
- Order system and partner matching

### **Phase 4: AI Integration (Weeks 9-10)**
- OpenAI Vision API
- Garment classification

### **Phase 5: Real-time Features (Weeks 11-13)**
- Tracking, notifications, payments

### **Phase 6: Frontend & Mobile (Weeks 14-18)**
- Web app and mobile apps

### **Phase 7: Testing & Launch (Weeks 19-20)**
- QA, deployment, go-live

---

## **Quick Start Commands**

### **Prerequisites Check**

```bash
# Check Python version (need 3.11+)
python3 --version

# Check if PostgreSQL is installed
which psql
brew install postgresql@15  # If not installed

# Check if Redis is installed
which redis-server
brew install redis  # If not installed

# Check if Docker is installed
docker --version
brew install --cask docker  # If not installed

# Check if Git is configured
git config --global user.name
git config --global user.email
```

### **Initialize Project**

```bash
# Create project directory
mkdir -p ~/projects/laundry-platform
cd ~/projects/laundry-platform

# Initialize Git repository
git init

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Ready for Django installation
```

---

## **Phase 1 Checklist**

When starting Phase 1, complete these tasks:

- [ ] Create project directory
- [ ] Set up virtual environment
- [ ] Install Django and dependencies
- [ ] Initialize Django project with modular structure
- [ ] Configure PostgreSQL database
- [ ] Configure Redis
- [ ] Create User model
- [ ] Implement JWT authentication
- [ ] Create registration API
- [ ] Create login API
- [ ] Set up Django admin
- [ ] Create Docker environment (docker-compose.yml)
- [ ] Set up GitHub repository
- [ ] Configure GitHub Actions CI/CD
- [ ] Write initial tests
- [ ] First demo: Registration and login working

---

## **Useful Commands During Development**

### **Django**
```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
pytest

# Run with coverage
pytest --cov=apps
```

### **Docker**
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose build
```

### **Git**
```bash
# Check status
git status

# Add files
git add .

# Commit
git commit -m "Phase 1: Initial Django setup"

# Push to remote
git push origin main
```

---

## **Key Features to Implement**

### **MVP Features (Must Have)**
1. ✅ Order booking & scheduling (7-step workflow)
2. ✅ Dynamic pricing & payment (Razorpay)
3. ✅ AI garment recognition (OpenAI Vision)
4. ✅ Real-time tracking & notifications
5. ✅ Partner/vendor management

### **Service Tiers**
- Regular (1.0x) - Next-day
- Premium (1.5x) - Same-day
- Express (2.0x) - 4-hour

### **Pricing Zones**
- Zone A: ₹30 pickup/delivery
- Zone B: ₹40 pickup/delivery
- Zone C: ₹46 pickup/delivery

---

## **Important URLs & Resources**

### **Documentation**
- Django: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- React: https://react.dev/
- React Native: https://reactnative.dev/
- PostgreSQL: https://www.postgresql.org/docs/

### **Third-Party Services**
- Razorpay: https://razorpay.com/docs/
- OpenAI API: https://platform.openai.com/docs/
- Google Maps API: https://developers.google.com/maps
- SendGrid: https://docs.sendgrid.com/
- Twilio: https://www.twilio.com/docs/

### **Claude Skills Best Practices**
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

---

## **Cost Tracking**

### **MVP Phase (Monthly)**
- Hosting: $5-20 (Railway/Render)
- Database: $0-25 (Supabase)
- Redis: $0-10 (Upstash)
- Storage: $5-10 (Cloudflare R2)
- Email: $0-15 (SendGrid)
- SMS: $10-50 (Twilio)
- Maps: $0-50 (Google)
- AI: $20-100 (OpenAI)
- **Total: $40-280/month**

### **Post-Launch (1000 orders/month)**
- **Total: $285-620/month**

---

## **Success Metrics**

### **Technical KPIs**
- API Response Time: <200ms (p95)
- Uptime: >99.5%
- Error Rate: <0.1%
- Test Coverage: >80%

### **Business KPIs**
- Order Completion Rate: >90%
- Customer Satisfaction: >4.5/5
- Partner Rating: >4.0/5
- Repeat Customer Rate: >30%

### **AI Performance**
- Classification Accuracy: >85%
- User Confirmation Rate: <15%
- Training Data Growth: 100+ images/week

---

## **Next Steps After Client Meeting**

1. **Get client approval** ✅
2. **Sign development agreement** ✅
3. **Set up development environment**
4. **Start Phase 1: Foundation**
5. **Weekly progress updates**

---

## **Contact & Support**

### **Developer**
- Name: Ganesh Thangavel
- Email: [Your email]
- Phone: [Your phone]

### **Project Management**
- Weekly updates: Every Friday 5 PM
- Bi-weekly meetings: Every other Monday 10 AM
- Communication: [Slack/Email/Other]

---

## **Emergency Commands**

### **If Something Breaks**

```bash
# Reset database
python manage.py flush

# Revert last migration
python manage.py migrate <app_name> <previous_migration>

# Clear Redis cache
redis-cli FLUSHALL

# Restart Docker services
docker-compose restart

# Check Django logs
tail -f logs/django.log

# Check PostgreSQL logs
tail -f logs/postgresql.log
```

### **Backup Commands**

```bash
# Backup database
pg_dump laundry_db > backup_$(date +%Y%m%d).sql

# Restore database
psql laundry_db < backup_20251230.sql

# Backup entire project
tar -czf laundry-platform-backup-$(date +%Y%m%d).tar.gz ~/projects/laundry-platform/
```

---

## **Tips for Efficient Development**

1. **Use Claude Skills**: They'll accelerate development by 50%
2. **Write tests first**: Ensures code quality from day 1
3. **Commit frequently**: Small, atomic commits are better
4. **Document as you go**: Future you will thank you
5. **Follow the plan**: The roadmap is well thought out
6. **Ask for help**: Claude is here to assist at every step

---

## **Motivation**

**You're building something amazing!**

- 20 weeks to a production-ready platform
- Solving real problems for real people
- AI-powered competitive advantage
- Clear path to profitability
- Scalable from day 1

**Let's build LaundryConnect! 🚀**

---

**Last Updated**: December 30, 2025
**Version**: 1.0
**Status**: Ready to Start Phase 1
