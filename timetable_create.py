from database_create import get_times, get_classrooms, get_studyplan, \
    get_teachers, get_groups_for_count_lessons, get_days, get_classrooms_by_subject, \
    get_type_id_by_subject, get_types, get_classrooms_by_type_id, get_max_time, \
    get_classes_id, get_classes
import random, time
from random import shuffle
from export_timetable import export_timetable
start_time = time.time()
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

def get_classrooms_for_count(times: list, classrooms):
    d = dict()
    for a in classrooms:
        d[a] = dict()
        for t in times:
            d[a][t] = 0
    return d
    
def get_teachers_for_count(times: list, teachers_models):
    d = dict()
    for a in teachers_models.values():
        d[a] = dict()
        for t in times:
            d[a][t] = 0
    return d

def create_models_classrooms_by_type_id(name: str, t: str, classrooms):
    clrms_ids = get_classrooms_by_type_id(name, t)
    clrms = list()
    for cl in classrooms:
        if cl.type_id == t:
            clrms.append(cl)
    return clrms

def read_time(DATABASE):
    print("Чтение из БД времен занятий...")
    times = list()  # Периоды - времена занятий
    for j in get_times(DATABASE):
        for i in j:
            t = Time(id=i.time_id, week=i.week_id, day=i.day_id, period=i.period)
            times.append(t)
    return times


def read_classrooms(DATABASE):
    print("Чтение из БД аудиторий...")
    classrooms = list()  # Аудитории
    for i in get_classrooms(DATABASE):
        c = Classroom(id=i.classroom_id, size=i.size, type_id=i.clrm_type_id)
        classrooms.append(c)
    return classrooms

def make_teachers_models(DATABASE):
    print("Чтение из БД преподавателей...")
    teachers_models = dict()
    for i in get_teachers(DATABASE, True):
        t = Teacher(i.teacher_id, 0, 0, 0)
        teachers_models[i.teacher_id] = t
    return teachers_models

def make_types_dict_clrms(DATABASE, classrooms):
    print("Распределение аудиторий по типам...")
    types_dict = dict()
    for i in get_types(DATABASE):
        types_dict[i]=create_models_classrooms_by_type_id(DATABASE, i, classrooms)
    return types_dict

def times_by_group(DATABASE, times):
    classes = get_classes_id(DATABASE)
    res = dict()
    for cl in classes:
        res[cl] = list()
        for t in times:
            res[cl].append(t)
    return res

def classrooms_by_times(DATABASE, times, classrooms):
    res = dict()
    for cl in classrooms:
        res[cl] = list()
        for t in times:
            res[cl].append(t)
    return res

def times_by_teachers(times, teachers_models):
    res = dict()
    for t_id in teachers_models.values():
        res[t_id] = list()
        for t in times:
            res[t_id].append(t)
    return res    


def to_create_one_entity(DATABASE, lessons, times, classrooms, teachers_models, types_dict):
    start_score = 0
    e = [dict(), dict(), start_score]
    lessons1 = lessons.copy()
    times_by_gr = times_by_group(DATABASE, times)  # cписок доступных времен у групп
    times_by_clrms = classrooms_by_times(DATABASE, times, classrooms)  # cписок доступных времен у аудиторий
    times_by_tchrs = times_by_teachers(times, teachers_models)  # cписок доступных времен у учителей
    for i in range(len(lessons)):
        if lessons1:  # занятия не повторяются
            index = random.randrange(len(lessons1))
            l = lessons1.pop(index)
        # подумать над сдвоенными
        # и один раз в две недели
            e[0][l] = list()  # первый ген особи (ЗАНЯТИЕ - ВРЕМЯ)
            e[1][l] = list()  # второй ген особи (ЗАНЯТИЕ - АУДИТОРИЯ)
            for j in range(l.hours):
                count = 0
                # while True:
                shuffle(times_by_gr[l.groups[0]])
                shuffle(times_by_gr[l.groups[0]])
                # shuffle(times_by_gr[l.groups[0]])
                # shuffle(times_by_gr[l.groups[0]])
                # новое
                # for t in times_by_gr[l.groups[0]]:
                #     #t = random.choice(times_by_gr[l.groups[0]])  # ДОБАВИТЬ УЧИТЫВАНИЕ ДРУГИХ ГРУПП ПО ВРЕМЕНИ
                #     if t in times_by_tchrs[l.teacher]:
                #         times_by_gr[l.groups[0]].remove(t)
                #         times_by_tchrs[l.teacher].remove(t)
                #         break
                #     if count > 35:
                #         print("NEVOZMOZHNO.....")
                #         break
                #     count += 1
                # конец нового
                h = list(set(times_by_gr[l.groups[0]]) & set(times_by_tchrs[l.teacher]))
                if len(h) > 0: 
                    t = random.choice(h)
                    times_by_gr[l.groups[0]].remove(t)
                    times_by_tchrs[l.teacher].remove(t)
                else:
                    return to_create_one_entity(DATABASE, lessons, times, classrooms)
                count = 0
                # while True:  # выбираю аудиторию, свободную в выбранный промежуток времени
                shuffle(types_dict[l.clrms])
                shuffle(types_dict[l.clrms])
                # shuffle(types_dict[l.clrms])
                # shuffle(types_dict[l.clrms])
                for c in types_dict[l.clrms]:
                    count += 1
                    # c = random.choice(types_dict[l.clrms]) # !!! ДОБАВИТЬ РАЗМЕРЫ АУДИТОРИЙ !!!
                    if t in times_by_clrms[c]:
                        #print(t)
                        times_by_clrms[c].remove(t)
                        break
                    # if count > 35:
                    #     count = 0
                    #     count_t = 0
                    #     while True:
                    #         t = random.choice(times_by_gr[l.groups[0]])  # ДОБАВИТЬ УЧИТЫВАНИЕ ДРУГИХ ГРУПП ПО ВРЕМЕНИ
                    #         if t not in times_by_tchrs[l.teacher]:
                    #             times_by_gr[l.groups[0]].remove(t)
                    #             break
                    #         if count_t > 35:
                    #             break
                    #         count_t += 1
                        
                e[0][l].append(t)
                e[1][l].append(c)
    return e

def create_entities(DATABASE: str, k: int, teachers_models, times, classrooms, types_dict):
    print("Создание объектов ЗАНЯТИЕ...")
    teachers = get_teachers(DATABASE)  # словарь id - объект 'учитель'
    lessons = list()
    for i in get_studyplan(DATABASE):
        # studyplan - таблица, а не класс!!!
        l = Lesson(subject=i[1], teacher=teachers_models[teachers[i[4]].teacher_id], \
            groups=[i[0]], is_stream=0, is_half=0, hours=i[2], \
            intensity=1, hours_inone=1, l_type=1, clrms=get_type_id_by_subject(DATABASE, i[1]))
        lessons.append(l)
    # Особь - занятие + время и занятие + аудитория
    print("Создание ОСОБЕЙ...")
    # k = 7  # количество особей
    entities = list()
    for i in range(k):
        shuffle(lessons)
        e = to_create_one_entity(DATABASE, lessons, times, classrooms, teachers_models, types_dict)
        entities.append(e)  # добавляю созданную особь в список всех особей
        print(k-i, "...")

    # for e in entities:
    #     print("НАЧАЛО ОСОБИ")
    #     for k, v in e[0].items():
    #         print(f'{k}: {v}')
    #     for k, v in e[1].items():
    #         print(f'{k}: {v}')
    #     print("КОНЕЦ ОСОБИ")

    return entities

def fines(entities, DATABASE, times, classrooms, teachers_models):  # функция оценивания особей
    print("Вызвана функция оценивания...")
    for i in range(len(entities)):  # перебираю особи
        entities[i][2] = 0  # задаю изначальный штраф 0
    print("  -Распределение времен занятий по дням недели...")
    times_days = dict()
    for d in get_days(DATABASE):
        times_days[d] = dict()
    for i in times:
        times_days[i.day][i] = 0
    print("  -Подсчет кол-ва пар у каждой группы одновременно...")

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

                    
    print("  -Подсчет кол-ва пар в каждой аудитории одновременно...")
    clrms_count = list()
    c_entities = entities.copy()
    for e in c_entities:
        clrms_dict = get_classrooms_for_count(times, classrooms)
        for c_lesson, c_classroom in e[1].items():
            c_time = e[0][c_lesson]
            for i in range(len(c_classroom)): # чтобы множества 
            # соотносились 1 к 1 [c1, c2] и [t1, t2] не было пары (c1, t2) и (c2, t1)
                clrms_dict[c_classroom[i]][c_time[i]] += 1
        clrms_count.append(clrms_dict)

    # for k, v in clrms_dict.items():
    #     print(f'{k}: {v}' + "\n")
    print("  -Подсчет кол-ва пар у каждого преподавателя одновременно...")
    teachers_count = list()
    c_entities = entities.copy()
    for e in c_entities:
        teachers_dict = get_teachers_for_count(times, teachers_models)
        for c_lesson, c_time in e[0].items():
            for t in c_time:
                teachers_dict[c_lesson.teacher][t] += 1
        teachers_count.append(teachers_dict)

    # for k, v in teachers_dict.items():
    #     print(f'{k}: {v}', "\n")
    # print(teachers_dict, "\n")
    print("  -Проверка накладок у групп...")
    fine_for_groups = 10000
    for i in range(len(entities)):
        b = entities[i][2]
        for g in groups_count[i].keys():
            for d in groups_count[i][g].keys():
                for t in groups_count[i][g][d].keys():
                    if groups_count[i][g][d][t] > 1:
                        entities[i][2] += fine_for_groups * (groups_count[i][g][d][t]-1) # штраф за одновременно два урока у группы
        # print(entities[i][2]-b)
        
    print("  -Проверка накладок аудиторий...")
    fine_for_classrooms = 10000
    for i in range(len(entities)):
        b = entities[i][2]
        for cl in classrooms:
            for t in times:
                if clrms_count[i][cl][t] > 1:
                    entities[i][2] += fine_for_classrooms * (clrms_count[i][cl][t]-1)  # штраф за накладки аудиторий
        # print(entities[i][2]-b)
    print("  -Проверка накладок у учителей...")
    fine_for_teachers = 100000000
    for i in range((len(entities))):
        b = entities[i][2]
        for teach in teachers_models.values():
            for t in times:
                if teachers_count[i][teach][t] > 1:
                    entities[i][2] += fine_for_teachers * (teachers_count[i][teach][t]-1)  # штраф за накладки exbntktq
        # print(entities[i][2]-b)

    # print("  -Проверка наличия окон у студентов...")
    # flag = bool()
    
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
                # bl = count_total - count_blank
                bl = count_blank
                entities[i][2] += bl * fine_for_blank_students
                # В отличии от формулы в статье повторно накладки НЕ учитываются

    # print("  -Проверка ограничения на кол-во пар в день...")
    # fine_for_overtime = 1
    # for i in range(len(entities)):
    #     for g in groups_count[i].keys():
    #         m = get_max_time(DATABASE, g)
    #         for d in groups_count[i][g].keys():
    #             c = 0
    #             for t in groups_count[i][g][d].keys():
    #                 if groups_count[i][g][d][t] >= 1:
    #                     c += 1
    #             if c > m:
    #                 entities[i][2] += (c-m) * fine_for_overtime
    #             # print(f'{g}, {c}, {m}')
    return entities


def crossingover(ent1, ent2):
    e1 = ent1.copy()
    e2 = ent2.copy()
    e_new = list()  # создаю новую особь
    e_new.append(dict())  # создаю гены
    e_new.append(dict())
    for lesson in e1[0].keys():  # перебираю занятия
        flag = random.choice([0, 1])  # выбираю особь для взятия гена времени
        e_new[0][lesson] = list()
        for i in range(len(e1[0][lesson])):
            if flag == 0:
                t = e1[0][lesson][i]
            else:
                t = e2[0][lesson][i]
            e_new[0][lesson].append(t)
        flag = random.choice([0, 1])
        e_new[1][lesson] = list()  # выбираю особь для взятия гена аудитории
        for i in range(len(e1[1][lesson])):
            if flag == 0:
                cl = e1[1][lesson][i]
            else:
                cl = e2[1][lesson][i]
            e_new[1][lesson].append(cl)
    e_new.append(0)
    return e_new

def mutation(ent1):
    e_new = list()
    e_new.append(dict())
    e_new.append(dict())
    e_new.append(0)
    for lesson in ent1[0].keys():
        e_new[0][lesson] = list()
        e_new[1][lesson] = list()
        for time in ent1[0][lesson]:
            if random.randrange(4) == 2:
                t = random.choice(times)
            else:
                t = time
            e_new[0][lesson].append(t)
        for cl in ent1[1][lesson]:
            if random.randrange(10) == 3:
                tp_id = lesson.clrms
                c = random.choice(types_dict[tp_id])
            else:
                c = cl
            e_new[1][lesson].append(c)
    return e_new

def new_ent(ent):  # функция глубокого "копирования" особи
    e_new = list()
    e_new.append(dict())
    e_new.append(dict())
    e_new.append(0)
    for lesson in ent[0].keys():
        e_new[0][lesson] = list()
        e_new[1][lesson] = list()
        for time in ent[0][lesson]:
            e_new[0][lesson].append(time)
        for cl in ent[1][lesson]:
            e_new[1][lesson].append(cl)
    return e_new
        

def loop(entities):
        n = 10  # количество выбираемых лучших особей
        for i in range(k-n):  # количество "пустых ячеек" для новых особей
            e_ind = random.randrange(n)  # индекс основы для новой особи
            e_base = new_ent(entities[e_ind])
            r = list(range(n))  # список индексов скрещиваемых особей
            if entities[e_ind][2] < 10000:
                r.pop(e_ind)
                for j in range(random.randrange(2, 13)):  # выбираю количество скрещиваний (от 2 до 12)
                    # for a in r:  # выбираю вторую скрещиваемую особь
                    a = random.choice(r)
                    if entities[a][2] < 10000:
                        e_new = crossingover(e_base, entities[a])  # скрещиваю e_new и entities[a]
                        e_base = new_ent(e_new)
                        # if random.randrange(1) == 1:
                            # e_new = mutation(e_new)
                        # entities = sorted(entities, key=lambda e: e[2])  # ????
                        entities[i+n] = e_new
        entities = fines(entities, DATABASE)
        return entities

def timetable_generation(name: str):
    k=35
    DATABASE = name+".db"
    times = read_time(DATABASE)
    classrooms = read_classrooms(DATABASE)
    teachers_models = make_teachers_models(DATABASE)
    types_dict = make_types_dict_clrms(DATABASE, classrooms)
    entities = create_entities(DATABASE, k, teachers_models, times, classrooms, types_dict)
    entities = fines(entities, DATABASE, times, classrooms, teachers_models)

    entities = sorted(entities, key=lambda e: e[2])
    print("ШТРАФЫ:")
    for e in range(len(entities)):
        print(f'{e+1}: {entities[e][2]}')
    min_start = entities[0][2]

    
        
    for i in range(0):  # количество проходов
        print(i, "...")
        entities = loop(entities)
    # entities = fines(entities)  # Закоментировал, чтобы не было повторной оценки штрафов
    entities = sorted(entities, key=lambda e: e[2])
    print("ШТРАФЫ:")
    for i in range(len(entities)):
        print(f'{i+1}: {entities[i][2]}')
    print("min start:", min_start)
    print("min now:", entities[0][2])
    print("time:", time.time() - start_time)

    export_timetable(entities[0], name+"_rasp.xlsx", DATABASE)

# timetable_generation("lyceum1524")
# for i in entities[0][0].keys():
#     if entities[0][0][i][0] != entities[1][0][i][0]:
#         print(entities[0][0][i][0], entities[1][0][i][0])