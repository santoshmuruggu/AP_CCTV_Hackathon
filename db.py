# db.py

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from faker import Faker
import random
from datetime import datetime, timedelta

# Use SQLite for local setup; switch to PostgreSQL by replacing the connection string
DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
faker = Faker()

# === TABLES ===

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    is_authorized = Column(Boolean)

class FaceLog(Base):
    __tablename__ = "face_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    confidence = Column(Float)
    status = Column(String)
    camera_id = Column(String)

    user = relationship("User")

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, unique=True)
    vehicle_type = Column(String)
    is_authorized = Column(Boolean)

class VehicleLog(Base):
    __tablename__ = "vehicle_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    camera_id = Column(String)
    license_plate = Column(String, ForeignKey("vehicles.license_plate"))
    confidence = Column(Float)
    status = Column(String)

    vehicle = relationship("Vehicle", backref="logs")

class GunnyBagEvent(Base):
    __tablename__ = "gunny_bag_events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    camera_id = Column(String)
    location_zone = Column(String)
    bag_count = Column(Integer)
    estimated_volume = Column(Float)

# === DB INIT + SEEDER ===

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed users
    for _ in range(10):
        user = User(
            name=faker.name(),
            role=random.choice(["manager", "hamali", "visitor"]),
            is_authorized=random.choice([True, True, False])
        )
        db.add(user)
    db.commit()

    users = db.query(User).all()

    # Seed face logs
    for _ in range(100):
        log = FaceLog(
            timestamp=faker.date_time_between(start_date="-7d", end_date="now"),
            user_id=random.choice(users).id,
            confidence=round(random.uniform(70, 99), 2),
            status=random.choice(["Verified", "Intrusion"]),
            camera_id=f"CAM-{random.randint(1,5)}"
        )
        db.add(log)

    # Seed vehicles
    plates = [faker.license_plate()[:10].replace(" ", "") for _ in range(15)]
    for plate in plates:
        db.add(Vehicle(
            license_plate=plate,
            vehicle_type=random.choice(["Truck", "Van", "Bike"]),
            is_authorized=random.choice([True, False])
        ))
    db.commit()

    # Seed vehicle logs
    for _ in range(100):
        plate = random.choice(plates)
        log = VehicleLog(
            timestamp=faker.date_time_between(start_date="-7d", end_date="now"),
            camera_id=f"CAM-{random.randint(1,5)}",
            license_plate=plate,
            confidence=round(random.uniform(60, 99), 2),
            status=random.choice(["Authorized", "Unauthorized"])
        )
        db.add(log)

    # Seed gunny bag events
    for _ in range(50):
        event = GunnyBagEvent(
            timestamp=faker.date_time_between(start_date="-7d", end_date="now"),
            camera_id=f"CAM-{random.randint(1,5)}",
            location_zone=random.choice(["Zone A", "Zone B", "Dock 1", "Storage Bay"]),
            bag_count=random.randint(10, 100),
            estimated_volume=round(random.uniform(1.5, 15.0), 2)
        )
        db.add(event)

    db.commit()
    db.close()
    print("✅ Database initialized and fake data inserted!")

# Run this file directly to init and seed DB
if __name__ == "__main__":
    init_db()
