from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db, login_manager


class Role:
    GUEST = "guest"
    PATIENT = "patient"
    MEDICAL = "medical"
    ADMIN = "admin"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)  # nullable for guests
    role = db.Column(db.String(20), nullable=False, default=Role.PATIENT)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_guest = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    # profile
    full_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    profile_picture = db.Column(db.String(256), nullable=True)

    analyses = db.relationship("Analysis", backref="user", lazy="dynamic",
                               cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return s.dumps(self.email, salt="password-reset")

    @staticmethod
    def verify_reset_token(token, expiry=3600):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = s.loads(token, salt="password-reset", max_age=expiry)
        except Exception:
            return None
        return User.query.filter_by(email=email).first()

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_medical(self):
        return self.role in (Role.MEDICAL, Role.ADMIN)

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
