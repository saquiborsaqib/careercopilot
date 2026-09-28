from backend.schemas.student import StudentProfileCreate
from backend.schemas.recommendation import RecommendationCreate
from backend.database.models.enums import RecommendationType


def test_student_profile_schema():
    x = StudentProfileCreate(user_id=1, degree="B.Tech", cgpa=8.5)
    assert x.cgpa == 8.5


def test_recommendation_target_validation():
    x = RecommendationCreate(
        student_id=1,
        recommendation_type=RecommendationType.CAREER,
        career_id=2,
        title="Data Scientist",
    )
    assert x.career_id == 2
