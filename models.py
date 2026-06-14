from database import database as db
from flask_login import UserMixin
from datetime import datetime

# ---------------------------------------------------------------------------
# Tabelas de Associação (Many-to-Many)
# ---------------------------------------------------------------------------

team_members = db.Table(
    "team_members",
    db.Column("fk_employee", db.Integer, db.ForeignKey("employee.pk_id_employee", ondelete="CASCADE"), nullable=False),
    db.Column("fk_team",     db.Integer, db.ForeignKey("team.pk_id_team", ondelete="CASCADE"), nullable=False),
    db.PrimaryKeyConstraint("fk_employee", "fk_team", name="pk_team_members"),
)

employee_skills = db.Table(
    "employee_skills",
    db.Column("fk_employee", db.Integer, db.ForeignKey("employee.pk_id_employee", ondelete="CASCADE"), nullable=False),
    db.Column("fk_skill",    db.Integer, db.ForeignKey("skill.pk_id_skill", ondelete="CASCADE"), nullable=False),
    db.PrimaryKeyConstraint("fk_employee", "fk_skill", name="pk_employee_skills"),
)

project_teams = db.Table(
    "project_teams",
    db.Column("fk_team",    db.Integer, db.ForeignKey("team.pk_id_team", ondelete="CASCADE"), nullable=False),
    db.Column("fk_project", db.Integer, db.ForeignKey("project.pk_id_project", ondelete="CASCADE"), nullable=False),
    db.PrimaryKeyConstraint("fk_team", "fk_project", name="pk_project_teams"),
)

# ---------------------------------------------------------------------------
# User  (ex-Usuario)
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = "user"

    pk_id_user      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_user       = db.Column(db.String(120), nullable=False)
    email_user      = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_user   = db.Column(db.String(255), nullable=False)
    type_user       = db.Column(db.String(30), nullable=False, default="employee")
    status_user     = db.Column(db.String(20), nullable=False, default="active")
    github_key_user = db.Column(db.String(255), nullable=True)
    created_at_user = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    admin    = db.relationship("Admin",     back_populates="user", uselist=False, cascade="all, delete-orphan")
    client   = db.relationship("Client",   back_populates="user", uselist=False, cascade="all, delete-orphan")
    employee = db.relationship("Employee", back_populates="user", uselist=False, cascade="all, delete-orphan")
    logs     = db.relationship("Log",     back_populates="user", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="user", cascade="all, delete-orphan")

    def get_id(self):
        return str(self.pk_id_user)

    def __repr__(self):
        return f"<User pk_id_user={self.pk_id_user} email_user={self.email_user!r}>"


# ---------------------------------------------------------------------------
# Admin  (ex-Admin)
# ---------------------------------------------------------------------------

class Admin(db.Model):
    __tablename__ = "admin"

    pk_id_admin = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_user     = db.Column(db.Integer, db.ForeignKey("user.pk_id_user", ondelete="CASCADE"), nullable=False, unique=True)
    level_admin = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship("User", back_populates="admin")

    __table_args__ = (db.Index("ix_admin_fk_user", "fk_user"),)

    def __repr__(self):
        return f"<Admin pk_id_admin={self.pk_id_admin} fk_user={self.fk_user}>"


# ---------------------------------------------------------------------------
# Client  (ex-Cliente)
# ---------------------------------------------------------------------------

class Client(db.Model):
    __tablename__ = "client"

    pk_id_client  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_user       = db.Column(db.Integer, db.ForeignKey("user.pk_id_user", ondelete="CASCADE"), nullable=False, unique=True)
    company_client = db.Column(db.String(200), nullable=True)
    cnpj_client    = db.Column(db.String(18),  nullable=True, unique=True)
    phone_client   = db.Column(db.String(20),  nullable=True)

    user     = db.relationship("User",    back_populates="client")
    projects = db.relationship("Project", back_populates="client", cascade="all, delete-orphan")

    __table_args__ = (
        db.Index("ix_client_fk_user",     "fk_user"),
        db.Index("ix_client_cnpj_client", "cnpj_client"),
    )

    def __repr__(self):
        return f"<Client pk_id_client={self.pk_id_client} company_client={self.company_client!r}>"


# ---------------------------------------------------------------------------
# Skill  (ex-Habilidade)
# ---------------------------------------------------------------------------

class Skill(db.Model):
    __tablename__ = "skill"

    pk_id_skill       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_skill        = db.Column(db.String(100), nullable=False, unique=True)
    description_skill = db.Column(db.Text, nullable=True)

    employees = db.relationship("Employee", secondary=employee_skills, back_populates="skills")

    def __repr__(self):
        return f"<Skill pk_id_skill={self.pk_id_skill} name_skill={self.name_skill!r}>"


# ---------------------------------------------------------------------------
# Employee  (ex-Funcionario)
# ---------------------------------------------------------------------------

class Employee(db.Model):
    __tablename__ = "employee"

    pk_id_employee = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_user        = db.Column(db.Integer, db.ForeignKey("user.pk_id_user", ondelete="CASCADE"), nullable=False, unique=True)
    role_employee  = db.Column(db.String(100), nullable=True)

    user   = db.relationship("User",     back_populates="employee")
    teams  = db.relationship("Team",     secondary=team_members,    back_populates="employees")
    skills = db.relationship("Skill",    secondary=employee_skills, back_populates="employees")

    __table_args__ = (db.Index("ix_employee_fk_user", "fk_user"),)

    def __repr__(self):
        return f"<Employee pk_id_employee={self.pk_id_employee} role_employee={self.role_employee!r}>"


# ---------------------------------------------------------------------------
# Team  (ex-Equipes)
# ---------------------------------------------------------------------------

class Team(db.Model):
    __tablename__ = "team"

    pk_id_team       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_team        = db.Column(db.String(120), nullable=False)
    description_team = db.Column(db.Text, nullable=True)
    status_team      = db.Column(db.String(20), nullable=False, default="active")
    funcao           = db.Column(db.String(250), nullable=True)
    lider_equipe     = db.Column(db.Integer, nullable=True)

    employees = db.relationship("Employee", secondary=team_members,  back_populates="teams")
    projects  = db.relationship("Project",  secondary=project_teams, back_populates="teams")

    def __repr__(self):
        return f"<Team pk_id_team={self.pk_id_team} name_team={self.name_team!r}>"


# ---------------------------------------------------------------------------
# Project  (ex-Projeto)
# ---------------------------------------------------------------------------

class Project(db.Model):
    __tablename__ = "project"

    pk_id_project      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_client          = db.Column(db.Integer, db.ForeignKey("client.pk_id_client", ondelete="SET NULL"), nullable=True)
    name_project       = db.Column(db.String(200), nullable=False)
    description_project = db.Column(db.Text, nullable=True)
    status_project     = db.Column(db.String(20), nullable=False, default="open")
    start_date_project = db.Column(db.Date, nullable=True)
    end_date_project   = db.Column(db.Date, nullable=True)
    orcamento          = db.Column(db.Float, nullable=True, default=0.0)

    client       = db.relationship("Client",      back_populates="projects")
    teams        = db.relationship("Team",        secondary=project_teams, back_populates="projects")
    requirements = db.relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    logs         = db.relationship("Log",         back_populates="project", cascade="all, delete-orphan")
    documents    = db.relationship("Document",    back_populates="project", cascade="all, delete-orphan")
    diagrams     = db.relationship("Diagram",     back_populates="project", cascade="all, delete-orphan")
    gallery      = db.relationship("Gallery",     back_populates="project", cascade="all, delete-orphan")
    comments     = db.relationship("Comment",     back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        db.Index("ix_project_fk_client",      "fk_client"),
        db.Index("ix_project_status_project", "status_project"),
    )

    def __repr__(self):
        return f"<Project pk_id_project={self.pk_id_project} name_project={self.name_project!r}>"


# ---------------------------------------------------------------------------
# Requirement  (ex-Requisito)
# ---------------------------------------------------------------------------

class Requirement(db.Model):
    __tablename__ = "requirement"

    pk_id_requirement       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_project              = db.Column(db.Integer, db.ForeignKey("project.pk_id_project", ondelete="CASCADE"), nullable=False)
    fk_team                 = db.Column(db.Integer, db.ForeignKey("team.pk_id_team", ondelete="SET NULL"), nullable=True)
    name_requirement        = db.Column(db.String(200), nullable=False)
    description_requirement = db.Column(db.Text, nullable=True)
    type_requirement        = db.Column(db.String(50), nullable=True)
    status_requirement      = db.Column(db.String(20), nullable=False, default="Pendente")

    project = db.relationship("Project", back_populates="requirements")
    team    = db.relationship("Team", backref="requirements")

    __table_args__ = (
        db.Index("ix_requirement_fk_project",         "fk_project"),
        db.Index("ix_requirement_status_requirement", "status_requirement"),
    )

    def __repr__(self):
        return f"<Requirement pk_id_requirement={self.pk_id_requirement} name_requirement={self.name_requirement!r}>"


# ---------------------------------------------------------------------------
# Log  (ex-Registro)
# ---------------------------------------------------------------------------

class Log(db.Model):
    __tablename__ = "log"

    pk_id_log       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_user         = db.Column(db.Integer, db.ForeignKey("user.pk_id_user", ondelete="SET NULL"), nullable=True)
    fk_project      = db.Column(db.Integer, db.ForeignKey("project.pk_id_project", ondelete="CASCADE"), nullable=True)
    fk_team         = db.Column(db.Integer, db.ForeignKey("team.pk_id_team", ondelete="SET NULL"), nullable=True)
    description_log = db.Column(db.Text, nullable=False)
    date_log        = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    type_log        = db.Column(db.String(50), nullable=True)

    user    = db.relationship("User",    back_populates="logs")
    project = db.relationship("Project", back_populates="logs")
    team    = db.relationship("Team", backref="logs")

    __table_args__ = (
        db.Index("ix_log_fk_user",    "fk_user"),
        db.Index("ix_log_fk_project", "fk_project"),
        db.Index("ix_log_fk_team",    "fk_team"),
        db.Index("ix_log_date_log",   "date_log"),
    )

    def __repr__(self):
        return f"<Log pk_id_log={self.pk_id_log} type_log={self.type_log!r} date_log={self.date_log}>"


# ---------------------------------------------------------------------------
# Document  (ex-Documento)
# ---------------------------------------------------------------------------

class Document(db.Model):
    __tablename__ = "document"

    pk_id_document       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_project           = db.Column(db.Integer, db.ForeignKey("project.pk_id_project", ondelete="CASCADE"), nullable=False)
    fk_team              = db.Column(db.Integer, db.ForeignKey("team.pk_id_team", ondelete="SET NULL"), nullable=True)
    name_document        = db.Column(db.String(200), nullable=False)
    path_document        = db.Column(db.String(500), nullable=False)
    type_document        = db.Column(db.String(50),  nullable=True)
    upload_date_document = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    project = db.relationship("Project", back_populates="documents")
    team    = db.relationship("Team", backref="documents")

    __table_args__ = (
        db.Index("ix_document_fk_project", "fk_project"),
        db.Index("ix_document_fk_team",    "fk_team"),
    )

    def __repr__(self):
        return f"<Document pk_id_document={self.pk_id_document} name_document={self.name_document!r}>"


# ---------------------------------------------------------------------------
# Diagram  (ex-Diagrama)
# ---------------------------------------------------------------------------

class Diagram(db.Model):
    __tablename__ = "diagram"

    pk_id_diagram = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_project    = db.Column(db.Integer, db.ForeignKey("project.pk_id_project", ondelete="CASCADE"), nullable=False)
    fk_team       = db.Column(db.Integer, db.ForeignKey("team.pk_id_team", ondelete="SET NULL"), nullable=True)
    name_diagram  = db.Column(db.String(200), nullable=False)
    type_diagram  = db.Column(db.String(50),  nullable=True)
    path_diagram  = db.Column(db.String(500), nullable=False)

    project = db.relationship("Project", back_populates="diagrams")
    team    = db.relationship("Team", backref="diagrams")

    __table_args__ = (
        db.Index("ix_diagram_fk_project", "fk_project"),
        db.Index("ix_diagram_fk_team",    "fk_team"),
    )

    def __repr__(self):
        return f"<Diagram pk_id_diagram={self.pk_id_diagram} name_diagram={self.name_diagram!r}>"


# ---------------------------------------------------------------------------
# Gallery  (ex-Galeria)
# ---------------------------------------------------------------------------

class Gallery(db.Model):
    __tablename__ = "gallery"

    pk_id_gallery = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_project    = db.Column(db.Integer, db.ForeignKey("project.pk_id_project", ondelete="CASCADE"), nullable=False)
    fk_team       = db.Column(db.Integer, db.ForeignKey("team.pk_id_team", ondelete="SET NULL"), nullable=True)
    path_gallery  = db.Column(db.String(500), nullable=False)
    date_gallery  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    project = db.relationship("Project", back_populates="gallery")
    team    = db.relationship("Team", backref="galleries")

    __table_args__ = (
        db.Index("ix_gallery_fk_project", "fk_project"),
        db.Index("ix_gallery_fk_team",    "fk_team"),
    )

    def __repr__(self):
        return f"<Gallery pk_id_gallery={self.pk_id_gallery} path_gallery={self.path_gallery!r}>"


# ---------------------------------------------------------------------------
# Comment  (ex-Comentario)
# ---------------------------------------------------------------------------

class Comment(db.Model):
    __tablename__ = "comment"

    pk_id_comment   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_user         = db.Column(db.Integer, db.ForeignKey("user.pk_id_user", ondelete="SET NULL"), nullable=True)
    fk_project      = db.Column(db.Integer, db.ForeignKey("project.pk_id_project", ondelete="CASCADE"), nullable=False)
    fk_team         = db.Column(db.Integer, db.ForeignKey("team.pk_id_team", ondelete="SET NULL"), nullable=True)
    content_comment = db.Column(db.Text, nullable=False)
    date_comment    = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user    = db.relationship("User",    back_populates="comments")
    project = db.relationship("Project", back_populates="comments")
    team    = db.relationship("Team", backref="comments")

    __table_args__ = (
        db.Index("ix_comment_fk_user",     "fk_user"),
        db.Index("ix_comment_fk_project",  "fk_project"),
        db.Index("ix_comment_fk_team",     "fk_team"),
        db.Index("ix_comment_date_comment", "date_comment"),
    )

    def __repr__(self):
        return f"<Comment pk_id_comment={self.pk_id_comment} fk_user={self.fk_user} date_comment={self.date_comment}>"
