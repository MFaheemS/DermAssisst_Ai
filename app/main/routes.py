from flask import render_template, redirect, url_for, session
from flask_login import login_required, current_user
from ..models.analysis import Analysis
from ..models.disease import DiseaseCategory
from . import main_bp


@main_bp.route("/")
def index():
    diseases = DiseaseCategory.query.filter_by(is_active=True).all()
    return render_template("main/index.html", title="DermAssist-AI", diseases=diseases)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    recent = (
        Analysis.query
        .filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(5)
        .all()
    )
    total = Analysis.query.filter_by(user_id=current_user.id).count()
    return render_template(
        "main/dashboard.html", title="Dashboard",
        recent_analyses=recent, total_analyses=total,
    )


@main_bp.route("/about")
def about():
    return render_template("main/about.html", title="About")


@main_bp.route("/history")
@login_required
def history():
    page = 1
    analyses = (
        Analysis.query
        .filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )
    return render_template("main/history.html", title="Analysis History", analyses=analyses)
