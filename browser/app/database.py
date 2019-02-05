from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# engine = create_engine(
#     'postgresql://miro_user:affenbrotbaum@localhost:5432/miro', convert_unicode=True
# )
engine = create_engine(
    'postgresql://miro:rpki@localhost:5432/mirodb', convert_unicode=True
)
db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.metadata.reflect(engine)
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # import app.models
    Base.metadata.create_all(bind=engine)
