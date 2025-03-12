# Imports
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError

# Create Database
engine = create_engine("sqlite:///tasks.db", echo = True)    # Naming database as tasks.db
Base = declarative_base()
Session = sessionmaker(bind = engine)
session = Session()

# Database Models (User / Tasks)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable = False)
    email = Column(String, nullable = False, unique = True)
    tasks = relationship('Task', back_populates='user', cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable = True)
    description = Column(String)
    users = Column(Integer, ForeignKey{'users.id'})
    user = relationship('User', back_populates='tasks')

Base.metadata.create_all(engine)

#Utlity functions
def get_user_by_email(email):
    return session.query(User).filter_by(email=email).first()

def confirm_action(prompt:str) -> bool:
    return input(f"{prompt} (yes/no): ").strip().lower() == 'yes'

# CRUD
def add_user():
    name, email = input("Enter user name: "), input("Enter the email: ")
    if get_user_by_email(email):
        print(f"User aldready exists")
        return

    try:
        session.add(User(name=name, email = email))
        session.commit()
        print(f"User: {name} added!")
    except IntegrityError:
        session.rollback()
        print(f"Error")

def add_task():
    email = input("Enter the email of the user to add tasks: ")
    user = get_user_by_email(email)

    if not user:
        print(f"No user found with that email")
        return

    title, description = input("Enter the title: "), input("Enter the description: ")
    session.add(Task(title = title, description = description))
    session.commit()

    print(f"Added to the database: {title}: {description}")

# Querying the database
def query_users():
    for user in session.query(User).all():
        print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")
    
def query_tasks():
    email = input("Enter the email of the user: ")
    user = get_user_by_email(email)

    if not user:
        print("There was no user with that email")
        return
    
    for task in user.tasks:
        print(f"Task ID: {task.id}, Title: {task.title}")

def update_user():
    email = input("Email of who you want to update: ")
    user = get_user_by_email(email)
    if not user:
        print("There is no user with that email")
        return
    
    user.name = input("Enter a new name for the user: ") or user.name
    user.email = input("Enter new email: ") or user.email

    session.commit()
    print("User has been updated")

def delete_user():
    email = input("Email of who you want to update: ")
    user = get_user_by_email(email)
    if not user:
        print("There is no user with that email")
        return
    
    if confirm_action(f"Are you sure you want to delete: {user.name}?"):
        session.delete(user)
        session.commit()
        print("User has been deleted")
