from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from ..extensions import db, mail
from ..models.user import User, Role
from ..models.analysis import SystemLog
from . import auth_bp
from .forms import (
    RegistrationForm, LoginForm, RequestPasswordResetForm,
    ResetPasswordForm, ProfileForm, ChangePasswordForm,
)


def _log(level, message, category="auth"):
    entry = SystemLog(
        level=level, category=category, message=message,
        user_id=current_user.id if current_user.is_authenticated else None,
        ip_address=request.remote_addr,
    )
    db.session.add(entry)
    db.session.commit()


# ── Register ──────────────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            role=Role.PATIENT,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        _log("INFO", f"New user registered: {user.email}")
        flash("Account created! Please sign in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form, title="Register")


# ── Login ─────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            _log("INFO", f"User logged in: {user.email}")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))
        flash("Invalid email or password.", "danger")
        _log("WARNING", f"Failed login attempt for: {form.email.data}")
    return render_template("auth/login.html", form=form, title="Sign In")


# ── Guest ─────────────────────────────────────────────────────────────────
@auth_bp.route("/guest")
def guest():
    session["is_guest"] = True
    flash("You are browsing as a guest. Sign up to save your analyses.", "info")
    return redirect(url_for("main.index"))


# ── Logout ────────────────────────────────────────────────────────────────
@auth_bp.route("/logout")
@login_required
def logout():
    _log("INFO", f"User logged out: {current_user.email}")
    logout_user()
    session.pop("is_guest", None)
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))


# ── Password Reset Request ────────────────────────────────────────────────
@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.get_reset_token()
            _send_reset_email(user, token)
            _log("INFO", f"Password reset requested for: {user.email}")
        # Always show success to avoid email enumeration
        flash("If that email is registered, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_request.html", form=form, title="Reset Password")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    user = User.verify_reset_token(token)
    if not user:
        flash("The reset link is invalid or has expired.", "danger")
        return redirect(url_for("auth.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        _log("INFO", f"Password reset completed for: {user.email}")
        flash("Password updated. Please sign in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form, title="New Password")


def _send_reset_email(user, token):
    reset_url = url_for("auth.reset_password", token=token, _external=True)
    msg = Message("DermAssist-AI — Password Reset", recipients=[user.email])
    msg.body = (
        f"Hi {user.username},\n\n"
        f"Click the link below to reset your password (valid for 1 hour):\n{reset_url}\n\n"
        "If you did not request this, please ignore this email.\n\n"
        "— DermAssist-AI Team"
    )
    try:
        mail.send(msg)
    except Exception:
        pass  # fail silently if mail not configured


# ── Profile ───────────────────────────────────────────────────────────────
@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.phone = form.phone.data
        current_user.date_of_birth = form.date_of_birth.data
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html", form=form, title="My Profile")


# ── Change Password ───────────────────────────────────────────────────────
@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("auth.change_password"))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        _log("INFO", f"Password changed for: {current_user.email}")
        flash("Password changed successfully.", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/change_password.html", form=form, title="Change Password")
