# CrewUp - Influencer Marketing Platform

![Django](https://img.shields.io/badge/Django-5.x-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

CrewUp is a comprehensive Django-based platform that connects brands with influencers for collaborative marketing campaigns. The platform streamlines the entire influencer marketing workflow from campaign creation to payment processing.

## 🌟 Features

### For Brands
- **Campaign Management**: Create, edit, and manage marketing campaigns
- **Influencer Discovery**: Browse and search for influencers based on criteria
- **Custom Offers**: Send personalized collaboration offers to influencers
- **Application Review**: Review and manage influencer applications
- **Payment Processing**: Secure payment handling via Stripe integration
- **Analytics Dashboard**: Track campaign performance and engagement

### For Influencers
- **Campaign Discovery**: Browse available campaigns and opportunities
- **Application System**: Apply to campaigns that match your niche
- **Offer Management**: Receive and respond to custom offers from brands
- **Profile Management**: Showcase your portfolio, analytics, and social media presence
- **Analytics Tracking**: Display follower counts, engagement rates, and platform statistics
- **Dashboard**: Manage all your campaigns and applications in one place

### For Administrators
- **User Management**: Comprehensive admin panel for managing users
- **Moderation Tools**: Ban/unban users with audit trail
- **System Monitoring**: Oversee platform activity and user interactions
- **Content Moderation**: Review and manage campaigns and user content

## 🛠️ Technology Stack

- **Backend**: Django 5.x
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Tailwind CSS (via django-tailwind)
- **Payment Processing**: Stripe API
- **Image Processing**: Pillow
- **Database**: SQLite (development) / PostgreSQL (production recommended)
- **Testing**: pytest with functional test suite

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Stripe account (for payment processing)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/1farha2023/CrewUp-Project.git
cd CrewUp-Project
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Stripe Configuration
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/crewup
```

**Note**: Use the provided `.env.example` file as a template.

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the platform.

## 📁 Project Structure

```
CrewUp-Project/
├── authentication/          # User authentication & profiles
│   ├── models.py           # Custom user model
│   ├── views.py            # Auth views (login, signup, profile)
│   ├── forms.py            # Authentication forms
│   └── backends.py         # Custom authentication backend
├── campaigns/              # Campaign management
│   ├── models.py           # Campaign, Application, Offer models
│   ├── views.py            # Campaign CRUD operations
│   └── forms.py            # Campaign forms
├── payments/               # Stripe payment integration
│   ├── models.py           # Payment models
│   ├── views.py            # Payment processing views
│   └── urls.py             # Payment endpoints
├── adminPanel/             # Admin functionality
│   ├── views.py            # User management, moderation
│   └── urls.py             # Admin routes
├── templates/              # HTML templates
│   ├── authentication/     # Login, signup, profile pages
│   ├── campaigns/          # Campaign views
│   ├── admin/              # Admin panel templates
│   └── base.html           # Base template
├── static/                 # Static files
│   └── js/                 # JavaScript files
├── functional_tests/       # Pytest functional tests
├── crewup/                 # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI configuration
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── .env.example            # Environment variables template
```

## 🧪 Running Tests

The project includes a comprehensive functional test suite using pytest.

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run specific test file
pytest functional_tests/test_authentication.py

# Run with coverage
pytest --cov=.

# Run with verbose output
pytest -v
```

## 👥 User Roles

### Brand Account
- Create and manage campaigns
- Search for influencers
- Send custom offers
- Process payments
- Review applications

### Influencer Account
- Browse campaigns
- Apply to campaigns
- Receive and respond to offers
- Manage profile and analytics
- Track collaborations

### Admin Account
- Manage all users
- Moderate content
- Ban/unban users
- System-wide oversight

## 🔐 Security Features

- Environment-based configuration for sensitive data
- Custom authentication backend supporting email/username login
- CSRF protection on all forms
- Secure password hashing
- .gitignore configured to prevent secret exposure
- Stripe webhook signature verification

## 💳 Payment Integration

The platform uses Stripe for secure payment processing:

1. Brands create campaigns with payment terms
2. Influencers accept offers/applications
3. Payment is processed through Stripe Checkout
4. Webhooks handle payment confirmations
5. Both parties receive payment notifications

## 🎨 Customization

### Tailwind CSS

The project uses django-tailwind for styling. To customize:

```bash
# Install Tailwind dependencies
python manage.py tailwind install

# Start Tailwind in watch mode
python manage.py tailwind start

# Build for production
python manage.py tailwind build
```

## 📝 API Endpoints

### Authentication
- `POST /auth/signup/` - User registration
- `POST /auth/login/` - User login
- `GET /auth/logout/` - User logout
- `GET /auth/profile/` - View profile
- `POST /auth/profile/edit/` - Edit profile

### Campaigns
- `GET /campaigns/` - List all campaigns
- `POST /campaigns/create/` - Create campaign (brands only)
- `GET /campaigns/<id>/` - Campaign details
- `POST /campaigns/<id>/apply/` - Apply to campaign
- `POST /campaigns/<id>/offer/` - Send custom offer

### Payments
- `POST /payment/create-checkout-session/` - Initiate payment
- `GET /payment/success/` - Payment success page
- `GET /payment/cancel/` - Payment cancelled page
- `POST /payment/webhook/` - Stripe webhook handler

### Admin
- `GET /admin/dashboard/` - Admin dashboard
- `GET /admin/users/` - User management
- `POST /admin/ban/<user_id>/` - Ban user
- `POST /admin/unban/<user_id>/` - Unban user

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Bug Reports

If you discover a bug, please create an issue on GitHub with:
- Bug description
- Steps to reproduce
- Expected behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django community for excellent documentation
- Stripe for robust payment processing
- Tailwind CSS for modern styling framework
- All contributors and testers

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: farhanahoquemahima@gmail.com
- **Farhana Hoque Mahima**- [@1farha2023](https://github.com/1farha2023)

## 🗺️ Roadmap

- [ ] Social media API integration (Instagram, YouTube, TikTok)
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Campaign performance metrics
- [ ] Multi-currency support
- [ ] Mobile app (React Native/Flutter)
- [ ] AI-powered influencer recommendations
- [ ] Contract management system
- [ ] Messaging system between brands and influencers

---

**Note**: This is a production-ready platform. Ensure you configure proper security settings, use environment variables for sensitive data, and follow Django best practices for deployment.

Made with ❤️ by the CrewUp Team
