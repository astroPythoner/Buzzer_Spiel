from os.path import join
from os import listdir
from random import choice,randint,shuffle
from math import floor,ceil
import json
import time
import string
import pygine
import pygame

class Quiz():
    def __init__(self,quiz_name,project_name):
        self.name = "<<unnamed>>"
        self.file_name = quiz_name
        self.project_name = project_name
        self.questions_random = True
        self.reask_wrong_questions = True
        self.num_total_questions_to_ask = 1
        self.orig_questions = []
        self.background = None
        self.text_color = (255, 255, 255)
        self.rect_color = (150, 150, 150)
        self.text_on_rect_color = (0,0,0)
        try:
            with open(quiz_name) as f:
                data = json.load(f)
                self.name = data["Name"]
                self.questions_random = data["Questions Random"]
                self.reask_wrong_questions = data["ask wrong questions again"]
                self.num_total_questions_to_ask = data["Number asked questions"]
                self.orig_questions = data["Questions"]
                self.background = img if (img := data["Background file"]) != "" else "default_background.png"
                self.text_color = data["Text color"]
                self.rect_color = data["Rect color"]
                self.text_on_rect_color = data["Text on Rect color"]
        except Exception as e:
            raise Exception(f"quiz file not found or incomplete: {e}")
        self.__current_question_idx = -1
        self.__list_left_questions = [i for i in range(len(self.orig_questions))]
        self.__question_time_add = 0
        self.__question_time_start = None
        self.__question_answer_time = None
        self.__solution = ""
        self.num_total_questions_to_ask = min([self.num_total_questions_to_ask,len(self.orig_questions)])
        self.question_attributes = {}  # other attributes needed to draw a question (filled in set_question_attributes)
        # check questions correct
        val = 0
        for count,question in enumerate(self.orig_questions):
            try:
                # question
                if question["Type"] == "Multiple Choice":
                    val = question["Question"]
                    ans = question["Answers"]
                    anz = len(question["Answers"])
                    if not 0 <= question["Correct Answer"] < anz:
                        raise Exception("Correct answer out of Answers range")
                    val = question["Question read time"]
                elif question["Type"] == "Building up Image":
                    val = question["Question"]
                    val = question["Answer"]
                    pygine.load_image(project_name,["img",question["Image"]])
                    val = question["Building Time"]
                    val = question["Top Color"]
                elif question["Type"] == "Question":
                    val = question["Question"]
                    val = question["Answer"]
                    if "Image" in question:
                        pygine.load_image(project_name, ["img", question["Image"]])
                # points
                if self.question["Points mode"] == "Add/remove points":
                    val = self.question["points for right answer"]
                    val = self.question["reduction for wrong answer"]
                elif self.question["Points mode"] == "Time points":
                    val = self.question["start points"]
                    val = self.question["point reduction per second"]
                    val = self.question["min points"]
                    val = self.question["reduction for wrong answer"]
            except Exception as e:
                raise Exception(f"Error in Question {count+1} of quiz file: {e}")

    def start_question(self,size,text_size):
        self.__question_time_start = None
        self.__question_time_add = 0
        self.__question_answer_time = None
        self.text_size = text_size
        self.question_attributes = {}
        if self.num_total_questions_to_ask <= self.num_asked_questions:
            return True
        if self.questions_random:
            self.__current_question_idx = choice(self.__list_left_questions)
            del self.__list_left_questions[self.__list_left_questions.index(self.__current_question_idx)]
        else:
            self.__current_question_idx += 1
        self.set_question_attributes(size,text_size)
        print(self.answer)
        return False
    def next_question(self,ask_again,size,text_size):
        if not ask_again:
            return self.start_question(size,text_size)
        else:
            self.__question_time_add = self.seconds_on_question
            self.__question_time_start = None
            self.__question_answer_time = None
            return False

    ##### use these functions to add the drawing of new question types #####
    def set_question_attributes(self,size,text_size):
        # is called once the question is selected or the screen resized, to for example calculate the size of text rectangles
        copy = self.question_attributes.copy()
        self.text_size = text_size
        self.question_attributes = {}  # dict for storing attributes
        if self.question["Type"] == "Multiple Choice":
            self.__solution = self.question["Answers"][self.question["Correct Answer"]]
            # split question in lines
            self.question_attributes["texts"] = pygine.split_text_into_lines_fitting_width(self.question["Question"],50*text_size,size[0]-50)
            # split answers into lines
            max_lines = 1
            max_width = 100
            if not "answers" in copy and self.question["Shuffle Answers"]: shuffle(self.question["Answers"])
            self.question_attributes["answers"] = []
            for answer in self.question["Answers"]:
                lines = pygine.split_text_into_lines_fitting_width(answer,35*text_size,int(size[0]/2-60))
                self.question_attributes["answers"].append(lines)
                if len(lines) > max_lines: max_lines = len(lines)
                for line in lines:
                    if (w:=pygine.get_text_rect(line,35*text_size).width+30) > max_width: max_width = w
            # get rects for answers
            self.question_attributes["rects"] = []
            num_answers = len(self.question["Answers"])
            rect_height = max_lines*40*text_size+30
            total_height = size[1]-len(self.question_attributes["texts"])*60*text_size-75*self.text_size-30
            distance = (total_height-rect_height*ceil(num_answers/2)) / (ceil(num_answers/2)+1)
            y_start = len(self.question_attributes["texts"])*60*text_size+75*self.text_size+15+distance
            for num in range(num_answers):
                quaters_of_width = 3 if num%2 != 0 else (1 if num != num_answers-1 else 2)
                self.question_attributes["rects"].append(pygame.Rect(size[0] * quaters_of_width / 4 - max_width/2, y_start + (distance + rect_height) * floor(num / 2), max_width, rect_height))
        elif self.question["Type"] == "Building up Image":
            self.__solution = self.question["Answer"]
            self.question_attributes["texts"] = pygine.split_text_into_lines_fitting_width(self.question["Question"],35*text_size,size[0]-50)
            if self.question["Building Type"] == "Random":
                self.question["Building Type"] = choice(["Rect","Dots"])
            img = pygine.load_image(self.project_name,["img",self.question["Image"]])
            small_img,pos,factor = pygine.get_image_fit_into_rect(img, pygame.Rect(0, 0, size[0] - 20, size[1] - len(self.question_attributes["texts"])*60*text_size+30*self.text_size-75*self.text_size-30))
            self.question_attributes["img"] = small_img
            self.question_attributes["pos"] = pos
            if "mask" in copy:
                self.question_attributes["mask"] = pygame.transform.scale(copy["mask"],small_img.get_size())
            else:
                self.question_attributes["mask"] = pygame.Surface(small_img.get_size(),pygame.SRCALPHA)
                self.question_attributes["mask"].fill((*self.question["Top Color"],255))
            build_size = ceil(small_img.get_width()/self.question["Building Size"])
            self.question_attributes["build size"] = build_size
            self.question_attributes["time last change"] = time.time()
            self.question_attributes["time between changes"] = self.question["Building Time"]/(ceil(small_img.get_width()/build_size)*ceil(small_img.get_height()/build_size))
            if self.question["Building Type"] == "Dots":
                self.question_attributes["time between changes"] *= 0.75
            elif self.question["Building Type"] == "Rect":
                self.question_attributes["positions"] = []
                for x in range(0,small_img.get_width(),build_size):
                    for y in range(0, small_img.get_height(), build_size):
                        self.question_attributes["positions"].append((x,y))
        elif self.question["Type"] == "Question":
            self.__solution = self.question["Answer"]
            self.question_attributes["texts"] = pygine.split_text_into_lines_fitting_width(self.question["Question"],35*text_size,size[0]-50)
            if "Image" in self.question:
                img = pygine.load_image(self.project_name, ["img", self.question["Image"]])
                small_img, pos, factor = pygine.get_image_fit_into_rect(img, pygame.Rect(0, 0, size[0] - 20, size[1] - len(self.question_attributes["texts"])*60*text_size+30*self.text_size-75*self.text_size-30))
                self.question_attributes["img"] = small_img
                self.question_attributes["pos"] = pos
    def draw(self,screen:pygame.Surface):
        # is called every frame to draw the question
        if self.__question_time_start is None: self.__question_time_start = time.time()
        pygine.draw_text(screen, f"Frage {self.num_asked_questions}/{self.num_total_questions_to_ask}", 25*self.text_size, 10, 10, color=self.text_color)
        if self.question["Type"] == "Multiple Choice":
            for count,line in enumerate(self.question_attributes["texts"]):
                if time.time() - self.__question_time_start < self.question["Question read time"]:
                    pygine.draw_text(screen, line, 50*self.text_size, int(screen.get_width() / 2), int((screen.get_height()/2)-(len(self.question_attributes["texts"])*60*self.text_size)/2+count*60*self.text_size), color=self.text_color, rect_place=pygine.CENTER)
                else:
                    pygine.draw_text(screen, line, 50*self.text_size, int(screen.get_width() / 2), 75*self.text_size+count*60*self.text_size, color=self.text_color, rect_place=pygine.CENTER)
            if time.time() - self.__question_time_start > self.question["Question read time"]:
                for rect,lines in zip(self.question_attributes["rects"],self.question_attributes["answers"]):
                    pygame.draw.rect(screen,self.rect_color,rect,border_radius=int(8*self.text_size))
                    for count,line in enumerate(lines):
                        pygine.draw_text(screen,line,35*self.text_size,rect.left+rect.w/2,rect.center[1]-(len(lines)*40*self.text_size)/2+count*40*self.text_size,rect_place=pygine.TOP,color=self.text_on_rect_color)
        elif self.question["Type"] == "Building up Image":
            for count, line in enumerate(self.question_attributes["texts"]):
                    pygine.draw_text(screen, line, 50*self.text_size, int(screen.get_width() / 2), 75*self.text_size+count*60*self.text_size, color=self.text_color, rect_place=pygine.CENTER)
            screen.blit(self.question_attributes["img"],(10+self.question_attributes["pos"].x, len(self.question_attributes["texts"])*60*self.text_size-30*self.text_size+75*self.text_size+15 + self.question_attributes["pos"].y))
            screen.blit(self.question_attributes["mask"],(10+self.question_attributes["pos"].x, len(self.question_attributes["texts"])*60*self.text_size-30*self.text_size+75*self.text_size+15 + self.question_attributes["pos"].y))
            s = self.question_attributes["mask"].get_size()
            if time.time() - self.question_attributes["time last change"] > self.question_attributes["time between changes"]:
                self.question_attributes["time last change"] = time.time()
                if self.question["Building Type"] == "Dots":
                    pygame.draw.circle(self.question_attributes["mask"],(0,0,0,0),(randint(0,s[0]-1),randint(0,s[1]-1)),self.question_attributes["build size"]/2)
                elif self.question["Building Type"] == "Rect":
                    if len(self.question_attributes["positions"])>0:
                        n = randint(0,len(self.question_attributes["positions"])-1)
                        pos = self.question_attributes["positions"][n]
                        del self.question_attributes["positions"][n]
                        pygame.draw.rect(self.question_attributes["mask"],(0,0,0,0),(pos[0],pos[1],self.question_attributes["build size"],self.question_attributes["build size"]))
        elif self.question["Type"] == "Question":
            if "Image" in self.question:
                for count, line in enumerate(self.question_attributes["texts"]):
                    pygine.draw_text(screen, line, 50*self.text_size, int(screen.get_width() / 2), 75*self.text_size+count*60*self.text_size, color=self.text_color, rect_place=pygine.CENTER)
                screen.blit(self.question_attributes["img"], (10 + self.question_attributes["pos"].x, len(self.question_attributes["texts"])*60*self.text_size-30*self.text_size+75*self.text_size+15 + self.question_attributes["pos"].y))
            else:
                for count, line in enumerate(self.question_attributes["texts"]):
                    pygine.draw_text(screen, line, 50*self.text_size, int(screen.get_width()/2), int((screen.get_height()/2)-(len(self.question_attributes["texts"])*60*self.text_size)/2+count*60*self.text_size), color=self.text_color, rect_place=pygine.CENTER)

    ##### use this function to add the calculating of new point types #####
    def get_points(self,correct:bool):
        if self.question["Points mode"] == "Add/remove points":
            if correct:
                return self.question["points for right answer"]
            else:
                return - self.question["reduction for wrong answer"]
        elif self.question["Points mode"] == "Time points":
            if correct:
                return max([self.question["start points"] - self.seconds_on_question * self.question["point reduction per second"], self.question["min points"]])
            else:
                return - self.question["reduction for wrong answer"]
        return 0

    
    @property
    def solution(self):
        return self.__solution
    @property
    def solution_explanation(self):
        if "Answer Explanation" in self.question:
            return self.question["Answer Explanation"]
        return ""
    ##### use this to adjust the anser information printed for the game master #####
    @property
    def answer(self):
        text = f"""########### {self.num_asked_questions}/{self.num_total_questions_to_ask}\n"""
        if self.question["Type"] == "Multiple Choice":
            text += f"""Frage: {self.question["Question"]}\nRichtige Antwort: {self.question["Answers"][self.question["Correct Answer"]]}"""
        elif self.question["Type"] == "Building up Image":
            text += "Bild Frage: dargestellt ist '" + self.question["Answer"] +"'"
        elif self.question["Type"] == "Question":
            text += f"""Frage: {self.question["Question"]}\nRichtige Antwort: {self.question["Answer"]}"""
        return text

    @property
    def question(self):
        return self.orig_questions[self.__current_question_idx]
    @property
    def num_asked_questions(self):
        if self.questions_random:
            return len(self.orig_questions) - len(self.__list_left_questions)
        else:
            return self.__current_question_idx + 1
    @property
    def seconds_on_question(self):
        if self.__question_answer_time is not None:
            return self.__question_answer_time - self.__question_time_start + self.__question_time_add
        else:
            return time.time()-self.__question_time_start + self.__question_time_add

    def answer_given(self):
        self.__question_answer_time = time.time()


def get_quiz_list(project_name):
    quizes = []
    dir = pygine.get_file_path(project_name,["questions"])
    for file in listdir(dir):
        try:
            if file[0] != ".":
                q = Quiz(join(dir,file),project_name)
                quizes.append(q)
        except Exception as e:
            print("Error in quiz file:",file)
            raise Warning(e)
    print(f"found {len(quizes)} Quizes")
    return quizes
