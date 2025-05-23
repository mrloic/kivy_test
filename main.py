from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
Config.set('kivy','keyboard_mode','systemanddock')
Config.set('graphics', 'resizable', True)


questions = [
    # Логические (true/false)
    {'question': '(Фишинг) ОТНОСИТСЯ К МЕТОДАМ СОЦИАЛЬНОЙ ИНЖЕНЕРИИ', 'type': 'true_false', 'correct': True},
    {'question': '(Антивирус) ПРЕДОСТАВЛЯЕТ ПОЛНУЮ ЗАЩИТУ ОТ ВСЕХ ВИДОВ АТАК', 'type': 'true_false', 'correct': False},
    {'question': '(VPN) СПОСОБЕН СКРЫТЬ IP-АДРЕС ПОЛЬЗОВАТЕЛЯ', 'type': 'true_false', 'correct': True},
    {'question': '(Двухфакторная аутентификация) ПОВЫШАЕТ УРОВЕНЬ БЕЗОПАСНОСТИ', 'type': 'true_false', 'correct': True},
    {'question': '(Обновление ПО) МОЖЕТ БЫТЬ ПРИЧИНОЙ УГРОЗ ИБ', 'type': 'true_false', 'correct': False},

    # Множественные
    {'question': 'Выберите все надёжные способы защиты информации:',
     'type': 'multiple',
     'answers': ["Антивирус", "2FA", "Надёжные пароли", "Общий Wi-Fi", "Обновления"],
     'correct': [0, 1, 2, 4]},
    {'question': 'Что может быть угрозой ИБ?',
     'type': 'multiple',
     'answers': ["Фишинг", "Брандмауэр", "Шпионское ПО", "Антивирус", "Соц. инженерия"],
     'correct': [0, 2, 4]},
    {'question': 'Какие из нижеперечисленных относятся к персональным данным?',
     'type': 'multiple',
     'answers': ["ФИО", "IP-адрес", "MAC-адрес", "CAPTCHA", "Серийный номер"],
     'correct': [0, 1, 2]},
    {'question': 'Выберите типы вредоносного ПО:',
     'type': 'multiple',
     'answers': ["Червь", "Троян", "Фаервол", "Руткит", "Брандмауэр"],
     'correct': [0, 1, 3]},
    {'question': 'К методам аутентификации относятся:',
     'type': 'multiple',
     'answers': ["Пароль", "Биометрия", "ПИН", "Открытый Wi-Fi", "SMS-код"],
     'correct': [0, 1, 2, 4]},

    # Открытые
    {'question': 'ТЕХНОЛОГИЯ ДЛЯ ЗАЩИЩЁННОГО ПОДКЛЮЧЕНИЯ К ИНТЕРНЕТУ', 'type': 'text', 'correct': 'vpn'},
    {'question': 'НАЗВАНИЕ ТЕХНОЛОГИИ ДЛЯ АУТЕНТИФИКАЦИИ С НЕСКОЛЬКИМИ ФАКТОРАМИ', 'type': 'text', 'correct': 'многофакторная аутентификация'},
    {'question': 'ПРОЦЕСС УСТРАНЕНИЯ УЯЗВИМОСТЕЙ В ПО', 'type': 'text', 'correct': 'обновление'},
    {'question': 'СПОСОБ ПОЛУЧЕНИЯ КОНФИДЕНЦ. ИНФОРМАЦИИ ПУТЁМ ОБМАНА', 'type': 'text', 'correct': 'фишинг'},
    {'question': 'УСТРОЙСТВО ДЛЯ ЗАЩИТЫ СЕТИ ОТ НЕСАНКЦ. ДОСТУПА', 'type': 'text', 'correct': 'фаервол'}
]


class StartScreen(Screen):
    def check_input(self, instance, value):
        self.ids.start_btn.disabled = not bool(value.strip())

    def start_test(self, instance):
        app = App.get_running_app()
        app.username = self.ids.name_input.text.strip()
        app.sm.current = 'question'
        app.sm.get_screen('question').load_question()


class QuestionScreen(Screen):
    question_index = NumericProperty(0)
    selected_answers = ListProperty([None] * len(questions))

    def load_question(self):
        self.ids.answers_container.clear_widgets()
        self.ids.result_label.text = ""
        self.ids.score_label.text = ""

        q = questions[self.question_index]
        self.ids.question_label.text = q['question']

        if q['type'] == 'single':
            for i, ans in enumerate(q['answers']):
                btn = ToggleButton(text=ans, group='answers', allow_no_selection=True)
                btn.bind(on_press=self.on_single_select)
                self.ids.answers_container.add_widget(btn)

        elif q['type'] == 'multiple':
            self.checkbox_states = {}
            for i, ans in enumerate(q['answers']):
                layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
                checkbox = CheckBox()
                checkbox.bind(active=self.on_multi_select)
                self.checkbox_states[checkbox] = i
                layout.add_widget(checkbox)
                layout.add_widget(Label(text=ans, color=(0, 0, 0, 1)))
                self.ids.answers_container.add_widget(layout)

        elif q['type'] == 'text':
            ti = TextInput(multiline=False)
            ti.bind(text=self.on_text_input)
            self.ids.answers_container.add_widget(ti)

        elif q['type'] == 'true_false':
            for val in ['Да', 'Нет']:
                btn = ToggleButton(text=val, group='tf', allow_no_selection=True)
                btn.bind(on_press=self.on_tf_select)
                self.ids.answers_container.add_widget(btn)

        # Load previous answer if any
        self.restore_answer()

    def restore_answer(self):
        answer = self.selected_answers[self.question_index]
        q = questions[self.question_index]
        if answer is None:
            return
        if q['type'] == 'single':
            for btn in self.ids.answers_container.children:
                if isinstance(btn, ToggleButton) and btn.text == q['answers'][answer]:
                    btn.state = 'down'
        elif q['type'] == 'multiple':
            for layout in self.ids.answers_container.children:
                if isinstance(layout, BoxLayout):
                    checkbox = layout.children[1]
                    if self.checkbox_states[checkbox] in answer:
                        checkbox.active = True
        elif q['type'] == 'text':
            self.ids.answers_container.children[0].text = answer
        elif q['type'] == 'true_false':
            for btn in self.ids.answers_container.children:
                if btn.text == ('Да' if answer else 'Нет'):
                    btn.state = 'down'

    def on_single_select(self, instance):
        index = questions[self.question_index]['answers'].index(instance.text)
        self.selected_answers[self.question_index] = index

    def on_multi_select(self, instance, value):
        if value:
            current = self.selected_answers[self.question_index] or []
            if self.checkbox_states[instance] not in current:
                current.append(self.checkbox_states[instance])
            self.selected_answers[self.question_index] = current
        else:
            current = self.selected_answers[self.question_index] or []
            if self.checkbox_states[instance] in current:
                current.remove(self.checkbox_states[instance])
            self.selected_answers[self.question_index] = current

    def on_text_input(self, instance, value):
        self.selected_answers[self.question_index] = value.strip().lower()

    def on_tf_select(self, instance):
        self.selected_answers[self.question_index] = (instance.text == 'Да')

    def next_question(self, instance):
        if self.question_index < len(questions) - 1:
            self.question_index += 1
            self.load_question()

    def prev_question(self, instance):
        if self.question_index > 0:
            self.question_index -= 1
            self.load_question()

    def finish_test(self, instance):
        correct = 0
        for i, q in enumerate(questions):
            user_ans = self.selected_answers[i]
            correct_ans = q['correct']
            if q['type'] == 'single' or q['type'] == 'true_false':
                if user_ans == correct_ans:
                    correct += 1
            elif q['type'] == 'multiple':
                if user_ans and sorted(user_ans) == sorted(correct_ans):
                    correct += 1
            elif q['type'] == 'text':
                if user_ans and user_ans.strip().lower() == correct_ans.lower():
                    correct += 1

        total = len(questions)
        percent = round(correct / total * 100)
        result_text = f"{App.get_running_app().username}, вы ответили правильно на {correct} из {total} вопросов ({percent}%)"
        result_screen = App.get_running_app().sm.get_screen('results')
        result_screen.ids.final_result.text = result_text
        App.get_running_app().sm.current = 'results'


class ResultsScreen(Screen):
    def retry_test(self, instance):
        app = App.get_running_app()
        question_screen = app.sm.get_screen('question')
        question_screen.question_index = 0
        question_screen.selected_answers = [None] * len(questions)
        app.sm.current = 'start'


class CyberTestApp(App):
    username = StringProperty("")
    sm = ObjectProperty(None)

    def build(self):
        from kivy.lang import Builder
        Builder.load_file('main.kv')
        self.sm = ScreenManager()
        self.sm.add_widget(StartScreen(name='start'))
        self.sm.add_widget(QuestionScreen(name='question'))
        self.sm.add_widget(ResultsScreen(name='results'))
        return self.sm


if __name__ == '__main__':
    CyberTestApp().run()
