import sqlalchemy
import os
import dotenv
from faker import Faker
import numpy as np
from random import choice

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True, pool_pre_ping=True)

with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""
    DROP TABLE IF EXISTS public.employees;
    DROP TABLE IF EXISTS public.dept;
    DROP TABLE IF EXISTS public.history;

    create table
    public.dept(
        dept_id BIGINT GENERATED BY DEFAULT AS IDENTITY, 
        created_at timestamp with time zone not null default now(),
        dept_name TEXT NULL,
        base_pay FLOAT,
        dept_populus INT
        
    ) tablespace pg_default;


    create table 
    public.employees(
        id BIGINT generated by default as identity,
        hire_date timestamp with time zone not null default now(),
        name text null,
        skills text null,
        pay REAL,
        department text null,
        level integer
        
    ) tablespace pg_default;


    create table 
    public.history(
        ledger_id BIGINT generated by default as identity,
        created_at timestamp with time zone not null default now(),
        emp_name text null,
        days_employed bigint,
        day_wage float,
        in_dept text null,
        emp_id bigint
        
    ) tablespace pg_default;
    """))
    

num_users = 1000
fake = Faker()

TECH_DEPARTMENTS = [
  'Frontend Engineering', 'Backend Engineering', 'Full Stack Development', 'Mobile Development', 'DevOps Engineering', 'Site Reliability Engineering', 'Systems Engineering', 'Embedded Systems', 'Gaming Engineering', 'Firmware Engineering',
  'Data Engineering', 'Data Science', 'Machine Learning Engineering', 'Business Intelligence', 'Data Analytics', 'Artificial Intelligence', 'Natural Language Processing', 'Computer Vision Engineering', 'Predictive Analytics', 'Big Data Engineering',
  'Information Security', 'Network Engineering', 'Cloud Infrastructure', 'Platform Engineering', 'Security Operations', 'Cybersecurity', 'Identity & Access Management', 'Infrastructure Automation', 'Network Security', 'Cloud Security',
  'Blockchain Development', 'AR/VR Development', 'IoT Engineering', 'Quantum Computing', 'Robotics Engineering', 'Autonomous Systems', '5G Engineering', 'Cryptography Engineering', 'High Performance Computing', 'Edge Computing',
  'Quality Assurance', 'QA Automation', 'Technical Support', 'IT Operations', 'Solutions Architecture', 'Database Administration', 'Release Engineering', 'Production Engineering', 'Technical Program Management', 'API Development'
]

SKILLS = [
   'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Go', 'Rust', 'TypeScript', 'SQL', 'R', 'MATLAB', 'Scala', 'Perl', 'Assembly', 'COBOL',
   'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring Boot', 'ASP.NET', 'Express.js', 'HTML5', 'CSS3', 'jQuery', 'Bootstrap', 'WordPress', 'GraphQL', 'REST APIs',
   'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI/CD', 'Terraform', 'Ansible', 'Puppet', 'Chef', 'VMware', 'OpenStack',
   'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Data Analysis', 'Natural Language Processing', 'Computer Vision', 'Neural Networks', 'Reinforcement Learning', 'Statistical Analysis', 'Big Data', 'Data Mining',
   'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'SQL Server', 'Redis', 'Cassandra', 'DynamoDB', 'Neo4j', 'Elasticsearch',
   'Git', 'SVN', 'Mercurial', 'JIRA', 'Confluence', 'Trello', 'Slack', 'Microsoft Teams', 'Bitbucket',
   'Agile', 'Scrum', 'Kanban', 'DevOps', 'TDD', 'BDD', 'CI/CD', 'Microservices', 'SOA', 'Design Patterns',
   'Leadership', 'Communication', 'Problem Solving', 'Team Management', 'Project Management', 'Critical Thinking', 'Time Management', 'Mentoring', 'Public Speaking', 'Conflict Resolution',
   'Cybersecurity', 'Penetration Testing', 'Encryption', 'Network Security', 'Security Auditing', 'Ethical Hacking', 'OWASP', 'Security Compliance',
   'iOS Development', 'Android Development', 'React Native', 'Flutter', 'Xamarin', 'Mobile UI Design', 'App Store Optimization'
]

departments_list = []
with engine.begin() as conn:
   print("Creating departments...")
   for dept in TECH_DEPARTMENTS:
       base_pay = fake.pyfloat(positive=True, min_value=30000, max_value=150000)
       conn.execute(
           sqlalchemy.text("INSERT INTO dept (dept_name, base_pay, dept_populus) VALUES (:dept_name, :base_pay, :dept_populus)"),
           {"dept_name": dept, "base_pay": base_pay, "dept_populus": 0}
       )
       departments_list.append((dept, base_pay))

with engine.begin() as conn:
   print("Creating employees and history...")
   for i in range(num_users):
       if (i % 100 == 0):
           print(i)
       
       dept_name, base_pay = choice(departments_list)
       emp_id = fake.pyint()
       profile = fake.profile()
       skills = ", ".join(fake.random_elements(elements=SKILLS, length=fake.random_int(min=2, max=5), unique=True))
       pay = fake.pyfloat(positive=True, min_value=base_pay, max_value=180000)
       day_wage = base_pay / 260
       level = fake.pyint(min_value=-2, max_value=12)
       days_employed = fake.pyint(min_value=1, max_value=10000)

       conn.execute(
           sqlalchemy.text("UPDATE dept SET dept_populus = dept_populus + 1 WHERE dept_name = :dept_name"),
           {"dept_name": dept_name}
       )

       conn.execute(
           sqlalchemy.text("INSERT INTO employees (name, skills, pay, department, level) VALUES (:name, :skills, :pay, :department, :level)"),
           {"name": profile['name'], "skills": skills, "pay": pay, "department": dept_name, "level": level}
       )

       conn.execute(
           sqlalchemy.text("INSERT INTO history (emp_name, days_employed, day_wage, in_dept, emp_id) VALUES (:emp_name, :days_employed, :day_wage, :in_dept, :emp_id)"),
           {"emp_name": profile['name'], "days_employed": days_employed, "day_wage": day_wage, "in_dept": dept_name, "emp_id": emp_id}
       )