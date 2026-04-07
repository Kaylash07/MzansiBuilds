from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, URLField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from models import PROJECT_STAGES, SUPPORT_TYPES, User


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(), Length(min=3, max=80, message="Username must be between 3 and 80 characters")
    ])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
        DataRequired(), Length(min=6, message="Password must be at least 6 characters")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password", message="Passwords must match")
    ])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already taken. Please choose another.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already registered.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class ProfileForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(), Length(min=3, max=80)
    ])
    email = StringField("Email", validators=[DataRequired(), Email()])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=500)])
    skills = StringField("Skills (comma separated)", validators=[Optional(), Length(max=500)])
    github_url = URLField("GitHub URL", validators=[Optional()])


class ProjectForm(FlaskForm):
    title = StringField("Project Title", validators=[
        DataRequired(), Length(min=3, max=200)
    ])
    description = TextAreaField("Description", validators=[
        DataRequired(), Length(min=10, message="Please provide at least 10 characters")
    ])
    tech_stack = StringField("Tech Stack (comma separated)", validators=[Optional(), Length(max=500)])
    repo_url = URLField("Repository URL", validators=[Optional()])
    live_url = URLField("Live URL", validators=[Optional()])
    stage = SelectField("Project Stage", choices=PROJECT_STAGES, validators=[DataRequired()])
    support_needed = SelectField("Support Needed", choices=SUPPORT_TYPES, validators=[DataRequired()])


class MilestoneForm(FlaskForm):
    title = StringField("Milestone Title", validators=[
        DataRequired(), Length(min=3, max=200)
    ])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])


class CommentForm(FlaskForm):
    content = TextAreaField("Comment", validators=[
        DataRequired(), Length(min=1, max=2000)
    ])


class CollaborationForm(FlaskForm):
    message = TextAreaField("Message (optional)", validators=[Optional(), Length(max=500)])


class SupportForm(FlaskForm):
    subject = StringField("Subject", validators=[
        DataRequired(), Length(min=5, max=200)
    ])
    category = SelectField("Category", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[
        DataRequired(), Length(min=10, message="Please provide at least 10 characters")
    ])
    email = StringField("Your Email", validators=[DataRequired(), Email()])
