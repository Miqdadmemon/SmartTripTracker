# Smart Trip Tracker & Logistics Management System

A complete full-stack web application for tracking transportation trips and logistics deliveries. Built with Python Flask, SQLite, Bootstrap 5, and modern JavaScript.

## 🌟 Features

### Core Features
- **User Authentication**: Secure registration and login system with role-based access (user/admin)
- **Trip Management**: Create, edit, delete, and track trips with detailed information
- **Delivery Tracking**: Track packages with unique tracking numbers and status updates
- **Analytics Dashboard**: View statistics including total trips, distance, cost, and carbon footprint
- **Search & Filter**: Easily find trips and deliveries with advanced filtering
- **Export Data**: Export trip data to CSV format

### Additional Features
- **Carbon Footprint Calculator**: Automatic calculation based on transport mode
- **Fuel Consumption Estimation**: Estimate fuel usage for vehicle trips
- **Route Optimization Suggestions**: Get personalized recommendations
- **Trip Status Tracking**: Plan, track, and complete trips
- **Mobile-Responsive Design**: Works like a mobile app on all devices

## 🛠️ Tech Stack

- **Backend**: Python 3.x with Flask
- **Database**: SQLite (built-in, no setup required)
- **Frontend**: HTML5, CSS3, JavaScript
- **Framework**: Bootstrap 5
- **Authentication**: Flask-Login with password hashing

## 📁 Project Structure

```
SmartTripTracker/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── dashboard.html   # User dashboard
│   ├── trips.html       # Trip list
│   ├── trip_form.html   # Create/Edit trip
│   ├── trip_detail.html # Trip details
│   ├── analytics.html   # Analytics page
│   ├── deliveries.html  # Delivery list
│   ├── delivery_form.html   # Create delivery
│   ├── delivery_detail.html # Delivery details
│   ├── search.html      # Search results
│   ├── admin.html       # Admin panel
│   └── error.html       # Error page
└── instance/           # SQLite database (created automatically)
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Navigate to Project Directory
```bash
cd SmartTripTracker
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On mac3 -m vOS/Linux
pythonsource venv/binenv venv
/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4:```bash
python Run the Application
 app.py
```

### Step 5: Access the Application
Open your browser and navigate to: **http://127.0.0.1:5000**

## 📋 Login Credentials

After running the application for the first time, sample data will be created automatically:

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`

### Regular User Account
- **Username**: `john_doe`
- **Password**: `password123`

## 🎯 How to Use

### 1. User Registration & Login
- Visit the home page and click "Register" to create a new account
- Or use the demo accounts above

### 2. Creating a Trip
1. Click "New Trip" from the dashboard
2. Fill in trip details (start location, destination, date, transport mode, distance)
3. Click "Create Trip"
4. The system will automatically calculate carbon footprint and fuel consumption

### 3. Managing Deliveries
1. Click "New Delivery" from the dashboard
2. Enter sender and receiver information
3. A unique tracking number will be generated
4. Update the status as the package moves

### 4. Viewing Analytics
1. Click "Analytics" from the navigation
2. View total trips, distance, cost, and carbon footprint
3. See breakdown by transport mode
4. Get route optimization suggestions

### 5. Admin Panel
- Access at `/admin` (requires admin role)
- View all users and their trips
- Manage users (delete)

### 6. Export Data
- Click "Export" on the trips page to download CSV

## 🔧 Configuration

### Changing the Secret Key
Edit `config.py` and change the `SECRET_KEY` value:
```python
SECRET_KEY = 'your-secret-key-here'
```

### Database
The application uses SQLite by default, which requires no setup. The database file (`smarttrip.db`) will be created automatically in the `instance/` folder.

## 📊 Database Schema

### Users Table
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- role (user/admin)
- created_at

### Trips Table
- id (Primary Key)
- user_id (Foreign Key)
- start_location
- destination
- start_date
- end_date
- mode_of_transport
- distance
- travel_cost
- fuel_consumption
- carbon_footprint
- status (planned/ongoing/completed)
- notes
- created_at

### Deliveries Table
- id (Primary Key)
- user_id (Foreign Key)
- tracking_number (Unique)
- sender_name
- receiver_name
- sender_address
- receiver_address
- package_description
- weight
- status
- current_location
- estimated_delivery
- actual_delivery
- created_at

## 🎓 For College Project Submission

This project is designed to meet all requirements for a final semester submission:

✅ Full-stack architecture
✅ Database integration
✅ User authentication
✅ CRUD operations
✅ Data visualization (analytics)
✅ Mobile-responsive design
✅ Clean code with comments
✅ Proper error handling
✅ Security best practices
✅ Sample data included
✅ Complete documentation

## 📝 License

This project is for educational purposes.

## 👨‍💻 Author

College Semester Project - Transportation & Logistics Domain

## 🆘 Troubleshooting

### Port Already in Use
If port 5000 is already in use, you can change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Database Issues
Delete the `instance/smarttrip.db` file and restart the application to recreate the database.

### Module Not Found
Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

