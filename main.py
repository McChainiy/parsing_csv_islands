import os
import time
import sys
from copy import deepcopy
import csv


class Response:
    def __init__(self, context, duration, id, island_type, grade, participant):
        self.context = context
        self.duration = float(duration)
        self.id = int(id)
        self.island_type = island_type
        if grade == '':
            self.grade = -1
        else:
            self.grade = int(grade)
        self.participant = participant

    def print_response(self):
        print("\nContext =", self.context, "\nDuration =", self.duration, "\nid =", self.id, "\nIsland Type =",
              self.island_type, "\nGrade =", self.grade, "\nParticipant ID =", self.participant.my_count,
              "\nParticipant seriousness =", self.participant.seriousness,
              "\nParticipant temper =", self.participant.temper,
              '\n_______________________________\n', end='')


class Participant:
    count = 0

    def __init__(self, age, knowledge, education, id, time_zone=0):
        Participant.count += 1
        self.my_count = Participant.count
        self.all_responses = []
        self.test_responses = []
        self.age = int(age)
        self.knowledge = knowledge
        self.education = education
        self.id = id
        self.time_zone = time_zone
        self.seriousness = 50
        self.temper = 0

    def add_response(self, response):
        self.all_responses.append(response)
        self.duration_check(response.duration)
        self.check_filler_answer(response)

    def duration_check(self, duration):
        if duration < 3:
            coef = 15 - duration * 5
            self.seriousness -= coef
        elif duration < 5:
            pass
        else:
            self.seriousness += 1

    def check_right_answer(self, answer, variants):
        variants = variants.split('; ')
        answer = answer.upper()
        if answer not in variants:
            self.seriousness -= 15

    def check_filler_answer(self, response):
        if response.island_type == 'gf':
            if response.grade >= 6:
                self.seriousness += 10
            elif response.grade >= 4:
                pass
            else:
                self.seriousness -= 10
            return
        if response.island_type == 'nf':
            if response.grade >= 6:
                self.seriousness -= 15
            elif response.grade >= 5:
                self.seriousness -= 10
            elif response.grade >= 4:
                self.seriousness -= 5
            else:
                self.seriousness += 10
            return

    def check_temper(self):
        total = 0
        length = len(self.all_responses)
        for i in range(length):
            total += self.all_responses[i].grade
            if i == length - 1:
                self.temper = total / (i + 1)

    def check_response_byid(self, id):
        for i in self.all_responses:
            if id == i.id:
                return 1
        return 0

    def get_average_duration(self):
        avr_dur = 0
        for i in self.all_responses:
            avr_dur += i.duration
        return avr_dur / len(self.all_responses)

    def print_participant(self, with_response=False):
        print('\n' + '+' * 220 + '\n')
        duration = self.get_average_duration()
        print("Participant №", Participant.count, " | Age = ", self.age, " | Knowlegde - ", self.knowledge,
              " | Education - ",               self.education, " | Seriousness = ", self.seriousness,
              " | Temper = ", self.temper, " | Power = ", len(self.all_responses), " | Duration = ", duration,
              " | ID = ", self.id, end='')
        print('\n\n' + '+' * 220)
        #print(self.all_responses, len(self.all_responses))
        if with_response or self.id == '':
            for i in self.all_responses:
                i.print_response()


def print_responses_bytype(participants, island_type):
    for n in participants:
        for i in n.all_responses:
            if i.island_type == island_type:
                i.print_response()


def print_responses_byid(participants, id):
    for n in participants:
        for i in n.all_responses:
            if i.id == id:
                i.print_response()


def analyse_responses_bytype(participants, island_type):
    responses_by_id = {}
    for n in participants:
        for i in n.all_responses:
            if i.island_type == island_type:
                if i.id not in responses_by_id:
                    responses_by_id[i.id] = []
                if i.grade == -1:
                    continue
                responses_by_id[i.id].append((i.grade, i))
    return responses_by_id


def average_participant(participants, power=30):
    avr_tmp = 0
    avr_age = 0
    avr_seriousness = 0
    avr_duration = 0
    tmp_count = 0
    edu = {}
    knowledge = {}
    for i in participants:
        if len(i.all_responses) >= power:
            tmp_count += 1
            avr_age += i.age
            avr_seriousness += i.seriousness
            avr_duration += i.get_average_duration()
            avr_tmp += i.temper
            if i.education not in edu:
                edu[i.education] = 1
            else:
                edu[i.education] += 1
            if i.knowledge not in knowledge:
                knowledge[i.knowledge] = 1
            else:
                knowledge[i.knowledge] += 1
    avr_tmp = avr_tmp / tmp_count
    avr_age = avr_age / tmp_count
    avr_duration = avr_duration / tmp_count
    avr_seriousness = avr_seriousness / tmp_count
    return {'tmp': avr_tmp, 'age': avr_age, 'seriousness': avr_seriousness, 'duration': avr_duration,
            'education': edu, 'knowledge': knowledge}


def get_all_files():
    participants = []
    directory_in_str = r"D:\IslandsPython\island_csv"

    directory = os.fsencode(directory_in_str)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".csv") or filename.endswith(".py"):
            full_filename = directory_in_str + '\\'
            full_filename = full_filename + filename
            participants.append(get_one_file(full_filename))
            continue
        else:
            continue
    return participants


def get_one_file(file_path):
    new_participant = None
    with open(file_path, "r", encoding="UTF-8") as f:
        reader = csv.reader(f)
        for line in reader:
            if line[0] == 'meta':
                continue
            # print(line)
            if line[1] == 'stimulus' and line[-7] != '':
                index_duration = 10
                index_number = line.index('6645cf40bc81b65c5faccf1d')
                if line[index_number-5].startswith('2024-05-2'):
                    index_duration = 11
                if new_participant.check_response_byid(int(line[index_number+12])):
                    continue
                new_response = Response(line[index_number+7], line[index_duration], line[index_number+12],
                                        line[index_number+9], line[index_number+4], new_participant)
                new_participant.add_response(new_response)
            if line[0].startswith('{"labjs'):
                if new_participant is not None:
                    continue
                index_number = line.index('6645cf40bc81b65c5faccf1d')
                if line[index_number - 5].startswith('2024-05-2'):
                    index_number -= 1
                new_participant = Participant(line[index_number-17], line[index_number-15], line[index_number-16],
                                              line[index_number-3])
                continue
            if line[9] == 'form submission':
                if line[-10] == 'Zrele':
                    continue
                new_participant.check_right_answer(line[27], line[-3])
        new_participant.check_temper()
        # new_participant.print_participant()
        return new_participant


def create_file_participants(participants):
    with open('all_participants.txt', 'w', encoding='UTF-8') as f:
        for i in participants:
            print('\n' + '+' * 180 + '\n', file=f)
            print("Participant №", i.my_count, " | Age = ", i.age, " | Knowlegde - ", i.knowledge,
                  " | Education - ", i.education, " | Seriousness = ", i.seriousness,
                  " | Temper = ", i.temper, " | Power = ", len(i.all_responses),
                  " | ID = ", i.id, end='', file=f)
            print('\n\n' + '+' * 180, file=f)
            for n in i.all_responses:
                print("\nStimulus =", n.context, "\nDuration =", n.duration, "\nid =", n.id, "\nIsland Type =",
                      n.island_type, "\nGrade =", n.grade, '\n_______________________________\n', end='', file=f)


def print_responses(responses, f=0):
    responses_summ = 0
    with open('stats.txt', 'a', encoding='UTF-8') as f:
        for i in sorted(responses):
            summ = 0
            summ_dur = 0
            for n in responses[i]:
                summ += n[0]
                summ_dur += n[1].duration
            length = len(responses[i])
            #print(responses[i][0][1])
            responses_summ += summ / length
            if f:
                print(i + 1, '=', round(summ / length, 3), '\t' * 5, int(summ_dur / length) / 1000, '\t',
                      length,
                      responses[i][0][1].island_type, responses[i][0][1].context, file=f)
            else:
                print(i, '=', round(summ / length, 3), '\t'*5, int(summ_dur / length) / 1000, '\t', length,
                      responses[i][0][1].island_type, responses[i][0][1].context)


#def create_stats_file(participants):


def main():
    types = ['csi', 'cnp', 'si', 'ai', 'di', 'lbc', 'nf', 'gf']
    participants = get_all_files()
    print_responses_byid(participants, 36)
    open('stats.txt', 'w').close()
    for i in types:
        print_responses(analyse_responses_bytype(participants, i))
    create_file_participants(participants)
    print(average_participant(participants))


main()
