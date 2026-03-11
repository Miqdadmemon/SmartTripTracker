"""
Smart Trip Tracker & Logistics Management System
Main Flask Application
"""
import os
import csv
import io
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, send_file, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user

# Import extensions and models
from extensions import db, login_manager
from models import User, Trip, Delivery

# Create Flask application
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== DECORATORS ====================

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTH ROUTES ====================

@app.route('/')
def index():
    """Home page - landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Make first user admin
        if User.query.count() == 0:
            user.role = 'admin'
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - shows recent trips and stats"""
    # Get user's recent trips
    recent_trips = Trip.query.filter_by(user_id=current_user.id)\
        .order_by(Trip.created_at.desc()).limit(5).all()
    
    # Get statistics
    total_trips = Trip.query.filter_by(user_id=current_user.id).count()
    total_distance = db.session.query(db.func.sum(Trip.distance))\
        .filter_by(user_id=current_user.id).scalar() or 0
    total_cost = db.session.query(db.func.sum(Trip.travel_cost))\
        .filter_by(user_id=current_user.id).scalar() or 0
    total_carbon = db.session.query(db.func.sum(Trip.carbon_footprint))\
        .filter_by(user_id=current_user.id).scalar() or 0
    
    # Get active deliveries
    active_deliveries = Delivery.query.filter_by(user_id=current_user.id)\
        .filter(Delivery.status.in_(['pending', 'picked_up', 'in_transit', 'out_for_delivery']))\
        .order_by(Delivery.created_at.desc()).limit(3).all()
    
    # Get trips by status
    planned_trips = Trip.query.filter_by(user_id=current_user.id, status='planned').count()
    ongoing_trips = Trip.query.filter_by(user_id=current_user.id, status='ongoing').count()
    completed_trips = Trip.query.filter_by(user_id=current_user.id, status='completed').count()
    
    stats = {
        'total_trips': total_trips,
        'total_distance': round(total_distance, 2),
        'total_cost': round(total_cost, 2),
        'total_carbon': round(total_carbon, 2),
        'planned': planned_trips,
        'ongoing': ongoing_trips,
        'completed': completed_trips
    }
    
    return render_template('dashboard.html', 
                         recent_trips=recent_trips,
                         active_deliveries=active_deliveries,
                         stats=stats)


# ==================== TRIP ROUTES ====================

@app.route('/trips')
@login_required
def trips():
    """List all trips with optional filters"""
    # Get filter parameters
    status = request.args.get('status', '')
    mode = request.args.get('mode', '')
    search = request.args.get('search', '')
    
    # Build query
    query = Trip.query.filter_by(user_id=current_user.id)
    
    if status:
        query = query.filter(Trip.status == status)
    if mode:
        query = query.filter(Trip.mode_of_transport == mode)
    if search:
        query = query.filter(
            db.or_(
                Trip.start_location.ilike(f'%{search}%'),
                Trip.destination.ilike(f'%{search}%'),
                Trip.notes.ilike(f'%{search}%')
            )
        )
    
    # Order by date descending
    all_trips = query.order_by(Trip.start_date.desc()).all()
    
    return render_template('trips.html', 
                         trips=all_trips,
                         status_filter=status,
                         mode_filter=mode,
                         search_query=search)


@app.route('/trips/new', methods=['GET', 'POST'])
@login_required
def new_trip():
    """Create a new trip"""
    if request.method == 'POST':
        start_location = request.form.get('start_location', '').strip()
        destination = request.form.get('destination', '').strip()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        mode_of_transport = request.form.get('mode_of_transport')
        distance = request.form.get('distance')
        travel_cost = request.form.get('travel_cost', 0)
        status = request.form.get('status', 'planned')
        notes = request.form.get('notes', '').strip()
        
        # Validation
        errors = []
        if not start_location:
            errors.append('Start location is required.')
        if not destination:
            errors.append('Destination is required.')
        if not start_date:
            errors.append('Start date is required.')
        if not mode_of_transport:
            errors.append('Mode of transport is required.')
        if not distance or float(distance) <= 0:
            errors.append('Valid distance is required.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('trip_form.html', trip=None, modes=Trip.TRANSPORT_MODES)
        
        # Parse dates
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
            end_dt = None
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('trip_form.html', trip=None, modes=Trip.TRANSPORT_MODES)
        
        # Create trip
        trip = Trip(
            user_id=current_user.id,
            start_location=start_location,
            destination=destination,
            start_date=start_dt,
            end_date=end_dt,
            mode_of_transport=mode_of_transport,
            distance=float(distance),
            travel_cost=float(travel_cost) if travel_cost else 0,
            status=status,
            notes=notes
        )
        
        # Calculate carbon footprint and fuel consumption
        trip.calculate_carbon_footprint()
        trip.calculate_fuel_consumption()
        
        db.session.add(trip)
        db.session.commit()
        
        flash('Trip created successfully!', 'success')
        return redirect(url_for('trips'))
    
    return render_template('trip_form.html', trip=None, modes=Trip.TRANSPORT_MODES)


@app.route('/trips/<int:trip_id>')
@login_required
def trip_detail(trip_id):
    """View trip details"""
    trip = Trip.query.get_or_404(trip_id)
    
    # Ensure user owns this trip (or is admin)
    if trip.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('trips'))
    
    return render_template('trip_detail.html', trip=trip)


@app.route('/trips/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id):
    """Edit an existing trip"""
    trip = Trip.query.get_or_404(trip_id)
    
    # Ensure user owns this trip
    if trip.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('trips'))
    
    if request.method == 'POST':
        trip.start_location = request.form.get('start_location', '').strip()
        trip.destination = request.form.get('destination', '').strip()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        trip.mode_of_transport = request.form.get('mode_of_transport')
        trip.distance = float(request.form.get('distance', 0))
        trip.travel_cost = float(request.form.get('travel_cost', 0))
        trip.status = request.form.get('status', 'planned')
        trip.notes = request.form.get('notes', '').strip()
        
        # Parse dates
        try:
            trip.start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
            if end_date:
                trip.end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
            else:
                trip.end_date = None
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('trip_form.html', trip=trip, modes=Trip.TRANSPORT_MODES)
        
        # Recalculate carbon footprint and fuel consumption
        trip.calculate_carbon_footprint()
        trip.calculate_fuel_consumption()
        
        db.session.commit()
        
        flash('Trip updated successfully!', 'success')
        return redirect(url_for('trip_detail', trip_id=trip.id))
    
    return render_template('trip_form.html', trip=trip, modes=Trip.TRANSPORT_MODES)


@app.route('/trips/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    """Delete a trip"""
    trip = Trip.query.get_or_404(trip_id)
    
    # Ensure user owns this trip
    if trip.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('trips'))
    
    db.session.delete(trip)
    db.session.commit()
    
    flash('Trip deleted successfully!', 'success')
    return redirect(url_for('trips'))


@app.route('/trips/<int:trip_id>/status', methods=['POST'])
@login_required
def update_trip_status(trip_id):
    """Update trip status"""
    trip = Trip.query.get_or_404(trip_id)
    
    # Ensure user owns this trip
    if trip.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('trips'))
    
    new_status = request.form.get('status')
    if new_status in ['planned', 'ongoing', 'completed']:
        trip.status = new_status
        
        # Set end date if completed
        if new_status == 'completed' and not trip.end_date:
            trip.end_date = datetime.utcnow()
        
        db.session.commit()
        flash(f'Trip status updated to {new_status}!', 'success')
    
    return redirect(url_for('trip_detail', trip_id=trip.id))


# ==================== ANALYTICS ROUTES ====================

@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard with statistics and charts"""
    # Basic stats
    total_trips = Trip.query.filter_by(user_id=current_user.id).count()
    total_distance = db.session.query(db.func.sum(Trip.distance))\
        .filter_by(user_id=current_user.id).scalar() or 0
    total_cost = db.session.query(db.func.sum(Trip.travel_cost))\
        .filter_by(user_id=current_user.id).scalar() or 0
    total_carbon = db.session.query(db.func.sum(Trip.carbon_footprint))\
        .filter_by(user_id=current_user.id).scalar() or 0
    total_fuel = db.session.query(db.func.sum(Trip.fuel_consumption))\
        .filter_by(user_id=current_user.id).scalar() or 0
    
    # Trips by transport mode
    mode_stats = db.session.query(
        Trip.mode_of_transport,
        db.func.count(Trip.id).label('count'),
        db.func.sum(Trip.distance).label('distance')
    ).filter_by(user_id=current_user.id).group_by(Trip.mode_of_transport).all()
    
    # Trips by status
    status_stats = db.session.query(
        Trip.status,
        db.func.count(Trip.id).label('count')
    ).filter_by(user_id=current_user.id).group_by(Trip.status).all()
    
    # Monthly trips (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_stats = db.session.query(
        db.func.strftime('%Y-%m', Trip.start_date).label('month'),
        db.func.count(Trip.id).label('count'),
        db.func.sum(Trip.distance).label('distance')
    ).filter(
        Trip.user_id == current_user.id,
        Trip.start_date >= six_months_ago
    ).group_by('month').order_by('month').all()
    
    # Average trip cost
    avg_cost = total_cost / total_trips if total_trips > 0 else 0
    avg_distance = total_distance / total_trips if total_trips > 0 else 0
    
    # Route optimization suggestions
    suggestions = []
    if total_trips > 0:
        # Find most common routes
        common_routes = db.session.query(
            Trip.start_location,
            Trip.destination,
            db.func.count(Trip.id).label('count')
        ).filter_by(user_id=current_user.id).group_by(
            Trip.start_location, Trip.destination
        ).having(db.func.count(Trip.id) > 1).all()
        
        if common_routes:
            suggestions.append(f"You frequently travel on {len(common_routes)} routes. Consider planning these trips together to save time and cost.")
        
        # Check for long-distance solo car trips
        long_car_trips = Trip.query.filter_by(
            user_id=current_user.id,
            mode_of_transport='car'
        ).filter(Trip.distance > 100).count()
        
        if long_car_trips > 2:
            suggestions.append(f"You have {long_car_trips} long car trips (>100km). Consider using public transport for these routes to reduce costs and carbon footprint.")
    
    stats = {
        'total_trips': total_trips,
        'total_distance': round(total_distance, 2),
        'total_cost': round(total_cost, 2),
        'total_carbon': round(total_carbon, 2),
        'total_fuel': round(total_fuel, 2),
        'avg_cost': round(avg_cost, 2),
        'avg_distance': round(avg_distance, 2)
    }
    
    return render_template('analytics.html',
                         stats=stats,
                         mode_stats=mode_stats,
                         status_stats=status_stats,
                         monthly_stats=monthly_stats,
                         suggestions=suggestions)


# ==================== DELIVERY ROUTES ====================

@app.route('/deliveries')
@login_required
def deliveries():
    """List all deliveries"""
    status_filter = request.args.get('status', '')
    
    query = Delivery.query.filter_by(user_id=current_user.id)
    if status_filter:
        query = query.filter(Delivery.status == status_filter)
    
    all_deliveries = query.order_by(Delivery.created_at.desc()).all()
    
    return render_template('deliveries.html', 
                         deliveries=all_deliveries,
                         status_filter=status_filter)


@app.route('/deliveries/new', methods=['GET', 'POST'])
@login_required
def new_delivery():
    """Create a new delivery"""
    if request.method == 'POST':
        sender_name = request.form.get('sender_name', '').strip()
        receiver_name = request.form.get('receiver_name', '').strip()
        sender_address = request.form.get('sender_address', '').strip()
        receiver_address = request.form.get('receiver_address', '').strip()
        package_description = request.form.get('package_description', '').strip()
        weight = request.form.get('weight', 0)
        estimated_days = request.form.get('estimated_days', 3)
        
        # Validation
        errors = []
        if not sender_name:
            errors.append('Sender name is required.')
        if not receiver_name:
            errors.append('Receiver name is required.')
        if not sender_address:
            errors.append('Sender address is required.')
        if not receiver_address:
            errors.append('Receiver address is required.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('delivery_form.html', delivery=None)
        
        # Create delivery
        delivery = Delivery(
            user_id=current_user.id,
            tracking_number=Delivery.generate_tracking_number(),
            sender_name=sender_name,
            receiver_name=receiver_name,
            sender_address=sender_address,
            receiver_address=receiver_address,
            package_description=package_description,
            weight=float(weight) if weight else None,
            status='pending',
            estimated_delivery=datetime.utcnow() + timedelta(days=int(estimated_days))
        )
        
        db.session.add(delivery)
        db.session.commit()
        
        flash(f'Delivery created! Tracking number: {delivery.tracking_number}', 'success')
        return redirect(url_for('deliveries'))
    
    return render_template('delivery_form.html', delivery=None)


@app.route('/deliveries/<tracking_number>')
@login_required
def delivery_detail(tracking_number):
    """View delivery details"""
    delivery = Delivery.query.filter_by(tracking_number=tracking_number).first_or_404()
    
    # Ensure user owns this delivery (or is admin)
    if delivery.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('deliveries'))
    
    return render_template('delivery_detail.html', delivery=delivery)


@app.route('/deliveries/<int:delivery_id>/update', methods=['POST'])
@login_required
def update_delivery_status(delivery_id):
    """Update delivery status"""
    delivery = Delivery.query.get_or_404(delivery_id)
    
    # Ensure user owns this delivery
    if delivery.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('deliveries'))
    
    new_status = request.form.get('status')
    current_location = request.form.get('current_location', '').strip()
    
    if new_status:
        delivery.status = new_status
        if current_location:
            delivery.current_location = current_location
        if new_status == 'delivered':
            delivery.actual_delivery = datetime.utcnow()
        
        db.session.commit()
        flash(f'Delivery status updated to {new_status}!', 'success')
    
    return redirect(url_for('delivery_detail', tracking_number=delivery.tracking_number))


# ==================== SEARCH ROUTES ====================

@app.route('/search')
@login_required
def search():
    """Search trips and deliveries"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('dashboard'))
    
    # Search trips
    trips = Trip.query.filter(
        Trip.user_id == current_user.id,
        db.or_(
            Trip.start_location.ilike(f'%{query}%'),
            Trip.destination.ilike(f'%{query}%'),
            Trip.notes.ilike(f'%{query}%')
        )
    ).order_by(Trip.start_date.desc()).all()
    
    # Search deliveries
    deliveries = Delivery.query.filter(
        Delivery.user_id == current_user.id,
        db.or_(
            Delivery.tracking_number.ilike(f'%{query}%'),
            Delivery.sender_name.ilike(f'%{query}%'),
            Delivery.receiver_name.ilike(f'%{query}%'),
            Delivery.sender_address.ilike(f'%{query}%'),
            Delivery.receiver_address.ilike(f'%{query}%')
        )
    ).order_by(Delivery.created_at.desc()).all()
    
    return render_template('search.html', 
                         query=query,
                         trips=trips,
                         deliveries=deliveries)


# ==================== EXPORT ROUTES ====================

@app.route('/export/csv')
@login_required
def export_csv():
    """Export trips to CSV"""
    trips = Trip.query.filter_by(user_id=current_user.id)\
        .order_by(Trip.start_date.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Start Location', 'Destination', 'Start Date', 'End Date',
        'Mode of Transport', 'Distance (km)', 'Travel Cost ($)',
        'Fuel Consumption (L)', 'Carbon Footprint (kg)', 'Status', 'Notes'
    ])
    
    # Write data
    for trip in trips:
        writer.writerow([
            trip.id,
            trip.start_location,
            trip.destination,
            trip.start_date.strftime('%Y-%m-%d %H:%M') if trip.start_date else '',
            trip.end_date.strftime('%Y-%m-%d %H:%M') if trip.end_date else '',
            trip.mode_of_transport,
            trip.distance,
            trip.travel_cost,
            trip.fuel_consumption or '',
            trip.carbon_footprint or '',
            trip.status,
            trip.notes or ''
        ])
    
    # Create response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'trips_export_{datetime.now().strftime("%Y%m%d")}.csv'
    )


# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@login_required
@admin_required
def admin():
    """Admin dashboard"""
    # Get all users
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Get all trips
    all_trips = Trip.query.order_by(Trip.created_at.desc()).limit(20).all()
    
    # Get statistics
    total_users = User.query.count()
    total_trips = Trip.query.count()
    total_deliveries = Delivery.query.count()
    
    stats = {
        'total_users': total_users,
        'total_trips': total_trips,
        'total_deliveries': total_deliveries
    }
    
    return render_template('admin.html', 
                         users=users,
                         trips=all_trips,
                         stats=stats)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting self
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} deleted successfully!', 'success')
    return redirect(url_for('admin'))


# ==================== API ROUTES ====================

@app.route('/api/trips/<int:trip_id>', methods=['GET'])
@login_required
def api_trip(trip_id):
    """Get trip as JSON"""
    trip = Trip.query.get_or_404(trip_id)
    
    if trip.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'id': trip.id,
        'start_location': trip.start_location,
        'destination': trip.destination,
        'start_date': trip.start_date.isoformat() if trip.start_date else None,
        'end_date': trip.end_date.isoformat() if trip.end_date else None,
        'mode_of_transport': trip.mode_of_transport,
        'distance': trip.distance,
        'travel_cost': trip.travel_cost,
        'fuel_consumption': trip.fuel_consumption,
        'carbon_footprint': trip.carbon_footprint,
        'status': trip.status,
        'notes': trip.notes
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('error.html', error_code=404, error_message='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500


# ==================== DATABASE SETUP ====================

def init_db():
    """Initialize database with tables and sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if sample data exists
        if User.query.count() == 0:
            print("Creating sample data...")
            create_sample_data()
            print("Sample data created successfully!")


def create_sample_data():
    """Create sample users, trips, and deliveries"""
    # Create admin user
    admin = User(username='admin', email='admin@smarttrip.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create regular user
    user = User(username='john_doe', email='john@example.com', role='user')
    user.set_password('password123')
    db.session.add(user)
    
    db.session.commit()
    
    # Sample trips for admin
    trips_data = [
        {
            'user_id': admin.id,
            'start_location': 'New York City',
            'destination': 'Boston',
            'start_date': datetime(2024, 1, 15, 8, 0),
            'end_date': datetime(2024, 1, 15, 12, 0),
            'mode_of_transport': 'train',
            'distance': 350,
            'travel_cost': 75,
            'status': 'completed',
            'notes': 'Business trip to Boston office'
        },
        {
            'user_id': admin.id,
            'start_location': 'Los Angeles',
            'destination': 'San Francisco',
            'start_date': datetime(2024, 2, 1, 7, 0),
            'end_date': datetime(2024, 2, 1, 14, 0),
            'mode_of_transport': 'flight',
            'distance': 615,
            'travel_cost': 150,
            'status': 'completed',
            'notes': 'Conference attendance'
        },
        {
            'user_id': admin.id,
            'start_location': 'Chicago',
            'destination': 'Detroit',
            'start_date': datetime(2024, 3, 10, 9, 0),
            'mode_of_transport': 'car',
            'distance': 280,
            'travel_cost': 45,
            'status': 'planned',
            'notes': 'Upcoming client meeting'
        },
        {
            'user_id': admin.id,
            'start_location': 'Miami',
            'destination': 'Orlando',
            'start_date': datetime(2024, 2, 20, 6, 0),
            'end_date': datetime(2024, 2, 20, 10, 0),
            'mode_of_transport': 'bus',
            'distance': 375,
            'travel_cost': 35,
            'status': 'ongoing',
            'notes': 'Currently on the road'
        }
    ]
    
    # Sample trips for regular user
    user_trips = [
        {
            'user_id': user.id,
            'start_location': 'San Francisco',
            'destination': 'Los Angeles',
            'start_date': datetime(2024, 1, 20, 10, 0),
            'end_date': datetime(2024, 1, 20, 18, 0),
            'mode_of_transport': 'flight',
            'distance': 543,
            'travel_cost': 120,
            'status': 'completed',
            'notes': 'Family visit'
        },
        {
            'user_id': user.id,
            'start_location': 'Seattle',
            'destination': 'Portland',
            'start_date': datetime(2024, 2, 5, 7, 30),
            'end_date': datetime(2024, 2, 5, 11, 0),
            'mode_of_transport': 'car',
            'distance': 280,
            'travel_cost': 40,
            'status': 'completed',
            'notes': 'Weekend trip'
        }
    ]
    
    for trip_data in trips_data + user_trips:
        trip = Trip(**trip_data)
        trip.calculate_carbon_footprint()
        trip.calculate_fuel_consumption()
        db.session.add(trip)
    
    # Sample deliveries
    deliveries_data = [
        {
            'user_id': admin.id,
            'tracking_number': 'STT-A1B2C3D4',
            'sender_name': 'Amazon Warehouse',
            'receiver_name': 'John Smith',
            'sender_address': '123 Warehouse St, New York, NY',
            'receiver_address': '456 Main St, Boston, MA',
            'package_description': 'Electronics - Laptop',
            'weight': 2.5,
            'status': 'in_transit',
            'current_location': 'Hartford, CT',
            'estimated_delivery': datetime(2024, 3, 15)
        },
        {
            'user_id': admin.id,
            'tracking_number': 'STT-E5F6G7H8',
            'sender_name': 'FedEx Center',
            'receiver_name': 'Jane Doe',
            'sender_address': '789 Shipping Ave, Los Angeles, CA',
            'receiver_address': '321 Delivery Rd, San Francisco, CA',
            'package_description': 'Documents - Important',
            'weight': 0.5,
            'status': 'delivered',
            'current_location': 'San Francisco, CA',
            'estimated_delivery': datetime(2024, 2, 10),
            'actual_delivery': datetime(2024, 2, 9)
        },
        {
            'user_id': user.id,
            'tracking_number': 'STT-I9J0K1L2',
            'sender_name': 'UPS Store',
            'receiver_name': 'Mike Johnson',
            'sender_address': '555 Parcel Way, Seattle, WA',
            'receiver_address': '777 Cargo Blvd, Portland, OR',
            'package_description': 'Clothing Package',
            'weight': 1.2,
            'status': 'pending',
            'estimated_delivery': datetime(2024, 3, 20)
        }
    ]
    
    for delivery_data in deliveries_data:
        delivery = Delivery(**delivery_data)
        db.session.add(delivery)
    
    db.session.commit()


# ==================== MAIN ENTRY POINT ====================

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    print("\n" + "="*60)
    print("🚀 Smart Trip Tracker & Logistics Management System")
    print("="*60)
    print("\n📱 Mobile-Friendly Trip Tracking Application")
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Server running at: http://127.0.0.1:{port}")
    print("\n📋 Login Credentials:")
    print("   Admin:   username: admin,   password: admin123")
    print("   User:    username: john_doe, password: password123")
    print("="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)

