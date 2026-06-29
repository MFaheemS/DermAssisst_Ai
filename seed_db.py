"""
Seed the database with:
  - Default admin user
  - 5 disease categories (Acne, Eczema, Melanoma, Psoriasis, Normal)

Usage: python seed_db.py
"""
import os
from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.disease import DiseaseCategory

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@dermassist.ai")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@12345")

DISEASES = [
    {
        "name": "Acne",
        "slug": "acne",
        "icon": "bandaid",
        "description": (
            "Acne is a common skin condition that occurs when hair follicles become "
            "plugged with oil and dead skin cells, causing pimples, blackheads, or whiteheads."
        ),
        "symptoms": "Whiteheads, blackheads, papules, pustules, nodules, cystic lesions.",
        "treatment": (
            "Topical retinoids, benzoyl peroxide, salicylic acid washes. "
            "Severe cases may require oral antibiotics or isotretinoin."
        ),
        "severity_info": "Low Risk: comedonal acne. Moderate Risk: inflammatory papules. High Risk: nodulocystic acne.",
        "educational_content": (
            "Acne affects approximately 85% of people at some point in their lives. "
            "It is most common during adolescence but can persist into adulthood. "
            "Hormonal changes, diet, and stress are known contributing factors."
        ),
    },
    {
        "name": "Eczema",
        "slug": "eczema",
        "icon": "moisture",
        "description": (
            "Eczema (atopic dermatitis) is a condition that makes the skin red, inflamed, "
            "and itchy. It is chronic and tends to flare periodically."
        ),
        "symptoms": "Dry skin, severe itching, red or brownish-gray patches, small raised bumps, thickened skin.",
        "treatment": (
            "Moisturisers, topical corticosteroids, calcineurin inhibitors, "
            "antihistamines for itch relief, biologics for severe cases."
        ),
        "severity_info": "Low Risk: mild dryness. Moderate Risk: widespread patches. High Risk: infected or weeping lesions.",
        "educational_content": (
            "Eczema affects about 10–20% of children and 1–3% of adults worldwide. "
            "It is not contagious. Triggers include soaps, detergents, sweat, stress, "
            "and certain foods."
        ),
    },
    {
        "name": "Melanoma",
        "slug": "melanoma",
        "icon": "exclamation-triangle-fill",
        "description": (
            "Melanoma is the most serious form of skin cancer, developing in the cells "
            "(melanocytes) that produce melanin. Early detection is critical for survival."
        ),
        "symptoms": (
            "Asymmetric mole, irregular border, multiple colours, diameter > 6 mm, "
            "evolving size/shape/colour (ABCDE rule)."
        ),
        "treatment": (
            "Surgical excision, immunotherapy, targeted therapy (BRAF/MEK inhibitors), "
            "radiation, chemotherapy depending on stage."
        ),
        "severity_info": "All melanoma detections are classified as High Risk — immediate dermatologist consultation required.",
        "educational_content": (
            "Melanoma accounts for only 1% of skin cancers but causes the majority of "
            "skin cancer deaths. UV radiation is the primary risk factor. "
            "5-year survival rate exceeds 98% when detected at Stage I."
        ),
    },
    {
        "name": "Psoriasis",
        "slug": "psoriasis",
        "icon": "layers-fill",
        "description": (
            "Psoriasis is a chronic autoimmune condition that speeds up the skin cell "
            "life cycle, causing cells to build up rapidly on the surface."
        ),
        "symptoms": "Red patches with thick, silvery scales, dry/cracked skin, itching, burning, soreness.",
        "treatment": (
            "Topical treatments (corticosteroids, vitamin D analogues), light therapy "
            "(phototherapy), systemic medications, biologics for moderate-to-severe cases."
        ),
        "severity_info": "Low Risk: limited plaque. Moderate Risk: >10% BSA. High Risk: erythrodermic or pustular psoriasis.",
        "educational_content": (
            "Psoriasis affects approximately 2–3% of the world population. "
            "It is not contagious. Triggers include stress, infections, certain medications, "
            "and skin injury (Koebner phenomenon)."
        ),
    },
    {
        "name": "Normal Skin",
        "slug": "normal",
        "icon": "check-circle-fill",
        "description": "No significant skin disease detected. The lesion appears within normal variation.",
        "symptoms": "No specific symptoms of concern detected.",
        "treatment": "Maintain regular skincare routine. Use sunscreen SPF 30+ daily.",
        "severity_info": "Low Risk: no disease indicators detected.",
        "educational_content": (
            "Regular skin self-examination and annual dermatologist visits are recommended "
            "for early detection of skin changes, especially for individuals with a history "
            "of sun exposure or family history of skin cancer."
        ),
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Admin user
        if not User.query.filter_by(email=ADMIN_EMAIL).first():
            admin = User(
                username="admin",
                email=ADMIN_EMAIL,
                role=Role.ADMIN,
                full_name="DermAssist Administrator",
            )
            admin.set_password(ADMIN_PASSWORD)
            db.session.add(admin)
            print(f"Admin created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        else:
            print("Admin already exists.")

        # Disease categories
        for d in DISEASES:
            if not DiseaseCategory.query.filter_by(slug=d["slug"]).first():
                cat = DiseaseCategory(**d)
                db.session.add(cat)
                print(f"Disease added: {d['name']}")
            else:
                print(f"Disease exists: {d['name']}")

        db.session.commit()
        print("\nDatabase seeded successfully.")
        print(f"Users: {User.query.count()}")
        print(f"Disease categories: {DiseaseCategory.query.count()}")


if __name__ == "__main__":
    seed()
