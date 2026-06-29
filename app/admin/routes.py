from functools import wraps
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from ..extensions import db
from ..models.user import User, Role
from ..models.disease import DiseaseCategory
from ..models.analysis import Analysis, SystemLog
from . import admin_bp


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return login_required(decorated)


class DiseaseCategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    slug = StringField("Slug", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description")
    symptoms = TextAreaField("Symptoms")
    treatment = TextAreaField("Treatment")
    severity_info = TextAreaField("Severity Info")
    educational_content = TextAreaField("Educational Content")
    icon = StringField("Bootstrap Icon Class", validators=[Length(max=50)])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save")


# ── Dashboard ─────────────────────────────────────────────────────────────
@admin_bp.route("/")
@admin_required
def dashboard():
    stats = {
        "users": User.query.count(),
        "analyses": Analysis.query.count(),
        "diseases": DiseaseCategory.query.count(),
        "errors": SystemLog.query.filter_by(level="ERROR").count(),
    }
    recent_logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(10).all()
    return render_template("admin/dashboard.html", title="Admin Dashboard",
                           stats=stats, recent_logs=recent_logs)


# ── User Management ───────────────────────────────────────────────────────
@admin_bp.route("/users")
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", title="Manage Users", users=all_users)


@admin_bp.route("/users/<int:uid>/toggle")
@admin_required
def toggle_user(uid):
    user = db.session.get(User, uid)
    if not user or user.is_admin:
        flash("Cannot modify this user.", "danger")
        return redirect(url_for("admin.users"))
    user.is_active = not user.is_active
    db.session.commit()
    state = "activated" if user.is_active else "deactivated"
    flash(f"User {user.email} {state}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:uid>/role", methods=["POST"])
@admin_required
def change_role(uid):
    user = db.session.get(User, uid)
    if not user:
        abort(404)
    new_role = request.form.get("role")
    if new_role in (Role.PATIENT, Role.MEDICAL, Role.ADMIN):
        user.role = new_role
        db.session.commit()
        flash(f"Role updated to {new_role}.", "success")
    return redirect(url_for("admin.users"))


# ── Disease Categories ────────────────────────────────────────────────────
@admin_bp.route("/diseases")
@admin_required
def diseases():
    cats = DiseaseCategory.query.all()
    return render_template("admin/diseases.html", title="Disease Categories", categories=cats)


@admin_bp.route("/diseases/new", methods=["GET", "POST"])
@admin_required
def new_disease():
    form = DiseaseCategoryForm()
    if form.validate_on_submit():
        cat = DiseaseCategory(
            name=form.name.data, slug=form.slug.data,
            description=form.description.data, symptoms=form.symptoms.data,
            treatment=form.treatment.data, severity_info=form.severity_info.data,
            educational_content=form.educational_content.data,
            icon=form.icon.data, is_active=form.is_active.data,
        )
        db.session.add(cat)
        db.session.commit()
        flash("Disease category created.", "success")
        return redirect(url_for("admin.diseases"))
    return render_template("admin/disease_form.html", form=form, title="New Disease Category")


@admin_bp.route("/diseases/<int:did>/edit", methods=["GET", "POST"])
@admin_required
def edit_disease(did):
    cat = db.session.get(DiseaseCategory, did)
    if not cat:
        abort(404)
    form = DiseaseCategoryForm(obj=cat)
    if form.validate_on_submit():
        form.populate_obj(cat)
        db.session.commit()
        flash("Disease category updated.", "success")
        return redirect(url_for("admin.diseases"))
    return render_template("admin/disease_form.html", form=form, title="Edit Disease Category")


# ── Logs ──────────────────────────────────────────────────────────────────
@admin_bp.route("/logs")
@admin_required
def logs():
    level = request.args.get("level", "")
    query = SystemLog.query
    if level:
        query = query.filter_by(level=level)
    page_logs = query.order_by(SystemLog.created_at.desc()).paginate(
        page=request.args.get("page", 1, type=int), per_page=50, error_out=False
    )
    return render_template("admin/logs.html", title="System Logs", logs=page_logs, level=level)


# ── Analyses ──────────────────────────────────────────────────────────────
@admin_bp.route("/analyses")
@admin_required
def analyses():
    page_analyses = (
        Analysis.query.order_by(Analysis.created_at.desc())
        .paginate(page=request.args.get("page", 1, type=int), per_page=20, error_out=False)
    )
    return render_template("admin/analyses.html", title="All Analyses",
                           analyses=page_analyses)
