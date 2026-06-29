from datetime import datetime, timezone
from ..extensions import db


class Severity:
    LOW = "Low Risk"
    MODERATE = "Moderate Risk"
    HIGH = "High Risk"


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # null = guest
    disease_id = db.Column(db.Integer, db.ForeignKey("disease_categories.id"), nullable=True)

    # image paths (relative to static/)
    original_image = db.Column(db.String(256), nullable=False)
    heatmap_image = db.Column(db.String(256), nullable=True)

    # prediction results
    predicted_class = db.Column(db.String(100), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    all_scores = db.Column(db.Text, nullable=True)  # JSON string of all class scores
    severity = db.Column(db.String(30), nullable=True)
    consult_recommended = db.Column(db.Boolean, default=False)
    is_normal = db.Column(db.Boolean, default=False)

    # meta
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    processing_time_ms = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default="pending")  # pending | completed | failed
    error_message = db.Column(db.Text, nullable=True)

    report = db.relationship("Report", backref="analysis", uselist=False,
                              cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Analysis {self.id} {self.predicted_class}>"


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey("analyses.id"), nullable=False)
    pdf_path = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Report {self.id} for Analysis {self.analysis_id}>"


class SystemLog(db.Model):
    __tablename__ = "system_logs"

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)   # INFO | WARNING | ERROR | CRITICAL
    category = db.Column(db.String(50), nullable=True) # auth | prediction | upload | admin
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<SystemLog [{self.level}] {self.message[:40]}>"
