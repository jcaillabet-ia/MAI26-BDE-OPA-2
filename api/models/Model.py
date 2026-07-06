from sqlmodel import SQLModel
from sqlmodel import Session

class Model(SQLModel):
    def save(self, session: Session):
        session.add(self)
        session.commit()
        session.refresh(self)
        