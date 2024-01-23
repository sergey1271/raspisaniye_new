import sqlite3 as sql
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, insert
from sqlalchemy.orm import relationship, backref, declarative_base, Session
from sqlalchemy_utils import create_database
import os

Base = declarative_base()

# Таблица предметов и типов аудиторий/кабинетов
subjects_clrm_type = Table(
    "subjects_clrm_type",
    Base.metadata,
    Column("id_subject", Integer, ForeignKey("subjects.subject_id")),
    Column("id_clrm_type", Integer, ForeignKey("clrm_types.clrm_type_id"))
)

# Таблица учителей и предметов
teachers_subjects = Table(
    "teachers_Subjects",
    Base.metadata,
    Column("teacher_id", Integer, ForeignKey("teachers.teacher_id")),
    Column("subject_id", Integer, ForeignKey("subjects.subject_id"))
)

# Таблица "Учебный план" описывает количество уроков
# различных предметов у каждой группы/класса
studyplan = Table(
    "studyplan",
    Base.metadata,
    Column("group", Integer),
    Column("subject_is", Integer, ForeignKey("subjects.subject_id")),
    Column("lessons", Integer),
    Column("difficulty", Integer),
    Column("teacher_id", Integer, ForeignKey("teachers.teacher_id")),
    Column("separate", Integer),
    Column("technical", Integer)
)

# Таблица связывает учителей и дни их работы
work_days = Table(
    "work_days",
    Base.metadata,
    Column("teacher_id", Integer, ForeignKey("teachers.teacher_id")),
    Column("day_id", Integer, ForeignKey("days.day_id"))
)

# Класс описывает группы/классы
class classes(Base):
    __tablename__ = "classes"
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String)
    max_time = Column(Integer)

# Класс описывает аудитории/кабинеты
class classrooms(Base):
    __tablename__ = "classrooms"
    classroom_id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String)
    clrm_type_id = Column(Integer, ForeignKey("clrm_types.clrm_type_id"))
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    class_id = Column(Integer, ForeignKey("classes.class_id"))
    size = Column(Integer)

# Класс описывает предметы/дисциплины
class subjects(Base):
    __tablename__ = "subjects"
    subject_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_name = Column(String)

# Класс описывает учителей/преподавателей
class teachers(Base):
    __tablename__ = "teachers"
    teacher_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_name = Column(String)

# Класс описывает типы кабинетов/аудиторий
class clrm_types(Base):
    __tablename__ = "clrm_types"
    clrm_type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String, unique=True)

# Класс описывает дни недели
class days(Base):
    __tablename__ = "days"
    day_id = Column(Integer, primary_key=True, autoincrement=True)
    day_name = Column(String, unique=True)

# realationship(), backref  ????

class Times(Base):
    __tablename__ = "times"
    time_id = Column(Integer, primary_key=True, autoincrement=True)
    day_id = Column(Integer, ForeignKey("days.day_id"))
    start = Column(String)
    end = Column(String)
    week_id = Column(Integer)
    period = Column(Integer)

def create_db(name: str, dfile) -> None:
    # Подключение к БД
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    # Чтение файла
    f1 = open(dfile, "r")
    lines = f1.readlines()[3:-2]
    f1.close()
    for i in lines:
        num, type = i.split("\t")
        type = type.strip("\n")
        with Session(autoflush=False, bind=engine) as db:
            tp = clrm_types(type_name=type)
            try:  # пробую добавить в БД
                db.add(tp)
                db.commit()
            except:  # при ошибке возвращаю                
                db.rollback()
                pass
            # Узнаю clrm_type_id
            tp_id = db.query(clrm_types).filter(clrm_types.type_name == type).first().clrm_type_id
            # Добавляю новую аудиторию
            clrm = classrooms(number=num, clrm_type_id=tp_id)
            db.add(clrm)
            db.commit()
            # clrm_id = db.query(classrooms).filter(classrooms.number == num).first()[0]

# Функции возвращают список классов групп (классов) / список их ID
def get_classes(name: str):
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(classes).all()
        return cl
def get_classes_id(name: str):
    cl = get_classes(name)
    cl_id = list()
    for i in cl:
        cl_id.append(i.class_id)
    return cl_id

# Функции возвращают список классов кабинетов (аудитороий) / список их ID
def get_classrooms(name: str):
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(classrooms).all()
        return cl
def get_classrooms_id(name: str):
    cl = get_classrooms(name)
    clrms_id = list()
    for i in cl:
        clrms_id.append(i.classroom_id)
    return clrms_id

# Функции возвращают список классов групп (классов) / список их ID
def get_teachers(name: str, is_list=False):
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(teachers).all()
    if is_list:
        return cl
    r = dict()
    for i in cl:
        r[i.teacher_id] = i
    return r

def get_teachers_id(name: str):
    tch = get_teachers(name)
    tch_id = list()
    for i in tch:
        tch_id.append(i.teacher_id)
    return tch_id

def get_times(name: str):
    res = list()
    for i in range(8):
        res.append(list())
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(Times).all()
    for i in cl:
        res[i.day_id].append(i)
    return res

def get_times_id(name: str):
    times_id = list()
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(Times).all()
    for i in cl:
        times_id.append(i.time_id)
    return times_id

def get_studyplan(name: str):
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(studyplan).all()
        return cl

def get_days(name: str):
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        t = db.query(Times).all()
    days = list()
    for i in t:
        if not i.day_id in days:
            days.append(i.day_id)
    return days

def get_groups_for_count_lessons(name: str)->dict:
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(classes).all()
        t = db.query(Times).all()
    days = list()
    for i in t:
        if not i.day_id in days:
            days.append(i.day_id)
    groups = dict()
    for i in cl:
        groups[i.class_id] = dict()
        for d in days:
            groups[i.class_id][d]=dict()
            # в словаре будут все времена
    return groups

def get_teachers_for_count(name: str)->dict:
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(teachers).all()
    tchrs = dict()
    for i in cl:
        tchrs[i.teacher_id] = dict()
    return tchrs

def get_classrooms_by_subject(name: str, s: int):
    # s -- id предмета
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        query = subjects_clrm_type.select().where(
        subjects_clrm_type.c.id_subject == s)
        q1 = connection.execute(query).fetchone()
    t = q1[1]
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(classrooms).filter(classrooms.clrm_type_id==t).all()
    clrms_ids = list()
    for c in cl:
        clrms_ids.append(c.classroom_id)
    return clrms_ids
def get_type_id_by_subject(name: str, s: int):
    # s -- id предмета
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        query = subjects_clrm_type.select().where(
        subjects_clrm_type.c.id_subject == s)
        q1 = connection.execute(query).fetchone()
    t = q1[1]
    return t
def get_types(name: str):
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(clrm_types).all()
    r = list()
    for i in cl:
        r.append(i.clrm_type_id)
    return r

def get_classrooms_by_type_id(name: str, t: int):
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(classrooms).filter(classrooms.clrm_type_id==t).all()
    r = list()
    for i in cl:
        r.append(i.classroom_id)
    return r

def get_max_time(name: str, g: int):
    engine = create_engine("sqlite:///" + name)
    Base.metadata.create_all(engine)
    with Session(autoflush=False, bind=engine) as db:
        cl = db.query(classes).filter(classes.class_id==g).first()
    return cl.max_time
# print(get_classrooms_by_type_id("1234.db", 1))
    