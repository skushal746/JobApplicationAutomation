from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from seeds import seed_data
from models import Company, QuestionAnswer, JobApplication
import os

# Use a temporary SQLite database for verification
TEST_DB_URL = "sqlite:///./test_seed.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Run seeding
        print("Running seed_data...")
        seed_data(db)
        
        # Verify data
        companies = db.query(Company).all()
        print(f"Companies found: {[c.name for c in companies]}")
        
        qas = db.query(QuestionAnswer).all()
        print(f"QuestionAnswers found: {len(qas)}")
        
        apps = db.query(JobApplication).all()
        print(f"JobApplications found: {len(apps)}")
        
        if len(companies) > 0 and len(qas) > 0 and len(apps) > 0:
            print("Verification SUCCESS: Dummy data correctly seeded.")
        else:
            print("Verification FAILURE: Some data is missing.")
            
    finally:
        db.close()
        # Clean up
        if os.path.exists("./test_seed.db"):
            os.remove("./test_seed.db")

if __name__ == "__main__":
    verify()
