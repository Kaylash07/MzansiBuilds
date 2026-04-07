from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import os

from config import Config
from models import db, User, Project, Milestone, Comment, CollaborationRequest, SupportTicket, Notification, PROJECT_STAGES, SUPPORT_TYPES, BUG_CATEGORIES
from forms import (
    RegistrationForm, LoginForm, ProfileForm,
    ProjectForm, MilestoneForm, CommentForm, CollaborationForm, SupportForm,
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ──────────────────────── Context Processors ────────────────────────

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.context_processor
def inject_globals():
    unread_count = 0
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return dict(
        PROJECT_STAGES=PROJECT_STAGES,
        SUPPORT_TYPES=SUPPORT_TYPES,
        now=datetime.now(timezone.utc),
        unread_count=unread_count,
    )


# ──────────────────────── Home ────────────────────────

@app.route("/")
def index():
    recent_projects = Project.query.order_by(Project.updated_at.desc()).limit(6).all()
    completed_count = Project.query.filter_by(stage="completed").count()
    developer_count = User.query.count()
    project_count = Project.query.count()
    return render_template(
        "index.html",
        recent_projects=recent_projects,
        completed_count=completed_count,
        developer_count=developer_count,
        project_count=project_count,
    )


# ──────────────────────── Auth ────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("feed"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("auth/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("feed"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("feed"))
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Check unique constraints
        if form.username.data != current_user.username:
            existing = User.query.filter_by(username=form.username.data).first()
            if existing:
                flash("Username already taken.", "danger")
                return render_template("auth/profile.html", form=form)
        if form.email.data != current_user.email:
            existing = User.query.filter_by(email=form.email.data).first()
            if existing:
                flash("Email already registered.", "danger")
                return render_template("auth/profile.html", form=form)

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        current_user.skills = form.skills.data
        current_user.github_url = form.github_url.data

        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("profile"))
    return render_template("auth/profile.html", form=form)


@app.route("/developer/<int:user_id>")
def developer_profile(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    projects = user.projects.order_by(Project.updated_at.desc()).all()
    return render_template("auth/developer.html", developer=user, projects=projects)


# ──────────────────────── Projects ────────────────────────

@app.route("/projects/new", methods=["GET", "POST"])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            tech_stack=form.tech_stack.data,
            repo_url=form.repo_url.data,
            live_url=form.live_url.data,
            stage=form.stage.data,
            support_needed=form.support_needed.data,
            user_id=current_user.id,
        )
        if form.stage.data == "completed":
            project.completed_at = datetime.now(timezone.utc)
        db.session.add(project)
        db.session.commit()
        flash("Project created!", "success")
        return redirect(url_for("project_detail", project_id=project.id))
    return render_template("projects/create.html", form=form)


@app.route("/projects/<int:project_id>")
def project_detail(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)
    comment_form = CommentForm()
    collab_form = CollaborationForm()
    milestone_form = MilestoneForm()

    milestones = project.milestones.all()
    comments = project.comments.all()

    has_requested = False
    if current_user.is_authenticated:
        has_requested = CollaborationRequest.query.filter_by(
            user_id=current_user.id, project_id=project.id
        ).first() is not None

    return render_template(
        "projects/detail.html",
        project=project,
        comment_form=comment_form,
        collab_form=collab_form,
        milestone_form=milestone_form,
        milestones=milestones,
        comments=comments,
        has_requested=has_requested,
    )


@app.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)
    if project.user_id != current_user.id:
        abort(403)

    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        old_stage = project.stage
        project.title = form.title.data
        project.description = form.description.data
        project.tech_stack = form.tech_stack.data
        project.repo_url = form.repo_url.data
        project.live_url = form.live_url.data
        project.stage = form.stage.data
        project.support_needed = form.support_needed.data

        if form.stage.data == "completed" and old_stage != "completed":
            project.completed_at = datetime.now(timezone.utc)
            flash("Congratulations! Your project is now on the Celebration Wall!", "success")
        elif form.stage.data != "completed":
            project.completed_at = None

        db.session.commit()
        flash("Project updated!", "success")
        return redirect(url_for("project_detail", project_id=project.id))

    return render_template("projects/edit.html", form=form, project=project)


@app.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)
    if project.user_id != current_user.id:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted.", "info")
    return redirect(url_for("my_projects"))


@app.route("/my-projects")
@login_required
def my_projects():
    projects = current_user.projects.order_by(Project.updated_at.desc()).all()
    return render_template("projects/my_projects.html", projects=projects)


# ──────────────────────── Milestones ────────────────────────

@app.route("/projects/<int:project_id>/milestones", methods=["POST"])
@login_required
def add_milestone(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)
    if project.user_id != current_user.id:
        abort(403)
    form = MilestoneForm()
    if form.validate_on_submit():
        milestone = Milestone(
            title=form.title.data,
            description=form.description.data,
            project_id=project.id,
        )
        db.session.add(milestone)
        project.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash("Milestone added!", "success")
    return redirect(url_for("project_detail", project_id=project.id))


# ──────────────────────── Comments ────────────────────────

@app.route("/projects/<int:project_id>/comments", methods=["POST"])
@login_required
def add_comment(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            project_id=project.id,
        )
        db.session.add(comment)
        # Notify project owner (unless commenting on own project)
        if project.user_id != current_user.id:
            notif = Notification(
                type="comment",
                message=f"{current_user.username} commented on your project \"{project.title}\"",
                user_id=project.user_id,
                project_id=project.id,
                actor_id=current_user.id,
            )
            db.session.add(notif)
        db.session.commit()
        flash("Comment posted!", "success")
    return redirect(url_for("project_detail", project_id=project.id))


# ──────────────────────── Collaboration Requests ────────────────────────

@app.route("/projects/<int:project_id>/collaborate", methods=["POST"])
@login_required
def request_collaboration(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)
    if project.user_id == current_user.id:
        flash("You can't collaborate on your own project.", "warning")
        return redirect(url_for("project_detail", project_id=project.id))

    existing = CollaborationRequest.query.filter_by(
        user_id=current_user.id, project_id=project.id
    ).first()
    if existing:
        flash("You've already raised your hand for this project.", "info")
        return redirect(url_for("project_detail", project_id=project.id))

    form = CollaborationForm()
    if form.validate_on_submit():
        collab = CollaborationRequest(
            message=form.message.data,
            user_id=current_user.id,
            project_id=project.id,
        )
        db.session.add(collab)
        # Notify project owner
        notif = Notification(
            type="collab_request",
            message=f"{current_user.username} wants to collaborate on your project \"{project.title}\"",
            user_id=project.user_id,
            project_id=project.id,
            actor_id=current_user.id,
        )
        db.session.add(notif)
        db.session.commit()
        flash("Collaboration request sent!", "success")
    return redirect(url_for("project_detail", project_id=project.id))


@app.route("/my-collaborations")
@login_required
def my_collaborations():
    # Requests others have made on my projects
    incoming = (
        CollaborationRequest.query
        .join(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(CollaborationRequest.created_at.desc())
        .all()
    )
    # Requests I have made
    outgoing = (
        CollaborationRequest.query
        .filter_by(user_id=current_user.id)
        .order_by(CollaborationRequest.created_at.desc())
        .all()
    )
    return render_template("projects/collaborations.html", incoming=incoming, outgoing=outgoing)


@app.route("/collaborations/<int:collab_id>/<action>", methods=["POST"])
@login_required
def handle_collaboration(collab_id, action):
    collab = db.session.get(CollaborationRequest, collab_id)
    if not collab:
        abort(404)
    if collab.project.user_id != current_user.id:
        abort(403)
    if action in ("accepted", "declined"):
        collab.status = action
        # Notify the requester
        notif = Notification(
            type=f"collab_{action}",
            message=f"Your collaboration request for \"{collab.project.title}\" was {action}",
            user_id=collab.user_id,
            project_id=collab.project_id,
            actor_id=current_user.id,
        )
        db.session.add(notif)
        db.session.commit()
        flash(f"Collaboration request {action}.", "success")
    return redirect(url_for("my_collaborations"))


# ──────────────────────── Feed ────────────────────────

@app.route("/feed")
def feed():
    page = request.args.get("page", 1, type=int)
    stage_filter = request.args.get("stage", "")
    support_filter = request.args.get("support", "")
    search_query = request.args.get("q", "").strip()
    query = Project.query

    if stage_filter:
        query = query.filter_by(stage=stage_filter)

    if support_filter:
        query = query.filter_by(support_needed=support_filter)

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Project.title.ilike(like_pattern),
                Project.description.ilike(like_pattern),
                Project.tech_stack.ilike(like_pattern),
            )
        )

    projects = query.order_by(Project.updated_at.desc()).paginate(page=page, per_page=12, error_out=False)
    return render_template(
        "projects/feed.html",
        projects=projects,
        stage_filter=stage_filter,
        support_filter=support_filter,
        search_query=search_query,
    )


# ──────────────────────── Celebration Wall ────────────────────────

@app.route("/celebration")
def celebration_wall():
    completed_projects = (
        Project.query
        .filter_by(stage="completed")
        .order_by(Project.completed_at.desc())
        .all()
    )
    return render_template("celebration.html", projects=completed_projects)


# ──────────────────────── Notifications ────────────────────────

@app.route("/notifications")
@login_required
def notifications():
    page = request.args.get("page", 1, type=int)
    notifs = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    # Mark all as read
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return render_template("notifications.html", notifications=notifs)


@app.route("/notifications/mark-read", methods=["POST"])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    flash("All notifications marked as read.", "info")
    return redirect(url_for("notifications"))


# ──────────────────────── Support / Help ────────────────────────

@app.route("/support", methods=["GET", "POST"])
def support():
    form = SupportForm()
    form.category.choices = BUG_CATEGORIES
    if current_user.is_authenticated:
        form.email.data = form.email.data or current_user.email
    if form.validate_on_submit():
        ticket = SupportTicket(
            subject=form.subject.data,
            category=form.category.data,
            description=form.description.data,
            email=form.email.data,
            user_id=current_user.id if current_user.is_authenticated else None,
        )
        db.session.add(ticket)
        db.session.commit()
        flash("Your support ticket has been submitted. We'll get back to you soon!", "success")
        return redirect(url_for("support"))
    return render_template("support.html", form=form)


# ──────────────────────── Error Handlers ────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403


# ──────────────────────── CLI Commands ────────────────────────

@app.cli.command("init-db")
def init_db():
    """Create all database tables."""
    db.create_all()
    print("Database tables created.")


@app.cli.command("seed-db")
def seed_db():
    """Seed database with sample data."""
    from werkzeug.security import generate_password_hash

    # Create sample users
    users_data = [
        {"username": "thabo_dev", "email": "thabo@example.com", "bio": "Full-stack developer from Johannesburg", "skills": "Python, React, PostgreSQL"},
        {"username": "naledi_codes", "email": "naledi@example.com", "bio": "Frontend specialist from Cape Town", "skills": "JavaScript, Vue.js, CSS"},
        {"username": "sipho_builds", "email": "sipho@example.com", "bio": "Mobile developer from Durban", "skills": "Flutter, Dart, Firebase"},
    ]

    users = []
    for data in users_data:
        user = User(
            username=data["username"],
            email=data["email"],
            password_hash=generate_password_hash("password123"),
            bio=data["bio"],
            skills=data["skills"],
        )
        db.session.add(user)
        users.append(user)

    db.session.flush()

    # Create sample projects
    projects_data = [
        {
            "title": "Township Connect",
            "description": "A platform connecting township businesses with customers. Using modern web technologies to bridge the digital divide.",
            "tech_stack": "Python, Flask, PostgreSQL, React",
            "stage": "in_progress",
            "support_needed": "frontend",
            "user": users[0],
        },
        {
            "title": "Mzansi Weather App",
            "description": "Hyper-local weather forecasting for South African communities with SMS alerts.",
            "tech_stack": "Node.js, Express, MongoDB",
            "stage": "completed",
            "support_needed": "none",
            "user": users[1],
        },
        {
            "title": "Ubuntu Learn",
            "description": "An e-learning platform focused on indigenous languages and local content.",
            "tech_stack": "Flutter, Firebase, Dart",
            "stage": "idea",
            "support_needed": "mentorship",
            "user": users[2],
        },
    ]

    for data in projects_data:
        project = Project(
            title=data["title"],
            description=data["description"],
            tech_stack=data["tech_stack"],
            stage=data["stage"],
            support_needed=data["support_needed"],
            user_id=data["user"].id,
            completed_at=datetime.now(timezone.utc) if data["stage"] == "completed" else None,
        )
        db.session.add(project)

    db.session.flush()

    # Add milestones for Township Connect
    project_tc = Project.query.filter_by(title="Township Connect").first()
    if project_tc:
        milestones = [
            Milestone(title="Database schema designed", description="Completed the ERD and created all tables", project_id=project_tc.id),
            Milestone(title="API endpoints built", description="REST API for businesses and listings", project_id=project_tc.id),
        ]
        for m in milestones:
            db.session.add(m)

    db.session.commit()
    print("Database seeded with sample data.")


if __name__ == "__main__":
    app.run(debug=True)
