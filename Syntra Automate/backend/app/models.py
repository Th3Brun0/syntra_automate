# backend/app/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

user_group = Table(
    "user_group", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("group_id", Integer, ForeignKey("groups.id"))
)

mikrotik_group = Table(
    "mikrotik_group", Base.metadata,
    Column("mikrotik_id", Integer, ForeignKey("mikrotiks.id")),
    Column("group_id", Integer, ForeignKey("groups.id"))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(50), default="support")  # admin | support
    is_active = Column(Boolean, default=True)
    mfa_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    groups = relationship("Group", secondary=user_group, back_populates="users")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    users = relationship("User", secondary=user_group, back_populates="groups")
    mikrotiks = relationship("Mikrotik", secondary=mikrotik_group, back_populates="groups")

class Mikrotik(Base):
    __tablename__ = "mikrotiks"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    ip = Column(String(64), nullable=False)
    ssh_port = Column(Integer, default=22)
    ssh_user = Column(String(150), nullable=False)
    # encrypted private key or password
    credential_type = Column(String(10), default="password")  # password | key
    credential_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    groups = relationship("Group", secondary=mikrotik_group, back_populates="mikrotiks")

class ExecLog(Base):
    __tablename__ = "exec_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String(150))
    command = Column(Text)
    targets = Column(Text)  # JSON or comma list
    output = Column(Text)
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
