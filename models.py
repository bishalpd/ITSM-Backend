from __future__ import annotations
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String,Text,func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

# ENUMS
class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    AGENT = "agent"
    ADMIN = "admin"

class  TicketType(str, enum.Enum):
    INCIDENT = "incident"
    SERVICE_REQUEST = "service_request"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# users
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False,index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
    Enum(
        UserRole,
        name="user_role",
        values_callable=lambda enum_class: [
            member.value for member in enum_class
        ],
    ),
    default=UserRole.EMPLOYEE,
    nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # tickets created by the user
    requested_tickets: Mapped[list[Ticket]] = relationship("Ticket", back_populates="requester", foreign_keys="[Ticket.requester_id]")
    # Tickets assigned to this user as an agent
    assigned_tickets: Mapped[list[Ticket]] = relationship("Ticket", back_populates="assigned_agent", foreign_keys="[Ticket.assigned_agent_id]")
    # Comments written by this user
    comments: Mapped[list[TicketComment]] = relationship("TicketComment", back_populates="author")
    # Ticket changes performed by this user
    ticket_history_entries: Mapped[list[TicketHistory]] = relationship("TicketHistory", back_populates="changed_by")

    
# categories
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100),unique=True,index=True,nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id",ondelete="SET NULL"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True,nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # parent category
    parent: Mapped[Optional[Category]] = relationship("Category",back_populates="children",remote_side="Category.id")
    # Subcategories
    children: Mapped[list[Category]] = relationship(
        "Category",
        back_populates="parent",
    )
    # tickets belonging to this category
    tickets: Mapped[list[Ticket]] = relationship("Ticket", back_populates="category")

# tickets
class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ticket_type: Mapped[TicketType] = mapped_column(Enum(TicketType,name="ticket_type"),default=TicketType.INCIDENT, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus,name="ticket_status"),default=TicketStatus.OPEN, nullable=False)
    priority: Mapped[TicketPriority] = mapped_column(Enum(TicketPriority,name="ticket_priority"),default=TicketPriority.MEDIUM, nullable=False)

    # user who created the ticket
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="RESTRICT"), index=True,nullable=False)

    # agent currently handling the ticket
    assigned_agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id",ondelete="SET NULL"), index=True,nullable=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id",ondelete="RESTRICT"), index=True,nullable=False)
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # user who created the ticket
    requester: Mapped[User] = relationship("User",back_populates="requested_tickets",foreign_keys=[requester_id])

    # agent assigned to the ticket
    assigned_agent: Mapped[Optional[User]] = relationship("User",back_populates="assigned_tickets",foreign_keys=[assigned_agent_id])
    # category to which the ticket belongs
    category: Mapped[Category] = relationship("Category", back_populates="tickets")
    comments: Mapped[list[TicketComment]] = relationship("TicketComment", back_populates="ticket",cascade="all, delete-orphan")
    history: Mapped[list[TicketHistory]] = relationship("TicketHistory", back_populates="ticket",cascade="all, delete-orphan")

    # ticket comment
class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id",ondelete="CASCADE"), index=True, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="RESTRICT"), index=True, nullable=False)
    message : Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="comments")
    author: Mapped[User] = relationship("User", back_populates="comments")


    # ticket history
class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id",ondelete="CASCADE"), index=True, nullable=False)
    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="RESTRICT"), index=True, nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="history")
    changed_by: Mapped[User] = relationship("User", back_populates="ticket_history_entries")