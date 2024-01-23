from database_create import get_times, get_classrooms, get_studyplan, \
    get_teachers, get_groups_for_count_lessons, get_days, get_classrooms_by_subject, \
    get_type_id_by_subject, get_types, get_classrooms_by_type_id, get_max_time
import random
DATABASE = "1234.db"
class Time:
    def __init__(self, id: int, week: int, day: int, period: int):
        self.id = id
        self.week = week  # id недели. Разные недели?
        self.day = day  # id дня недели
        self.period = period  # id пары

class Classroom:
    def __init__(self, id: int, size: int, type_id: int, lab=0):
        # size - сколько групп вмещает аудитория
        # lab - id предмета лаборатории(в школе) / кафедры(?)
        # подумать над способом хранения
        self.id = id
        self.size = size
        self.lab = lab
        self.type_id = type_id
        
class Teacher:
    def __init__(self, teacher_id: int, subjects: list, workdays: list, groups: list):
        self.id = teacher_id
        self.subjects = subjects
        self.workdays = workdays
        self.groups = groups

class Lesson:
    def __init__(self, teacher: int, subject: int, groups, is_stream: int, \
        is_half: int, hours: int, intensity: int, hours_inone: int, l_type: int, clrms: int):
        # hours - длителность цикла (число занятий)
        # intensity - интенсивность занятий в цикле: если 1,
            # то занятия в цикле проводятся 1 раз в неделю; если же 2,
            # то — 1 раз в 2 недели;
        # hours_inone - длина (число пар) одного занятия
        # l_type - параметр, определяющий вид занятия
        # clrms - код допустимого подмножества аудиторий
        self.teacher = teacher
        self.subject = subject
        self.groups = groups
        self.is_stream = is_stream
        self.is_half = is_half
        self.hours = hours
        self.intensity = intensity
        self.hours_inone = hours_inone
        self.l_type = l_type
        self.clrms = clrms



class Subject:
    def __init__(self, subject_id: int):
        self.subject_id = subject_id

class Group:  # НЕ НАДО?, есть учебный план, Lesson?
    def __init__(self, subjects: list):
        self.subjects = subjects

print("Чтение из БД времен занятий...")

times = list()  # Периоды - времена занятий
for j in get_times(DATABASE):
    for i in j:
        t = Time(id=i.time_id, week=i.week_id, day=i.day_id, period=i.period)
        times.append(t)

print("Чтение из БД аудиторий...")

classrooms = list()  # Аудитории
for i in get_classrooms(DATABASE):
    c = Classroom(id=i.classroom_id, size=i.size, type_id=i.clrm_type_id)
    classrooms.append(c)

print("Чтение из БД преподавателей...")

teachers_models = dict()
for i in get_teachers(DATABASE, True):
    t = Teacher(i.teacher_id, 0, 0, 0)
    teachers_models[i.teacher_id] = t



def create_models_classrooms_by_type_id(name: str, t: str):
    clrms_ids = get_classrooms_by_type_id(name, t)
    clrms = list()
    for cl in classrooms:
        if cl.type_id == t:
            clrms.append(cl)
    return clrms

print("Распределение аудиторий по типам...")

types_dict = dict()
for i in get_types(DATABASE):
    types_dict[i]=create_models_classrooms_by_type_id(DATABASE, i)


print("Создание объектов ЗАНЯТИЕ...")

teachers = get_teachers(DATABASE)  # словарь id - объект 'учитель'
lessons = list()
for i in get_studyplan(DATABASE):
    # studyplan - таблица, а не класс!!!
    l = Lesson(subject=i[1], teacher=teachers_models[teachers[i[4]].teacher_id], \
        groups=[i[0]], is_stream=0, is_half=0, hours=i[2], \
        intensity=1, hours_inone=1, l_type=1, clrms=get_type_id_by_subject(DATABASE, i[1]))
    lessons.append(l)



def get_classrooms_for_count(times: list):
    d = dict()
    for a in classrooms:
        d[a] = dict()
        for t in times:
            d[a][t] = 0
    return d
    
def get_teachers_for_count(times: list):
    d = dict()
    for a in teachers_models.values():
        d[a] = dict()
        for t in times:
            d[a][t] = 0
    return d

# Особь - занятие + время и занятие + аудитория

print("Создание ОСОБЕЙ...")

k = 7  # количество особей
entities = list()
for i in range(k):
    start_score = 0
    e = [dict(), dict(), start_score]
    lessons1 = lessons.copy()
    for i in range(len(lessons)):
        if lessons1:  # занятия не повторяются
            index = random.randrange(len(lessons1))
            l = lessons1.pop(index)
        # подумать над сдвоенными
        # и один раз в две недели
            e[0][l] = list()
            e[1][l] = list()
            for j in range(l.hours) :
                t = random.choice(times)
                c = random.choice(types_dict[l.clrms]) # !!! ДОБАВИТЬ КОД ДОПУСТИМОГО ПОДМНОЖЕСТВА !!!
                e[0][l].append(t)
                e[1][l].append(c)
            # e[0].append({l: t})  # занятия к времени
            # e[1].append({l: c})  # занятия к аудиториям
    entities.append(e)

# for e in entities:
#     print("НАЧАЛО ОСОБИ")
#     for k, v in e[0].items():
#         print(f'{k}: {v}')
#     for k, v in e[1].items():
#         print(f'{k}: {v}')
#     print("КОНЕЦ ОСОБИ")

print("Распределение времен занятий по дням недели...")

times_days = dict()
for d in get_days(DATABASE):
    times_days[d] = dict()
for i in times:
    times_days[i.day][i] = 0


print("Подсчет кол-ва пар у каждой группы одновременно...")

groups_count = list()
c_entities = entities.copy()
for e in c_entities:
    count_dict = get_groups_for_count_lessons(DATABASE)
    for i in count_dict.keys():  # перебираю группы
            for t in times:# перебираю все времена занятий
                count_dict[i][t.day][t] = 0  # задаю изначальное значение 0
    for c_lesson, c_time in e[0].items():
        c_groups = c_lesson.groups
        c_half = 1 if c_lesson.is_half == 0 else 0.5
        for g in c_groups:
            for t in c_time:
                count_dict[g][t.day][t] += c_half # добавляю 1 или 0.5 (половина группы)
    groups_count.append(count_dict)
# СРАЗУ ТРИ ПРОВЕРКИ: НА НАКЛАДКИ (значение не более 1), ОКОН и МАКС. КОЛ-ВА ПАР В ДЕНЬ
# !!! НУЖНО ДОБАВИТЬ ПРОВЕРКУ ЧЕТНОСТИ/НЕЧЕТНОСТИ НЕДЕЛИ !!!
# Половинчатые занятия будут в одно время у обоих    групп? Нет, уйдет при проверке учителей
# https://translated.turbopages.org/proxy_u/en-ru.ru.decb8fcb-655db9c4-781d4731-74722d776562/https/stackoverflow.com/questions/2053021/is-the-order-of-a-python-dictionary-guaranteed-over-iterations

# for k, v in count_dict.items():
#     print(f'{k}: {v}' + "\n")

                
print("Подсчет кол-ва пар в каждой аудитории одновременно...")

clrms_count = list()
c_entities = entities.copy()
for e in c_entities:
    clrms_dict = get_classrooms_for_count(times)
    for c_lesson, c_classroom in e[1].items():
        c_time = e[0][c_lesson]
        for i in range(len(c_classroom)): # чтобы множества 
        # соотносились 1 к 1 [c1, c2] и [t1, t2] не было пары (c1, t2) и (c2, t1)
            clrms_dict[c_classroom[i]][c_time[i]] += 1
    clrms_count.append(clrms_dict)

# for k, v in clrms_dict.items():
#     print(f'{k}: {v}' + "\n")
print("Подсчет кол-ва пар у каждого преподавателя одновременно...")

teachers_count = list()
c_entities = entities.copy()
for e in c_entities:
    teachers_dict = get_teachers_for_count(times)
    for c_lesson, c_time in e[0].items():
        for t in c_time:
            teachers_dict[c_lesson.teacher][t] += 1
    teachers_count.append(teachers_dict)

# for k, v in teachers_dict.items():
#     print(f'{k}: {v}', "\n")
# print(teachers_dict, "\n")
print("Проверка накладок у групп...")

fine_for_groups = 1
for i in range(len(entities)):
    for g in groups_count[i].keys():
        for d in groups_count[i][g].keys():
            for t in groups_count[i][g][d].keys():
                if groups_count[i][g][d][t] > 1:
                    entities[i][2] += fine_for_groups * (groups_count[i][g][d][t]-1) # штраф за одновременно два урока у группы

print("Проверка накладок аудиторий...")

fine_for_classrooms = 1
for i in range(len(entities)):
    for cl in classrooms:
        for t in times:
            if clrms_count[i][cl][t] > 1:
                entities[i][2] += fine_for_classrooms * (clrms_count[i][cl][t]-1)  # штраф за накладки аудиторий

print("Проверка накладок у учителей...")

fine_for_teachers = 1
for i in range((len(entities))):
    for teach in teachers_models.values():
        for t in times:
            if teachers_count[i][teach][t] > 1:
                entities[i][2] += fine_for_teachers * (teachers_count[i][teach][t]-1)  # штраф за накладки exbntktq

print("Проверка наличия окон у студентов...")
flag = bool()
fine_for_blank_students = 1
for i in range(len(entities)):
    for g in groups_count[i].keys():
        for d in groups_count[i][g].keys():
            flag_first = False
            count_blank = 0
            count_total = 0
            for t in groups_count[i][g][d].keys():
                if groups_count[i][g][d][t] >= 1 and not flag_first:
                    flag_first = True
                if flag_first:
                    if groups_count[i][g][d][t] < 1:
                        count_blank += 1
                        count_total += 1
                    if groups_count[i][g][d][t] >= 1:
                        count_blank = 0
            # print(groups_count[i][g][d])
            # print(count_total-count_blank)
            bl = count_total - count_blank
            entities[i][2] += bl * fine_for_blank_students
            # В отличии от формулы в статье повторно накладки НЕ учитываются

print("Проверка ограничения на кол-во пар в день...")
fine_for_overtime = 1
for i in range(len(entities)):
    for g in groups_count[i].keys():
        m = get_max_time(DATABASE, g)
        for d in groups_count[i][g].keys():
            c = 0
            for t in groups_count[i][g][d].keys():
                if groups_count[i][g][d][t] >= 1:
                    c += 1
            if c > m:  # добавить импорт из таблицы - добавить колонку с макс.кол-вом
                entities[i][2] += (c-m) * fine_for_overtime
            # print(f'{g}, {c}, {m}')
print("ШТРАФЫ:")

for e in range(len(entities)):
    print(f'{e+1}: {entities[e][2]}')  # штраф от 220 до 280, чаще 250 +- 10 (240 - 260)