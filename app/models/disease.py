from ..extensions import db


class DiseaseCategory(db.Model):
    __tablename__ = "disease_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    symptoms = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    severity_info = db.Column(db.Text, nullable=True)
    educational_content = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    icon = db.Column(db.String(50), nullable=True)  # Bootstrap icon class

    analyses = db.relationship("Analysis", backref="disease", lazy="dynamic")

    def __repr__(self):
        return f"<DiseaseCategory {self.name}>"
