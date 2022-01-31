from .model import Base , DEMfiles, Shapefiles, accessCode
from .app import nasaaccess as app
from sqlalchemy.orm import sessionmaker


# Initialize an empty database, if the database has not been created already.



def init_db(engine, first_time):
    print("Initializing Persistant Storage")
    Base.metadata.create_all(engine)
    if first_time:
    # # Make session
        SessionMaker = sessionmaker(bind=engine)
        session = SessionMaker()

        session.close()
        print("Finishing Initializing Persistant Storage")