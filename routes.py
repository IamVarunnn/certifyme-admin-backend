from app import app
from flask import request, jsonify
from models import db, Admin
from werkzeug.security import generate_password_hash

@app.route('/')
def home():
    return jsonify({"message": "Backend Running"})


# ================= SIGNUP =================
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()

    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # 🔴 Validation
    if not full_name or not email or not password or not confirm_password:
        return jsonify({"error": "All fields are required"}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    # 🔴 Check if user exists
    existing_user = Admin.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # 🔐 Hash password
    hashed_password = generate_password_hash(password)

    # 💾 Save user
    new_admin = Admin(
        full_name=full_name,
        email=email,
        password_hash=hashed_password
    )

    db.session.add(new_admin)
    db.session.commit()

    return jsonify({"message": "Signup successful"}), 201


from werkzeug.security import check_password_hash
from flask_login import login_user

# ================= LOGIN =================
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False)

    # 🔴 Validate input
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    # 🔍 Find user
    user = Admin.query.filter_by(email=email).first()

    # 🔐 Check password
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # ✅ Login user
    login_user(user, remember=remember)

    return jsonify({"message": "Login successful"}), 200

from itsdangerous import URLSafeTimedSerializer

# Token generator
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# ================= FORGOT PASSWORD =================
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    user = Admin.query.filter_by(email=email).first()

    if user:
        # 🔐 Generate token (valid for 1 hour)
        token = serializer.dumps(email, salt='password-reset-salt')

        reset_link = f"http://127.0.0.1:5000/api/reset-password/{token}"

        # 👉 Instead of email, print in console
        print("\n🔗 PASSWORD RESET LINK:")
        print(reset_link)
        print()

    # 🔒 Always return success
    return jsonify({"message": "If this email exists, a reset link has been sent"}), 200

from flask_login import login_required, current_user
from models import Opportunity

# ================= ADD OPPORTUNITY =================
@app.route('/api/opportunities', methods=['POST'])
@login_required
def add_opportunity():
    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    duration = data.get('duration')
    start_date = data.get('start_date')
    skills = data.get('skills')
    category = data.get('category')
    future_opportunities = data.get('future_opportunities')
    max_applicants = data.get('max_applicants')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    # Optional: category validation
    allowed_categories = ["Internship", "Job", "Training"]
    if category and category not in allowed_categories:
        return jsonify({"error": "Invalid category"}), 400

    new_op = Opportunity(
        title=title,
        description=description,
        duration=duration,
        start_date=start_date,
        skills=skills,
        category=category,
        future_opportunities=future_opportunities,
        max_applicants=max_applicants,
        admin_id=current_user.id
    )

    db.session.add(new_op)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Opportunity created",
        "id": new_op.id
    }), 201

# ================= GET ALL OPPORTUNITIES =================
@app.route('/api/opportunities', methods=['GET'])
@login_required
def get_opportunities():
    ops = Opportunity.query.filter_by(admin_id=current_user.id).all()

    result = []
    for op in ops:
        result.append({
            "id": op.id,
            "title": op.title,
            "description": op.description,
            "duration": op.duration,
            "start_date": op.start_date,
            "skills": op.skills,
            "category": op.category,
            "future_opportunities": op.future_opportunities,
            "max_applicants": op.max_applicants
        })

    return jsonify({"status": "success", "data": result}), 200

# ================= GET SINGLE =================
@app.route('/api/opportunities/<int:id>', methods=['GET'])
@login_required
def get_single_opportunity(id):
    op = Opportunity.query.get(id)

    if not op or op.admin_id != current_user.id:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "id": op.id,
        "title": op.title,
        "description": op.description,
        "duration": op.duration,
        "start_date": op.start_date,
        "skills": op.skills,
        "category": op.category,
        "future_opportunities": op.future_opportunities,
        "max_applicants": op.max_applicants
    }), 200

# ================= UPDATE =================
@app.route('/api/opportunities/<int:id>', methods=['PUT'])
@login_required
def update_opportunity(id):
    op = Opportunity.query.get(id)

    if not op or op.admin_id != current_user.id:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()

    op.title = data.get('title', op.title)
    op.description = data.get('description', op.description)

    db.session.commit()

    return jsonify({"message": "Updated successfully"}), 200

# ================= DELETE =================
@app.route('/api/opportunities/<int:id>', methods=['DELETE'])
@login_required
def delete_opportunity(id):
    op = Opportunity.query.get(id)

    if not op or op.admin_id != current_user.id:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(op)
    db.session.commit()

    return jsonify({"message": "Deleted successfully"}), 200