from sqlalchemy import String, Column, Integer, ForeignKey, DateTime, func, Table
from sqlalchemy.orm import relationship
from app.database import Base

project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id")),
    Column("user_id", ForeignKey("users.id"))
)

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User",backref="projects")
    members = relationship("User", secondary=project_members, backref="joined_projects")