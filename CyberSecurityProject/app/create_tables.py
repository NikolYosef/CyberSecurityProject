from app.database import engine, Base


# Creates all database tables based on the SQLAlchemy models.
def run():
    Base.metadata.create_all(bind=engine)
    print("Tables created!")


if __name__ == "__main__":
    run()
