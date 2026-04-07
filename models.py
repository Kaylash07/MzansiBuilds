from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    bio = db.Column(db.Text, default="")
    skills = db.Column(db.String(500), default="")
    github_url = db.Column(db.String(200), default="")
    avatar_color = db.Column(db.String(7), default="#00A86B")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    projects = db.relationship("Project", backref="developer", lazy="dynamic", cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="author", lazy="dynamic", cascade="all, delete-orphan")
    collaborations = db.relationship("CollaborationRequest", backref="requester", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def completed_projects_count(self):
        return self.projects.filter_by(stage="completed").count()

    @property
    def initials(self):
        return self.username[:2].upper()

    def __repr__(self):
        return f"<User {self.username}>"


# Project stages
PROJECT_STAGES = [
    ("idea", "Idea / Concept"),
    ("planning", "Planning"),
    ("in_progress", "In Progress"),
    ("testing", "Testing"),
    ("completed", "Completed"),
]

SUPPORT_TYPES = [
    ("none", "No support needed"),
    ("frontend", "Frontend Development"),
    ("backend", "Backend Development"),
    ("design", "UI/UX Design"),
    ("testing", "Testing / QA"),
    ("devops", "DevOps / Deployment"),
    ("mentorship", "Mentorship"),
    ("code_review", "Code Review"),
    ("other", "Other"),
]


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack = db.Column(db.String(500), default="")
    repo_url = db.Column(db.String(200), default="")
    live_url = db.Column(db.String(200), default="")
    stage = db.Column(db.String(20), nullable=False, default="idea")
    support_needed = db.Column(db.String(20), default="none")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    milestones = db.relationship("Milestone", backref="project", lazy="dynamic", cascade="all, delete-orphan",
                                 order_by="Milestone.created_at.desc()")
    comments = db.relationship("Comment", backref="project", lazy="dynamic", cascade="all, delete-orphan",
                               order_by="Comment.created_at.desc()")
    collaboration_requests = db.relationship("CollaborationRequest", backref="project", lazy="dynamic",
                                             cascade="all, delete-orphan")

    @property
    def stage_display(self):
        return dict(PROJECT_STAGES).get(self.stage, self.stage)

    @property
    def support_display(self):
        return dict(SUPPORT_TYPES).get(self.support_needed, self.support_needed)

    def __repr__(self):
        return f"<Project {self.title}>"


class Milestone(db.Model):
    __tablename__ = "milestones"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    def __repr__(self):
        return f"<Milestone {self.title}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    def __repr__(self):
        return f"<Comment by {self.author.username if self.author else 'unknown'}>"


class CollaborationRequest(db.Model):
    __tablename__ = "collaboration_requests"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="pending")  # pending, accepted, declined
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    # Prevent duplicate requests
    __table_args__ = (
        db.UniqueConstraint("user_id", "project_id", name="unique_collaboration_request"),
    )

    def __repr__(self):
        return f"<CollaborationRequest by {self.requester.username if self.requester else 'unknown'}>"


BUG_CATEGORIES = [
    ("bug", "Bug / Something Broken"),
    ("ui", "UI / Design Issue"),
    ("feature", "Feature Request"),
    ("account", "Account Issue"),
    ("other", "Other"),
]


class SupportTicket(db.Model):
    __tablename__ = "support_tickets"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(20), nullable=False, default="bug")
    description = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default="open")  # open, in_progress, resolved
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reporter = db.relationship("User", backref="support_tickets")

    @property
    def category_display(self):
        return dict(BUG_CATEGORIES).get(self.category, self.category)

    def __repr__(self):
        return f"<SupportTicket {self.subject}>"


NOTIFICATION_TYPES = [
    ("comment", "New Comment"),
    ("collab_request", "Collaboration Request"),
    ("collab_accepted", "Collaboration Accepted"),
    ("collab_declined", "Collaboration Declined"),
    ("milestone", "New Milestone"),
]


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    recipient = db.relationship("User", foreign_keys=[user_id], backref=db.backref("notifications", lazy="dynamic", order_by="Notification.created_at.desc()"))
    project = db.relationship("Project", backref="notifications")
    actor = db.relationship("User", foreign_keys=[actor_id])

    def __repr__(self):
        return f"<Notification {self.type} for user {self.user_id}>"
