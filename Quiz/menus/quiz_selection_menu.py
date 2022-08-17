import pygine

def get(quiz_list=[]):
    menu = pygine.Menu_creator("quize")
    menu.add_vertical_selection("Quiz auswählen",[pygine.Menu_creator.get_value(quiz.name,quiz) for quiz in quiz_list],1,1,[0],(255, 255, 255),35,(255, 255, 255),20,(150, 200, 175),20)
    return menu