#!/usr/bin/env python3
"""
Process missing students with proper student ID handling
Generated: 2025-08-05
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.process_data import DataProcessor
from scripts.generate_reports import ReportGenerator

# Missing students from batch 7 and 8
missing_students = [
    # From batch 7 (rows 10-24)
    {
        'student_id': 's10569',
        'student_name': 'Josiah Hoo En Yi',
        'program': 'BBP',
        'sessions': [
            {'date': '02/08/2025', 'session': '19', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '26/07/2025', 'session': '19', 'lesson': 'L1: Concept 2 Jupyter Notebook  https://www.telebort.com/demo/ai1/lesson/2 https://www.telebort.com/demo/ai1/activity/2 https://forms.gle/uLTj2zspLYciMmkV8 ', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '19/07/2025', 'session': '18', 'lesson': 'Lesson 1: Introduction to Python\r\nLesson 2: Jupyter Notebook\r\nLesson 3: Variables & Operators', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '12/07/2025', 'session': '17', 'lesson': 'L24: Graduation https://forms.gle/PeS4pRvbWBF7czr96  https://forms.gle/jWiufwDrj9UrrxRB6 ', 'attendance': 'No Class', 'progress': '-'},
            {'date': '05/07/2025', 'session': '17', 'lesson': 'L21: Project: Scientific Calculator COMPLETED\nL22: Revision Quiz 2 8/11\nL23: Quiz 2 90/100', 'attendance': 'Han Yang', 'progress': 'Completed'},
            {'date': '28/06/2025', 'session': '16', 'lesson': 'L20: Python Math Module COMPLETED', 'attendance': 'Han Yang', 'progress': ''}
        ]
    },
    {
        'student_id': 's10608',
        'student_name': 'Lee Chong Tatt',
        'program': 'D (W-2)',
        'sessions': [
            {'date': '03/08/2025', 'session': '0', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '20', 'lesson': 'L22: Final Project (Part 2)\nL23: Quiz 2\nL24: Graduation', 'attendance': 'Soumiya', 'progress': 'Graduated'},
            {'date': '20/07/2025', 'session': '19', 'lesson': 'L23: Calorie counter part 2 https://www.telebort.com/demo/w2/project/6 ', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '13/07/2025', 'session': '18', 'lesson': 'L22 calorie counter part 1 https://www.telebort.com/demo/w2/project/6', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '06/07/2025', 'session': '17', 'lesson': 'L20 Final Project (Calorie Calculator Part 1): IN PROGRESS', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '29/06/2025', 'session': '16', 'lesson': 'L19 Mini Project 5: COMPLETED', 'attendance': 'Soumiya', 'progress': ''}
        ]
    },
    {
        'student_id': 's10609',
        'student_name': 'Lee Xuen Ni',
        'program': 'D (W-2)',
        'sessions': [
            {'date': '03/08/2025', 'session': '0', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '20', 'lesson': 'L23: Quiz 2\nL24: Graduation', 'attendance': 'Soumiya', 'progress': 'Graduated'},
            {'date': '20/07/2025', 'session': '19', 'lesson': 'quiz 2  https://forms.gle/vAPNXoE7RJ1N83ZH6', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '13/07/2025', 'session': '18', 'lesson': 'L22 calorie counter part 1 https://www.telebort.com/demo/w2/project/6\nL23 calorie counter part 2 https://www.telebort.com/demo/w2/project/6', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '06/07/2025', 'session': '17', 'lesson': 'L20 Final Project (Calorie Calculator Part 1): IN PROGRESS\n', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '29/06/2025', 'session': '16', 'lesson': 'L19 Mini Project 5: COMPLETED', 'attendance': 'Soumiya', 'progress': ''}
        ]
    },
    {
        'student_id': 's10707',
        'student_name': 'Lim Jia Sheng',
        'program': 'F (AI-1)',
        'sessions': [
            {'date': '03/08/2025', 'session': '6', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '6', 'lesson': 'L4: Concept 4 Control Flow https://www.telebort.com/demo/w2/lesson/4  https://www.telebort.com/demo/w2/activity/4 https://forms.gle/qJXapV5TVKJXLP4e6 ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '20/07/2025', 'session': '5', 'lesson': 'L3: concept 4 List https://www.telebort.com/demo/ai1/lesson/4 https://www.telebort.com/demo/ai1/activity/4   ', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '13/07/2025', 'session': '4', 'lesson': 'L2: concept 3 variables& operators  notes & activity ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '06/07/2025', 'session': '3', 'lesson': 'L1 Jupyter Notebook: COMPLETED', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '29/06/2025', 'session': '2', 'lesson': 'L1 Introduction to Python Programming: COMPLETED\nL1 Jupyter Notebook: IN PROGRESS', 'attendance': 'Soumiya', 'progress': ''}
        ]
    },
    {
        'student_id': 's10809',
        'student_name': 'Felicia P\'ng Wei Xing',
        'program': 'F (AI-1)',
        'sessions': [
            {'date': '03/08/2025', 'session': '-', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '3', 'lesson': 'L2 Variables & Operators', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '20/07/2025', 'session': '2', 'lesson': 'L1: concept 1 notes & activity', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '13/07/2025', 'session': '1', 'lesson': 'L1: concept 1 notes & activity', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '06/07/2025', 'session': '0', 'lesson': '-', 'attendance': 'No Class', 'progress': '-'},
            {'date': '29/06/2025', 'session': '-', 'lesson': '-', 'attendance': '-', 'progress': ''}
        ]
    },
    {
        'student_id': 's10510',
        'student_name': 'Justin Kang Yoong Ming',
        'program': 'C (W-1)',
        'sessions': [
            {'date': '03/08/2025', 'session': '10', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '10', 'lesson': 'L10 & L11: my holiday part 3 & Part 4 https://www.telebort.com/demo/w1/project/3 ', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '20/07/2025', 'session': '9', 'lesson': 'L11: my holiday part 3  https://www.telebort.com/demo/w1/project/3 ', 'attendance': 'Soumiya', 'progress': '-'},
            {'date': '13/07/2025', 'session': '8', 'lesson': 'L10: project 3 my holiday part 1 https://www.telebort.com/demo/w1/project/3', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '06/07/2025', 'session': '7', 'lesson': 'L8: My Holiday Part 1: IN PROGRESS', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '29/06/2025', 'session': '6', 'lesson': 'L7: CSS Display & Flexbox: COMPLETED', 'attendance': 'Soumiya', 'progress': ''}
        ]
    },
    {
        'student_id': 's10708',
        'student_name': 'Teoh Wei Lynn',
        'program': 'C (W-1)',
        'sessions': [
            {'date': '03/08/2025', 'session': '7', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '7', 'lesson': 'L8: concept 7&8 CSS Display + CSS Flexbox https://www.telebort.com/demo/w1/lesson/7  https://www.telebort.com/demo/w1/activity/7  https://www.telebort.com/demo/w1/lesson/8 https://www.telebort.com/demo/w1/activity/8 ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '20/07/2025', 'session': '6', 'lesson': 'L8: concept 7&8 CSS Display + CSS Flexbox https://www.telebort.com/demo/w1/lesson/7  https://www.telebort.com/demo/w1/activity/7  https://www.telebort.com/demo/w1/lesson/8 https://www.telebort.com/demo/w1/activity/8 ', 'attendance': 'Absent', 'progress': '-'},
            {'date': '13/07/2025', 'session': '6', 'lesson': 'L7: concept 5 notes+activity https://www.telebort.com/demo/w1/lesson/5 https://www.telebort.com/demo/w1/activity/5 & 6 notes+activity https://www.telebort.com/demo/w1/lesson/6 https://www.telebort.com/demo/w1/activity/6 ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '06/07/2025', 'session': '5', 'lesson': 'L6 HTML Content Division & CSS Box Model: IN PROGRESS', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '29/06/2025', 'session': '4', 'lesson': 'L5 CSS Selector: COMPLETED', 'attendance': 'Soumiya', 'progress': ''}
        ]
    },
    {
        'student_id': 's10767',
        'student_name': 'Klarixa Joli Ramesh',
        'program': 'D (W-2)',
        'sessions': [
            {'date': '03/08/2025', 'session': '4', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '4', 'lesson': 'L4: Concept 4 Control Flow https://www.telebort.com/demo/w2/lesson/4  https://www.telebort.com/demo/w2/activity/4 https://forms.gle/qJXapV5TVKJXLP4e6 ', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '20/07/2025', 'session': '3', 'lesson': 'L1-L3', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '13/07/2025', 'session': '2', 'lesson': 'L1: concept 1 notes & activity https://www.telebort.com/demo/w2/activity/1 ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '06/07/2025', 'session': '1', 'lesson': 'L1: concept 1 notes & activity https://www.telebort.com/demo/w2/activity/1 ', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '29/06/2025', 'session': '0', 'lesson': '-', 'attendance': 'No Class', 'progress': ''}
        ]
    },
    {
        'student_id': 's10360',
        'student_name': 'Hadi Imran Bin Hayazi',
        'program': 'D (W-2)',
        'sessions': [
            {'date': '03/08/2025', 'session': '13', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '13', 'lesson': ' L9: Revision & Quiz 1 https://docs.google.com/presentation/d/1zKfCB5MyMlpGfrR1IuVXri-cD7gizJjEXIXgXjtwXWU/edit?usp=sharing https://forms.gle/GqbLV9z5WsEGZ1EM8 ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '20/07/2025', 'session': '12', 'lesson': 'L7: concept 6 notes & activity https://www.telebort.com/demo/w2/lesson/6 https://www.telebort.com/demo/w2/activity/6 \nL10: Array Part 1', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '13/07/2025', 'session': '11', 'lesson': 'L7: concept 6 notes & activity https://www.telebort.com/demo/w2/lesson/6 https://www.telebort.com/demo/w2/activity/6 ', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '06/07/2025', 'session': '10', 'lesson': 'L6 Mini Project BMI Calculator: COMPLETED', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '29/06/2025', 'session': '9', 'lesson': 'L5 Loops: COMPLETED', 'attendance': 'Soumiya', 'progress': ''}
        ]
    },
    {
        'student_id': 's10808',
        'student_name': 'Ravio Reinhart Sianipar',
        'program': 'C (W-1)',
        'sessions': [
            {'date': '03/08/2025', 'session': '2', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '2', 'lesson': 'L20: Final Project (Part 1) https://www.telebort.com/demo/bbd/project/4  https://forms.gle/9HmphJYq8on865AcA  L21: Final Project (Part 2) https://forms.gle/8v5Qtyu4TqFs6snW8 ', 'attendance': 'No Class', 'progress': '-'},
            {'date': '20/07/2025', 'session': '2', 'lesson': 'L2: concept 2 activity https://www.telebort.com/demo/w1/activity/2  then continue with L3: project 1 https://www.telebort.com/demo/w1/project/1 ', 'attendance': 'No Class', 'progress': 'In Progress'},
            {'date': '13/07/2025', 'session': '2', 'lesson': 'L2: concept 2 activity https://www.telebort.com/demo/w1/activity/2  then continue with L3: project 1 https://www.telebort.com/demo/w1/project/1 ', 'attendance': 'Absent', 'progress': 'In Progress'},
            {'date': '06/07/2025', 'session': '2', 'lesson': 'L2\nIntroduction to HTML: DONE\n\nExercise: DOING', 'attendance': 'Syahin', 'progress': 'In Progress'},
            {'date': '29/06/2025', 'session': '1', 'lesson': 'L1\nIntroduction to Web Design: DONE\n\nSetup GitHub & Stackblitz', 'attendance': 'Syahin', 'progress': ''}
        ]
    },
    {
        'student_id': 's10726',
        'student_name': 'Too U-Gyrn',
        'program': 'BBP',
        'sessions': [
            {'date': '03/08/2025', 'session': '30', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '30', 'lesson': 'L24: Graduation  https://forms.gle/NMcQPXCijBgjHigL9  https://forms.gle/AFRP1NsjPn78g1Q4A ', 'attendance': 'Nurafrina', 'progress': 'In Progress'},
            {'date': '20/07/2025', 'session': '29', 'lesson': 'L18: Project: My Quiz Game (Basic) https://www.telebort.com/demo/bbp/project/4 ', 'attendance': 'Nurafrina', 'progress': 'In Progress'},
            {'date': '13/07/2025', 'session': '28', 'lesson': 'L17: Project: Nutritious Meal https://www.telebort.com/demo/bbp/project/5  https://dashboard.telebort.me/training/learningPlan/63e3715442b65c4edbaa6c70', 'attendance': 'Syahin', 'progress': 'Completed'},
            {'date': '06/07/2025', 'session': '27', 'lesson': 'Quiz 1', 'attendance': 'Syahin', 'progress': 'Completed'},
            {'date': '29/06/2025', 'session': '26', 'lesson': 'L17 Project: Nutritious Meal (Part 2): \nONGOING', 'attendance': 'Syahin', 'progress': ''}
        ]
    },
    {
        'student_id': 's10723',
        'student_name': 'Yashvid Daryl Kumar',
        'program': 'BBP',
        'sessions': [
            {'date': '03/08/2025', 'session': '0', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '27/07/2025', 'session': '0', 'lesson': 'L9: Concept 8 AI Coding with IDE https://www.telebort.com/demo/ai3/lesson/8 https://www.telebort.com/demo/ai3/activity/8 https://forms.gle/6AruKFm38vR1oES38 ', 'attendance': 'No Class', 'progress': '-'},
            {'date': '20/07/2025', 'session': '0', 'lesson': 'L1: concept 1 notes & activity https://www.telebort.com/demo/w1/lesson/1 https://www.telebort.com/demo/w1/activity/1 ', 'attendance': 'In Break', 'progress': '-'},
            {'date': '13/07/2025', 'session': '0', 'lesson': 'L1: concept 1 notes & activity https://www.telebort.com/demo/w1/lesson/1 https://www.telebort.com/demo/w1/activity/1 ', 'attendance': 'In Break', 'progress': '-'},
            {'date': '06/07/2025', 'session': '29', 'lesson': 'GRADUATION', 'attendance': 'Syahin', 'progress': 'Graduated'},
            {'date': '29/06/2025', 'session': '28', 'lesson': 'Quiz 2:\nCOMPLETED', 'attendance': 'Syahin', 'progress': ''}
        ]
    },
    {
        'student_id': 's10084',
        'student_name': 'Jiwoo Kim',
        'program': 'H (BBD)',
        'sessions': [
            {'date': '02/08/2025', 'session': '25', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '26/07/2025', 'session': '25', 'lesson': 'L9: Quiz 1 https://forms.gle/5zeDUwKQnd12oRdSA + Concept 8 AI Coding with IDE https://www.telebort.com/demo/ai3/lesson/8 https://www.telebort.com/demo/ai3/activity/8 https://forms.gle/6AruKFm38vR1oES38 ', 'attendance': 'No Class', 'progress': '-'},
            {'date': '19/07/2025', 'session': '25', 'lesson': 'L19: quiz 2 revision quiz link  L20: https://docs.google.com/document/d/1IwVrL_HXIg-ENfpn67vOVCKTE7xvo8ncHO_Eol5NtCo/edit?usp=sharing ', 'attendance': 'Khairina', 'progress': 'In Progress'},
            {'date': '12/07/2025', 'session': '24', 'lesson': 'L19: quiz 2 revision quiz link ', 'attendance': 'No Class', 'progress': '-'},
            {'date': '05/07/2025', 'session': '24', 'lesson': 'L18 Exercise\nAI Application Interfaces: \n\nL19 Quiz 2\n', 'attendance': 'Khairina', 'progress': 'Completed'},
            {'date': '28/06/2025', 'session': '23', 'lesson': 'L16 MP3\nPrototyping Web Apps: Done\n\nL17 Excercise\nIntroduction to AI-First Applications: Done', 'attendance': 'Khairina', 'progress': ''}
        ]
    },
    {
        'student_id': 's10100',
        'student_name': 'Cheng Hao Wen',
        'program': 'H (BBD)',
        'sessions': [
            {'date': '02/08/2025', 'session': '30', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '26/07/2025', 'session': '30', 'lesson': 'L9: Concept 10 Text Processing in NLP https://www.telebort.com/demo/ai2/lesson/10 https://www.telebort.com/demo/ai2/activity/10 https://forms.gle/nivVu9aGjRbcFvq17 ', 'attendance': 'No Class', 'progress': '-'},
            {'date': '19/07/2025', 'session': '30', 'lesson': 'L23: part 4 project presentation https://www.telebort.com/demo/bbd/project/4      https://www.figma.com/design/clK3I2Z2o0NUgCz79QD1rE/Untitled?node-id=0-1&p=f&t=RgDtnayyXGgSFKe3-0', 'attendance': 'Khairina', 'progress': 'Completed'},
            {'date': '12/07/2025', 'session': '29', 'lesson': 'L23: part 4 project presentation https://www.telebort.com/demo/bbd/project/4 ', 'attendance': 'No Class', 'progress': '-'},
            {'date': '05/07/2025', 'session': '29', 'lesson': 'L21 Final Project\n(Part 2) - Wireframe\n\nL22 Final Project\n(Part 3) - Portfolio Building', 'attendance': 'Khairina', 'progress': 'Completed'},
            {'date': '28/06/2025', 'session': '28', 'lesson': 'L20 Final Project\n(Part 1) - Analysis: Done\n\nL21 Final Project\n(Part 2) - Wireframe', 'attendance': 'Khairina', 'progress': ''}
        ]
    },
    {
        'student_id': 's10779',
        'student_name': 'Tew Jae Fung',
        'program': 'D (W-2)',
        'sessions': [
            {'date': '02/08/2025', 'session': '8', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '26/07/2025', 'session': '8', 'lesson': 'based on previous lessons & progress, havent done L4: Concept 4 Control Flow https://www.telebort.com/demo/W2/lesson/4 https://www.telebort.com/demo/W2/activity/4 https://forms.gle/qZ2c5Fy6TJ8eRURP8 after done with C4 proceed with L7: Concept 6 Functions https://www.telebort.com/demo/W2/lesson/6 https://www.telebort.com/demo/W2/activity/6 https://forms.gle/cAg6qP3u1K3fYiBv5 ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '19/07/2025', 'session': '7', 'lesson': 'L6: project 1  ', 'attendance': 'Han Yang', 'progress': 'Completed'},
            {'date': '12/07/2025', 'session': '6', 'lesson': 'L6: project 1 https://www.telebort.com/demo/w2/project/1 ', 'attendance': 'No Class', 'progress': '-'},
            {'date': '05/07/2025', 'session': '6', 'lesson': 'L6: project 1 https://www.telebort.com/demo/w2/project/1 ', 'attendance': 'Han Yang', 'progress': 'In Progress'},
            {'date': '28/06/2025', 'session': '5', 'lesson': 'L5: Loops IN PROGRESS', 'attendance': 'Han Yang', 'progress': ''}
        ]
    },
    # From batch 8 (rows 6-8)
    {
        'student_id': 's10777',
        'student_name': 'Nathan Chee Ying-Cherng',
        'program': 'F (AI-1)',
        'sessions': [
            {'date': '02/08/2025', 'session': '13', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '26/07/2025', 'session': '13', 'lesson': 'L22: Final Project Prototype https://www.telebort.com/demo/ai2/project/7  ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '19/07/2025', 'session': '12', 'lesson': 'L9: concept 11 Descriptive Statistics\nL10: concept 12 pretty table \nhttps://www.telebort.com/demo/ai1/lesson/12  \nhttps://www.telebort.com/demo/ai1/activity/12   ', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '12/07/2025', 'session': '11', 'lesson': 'L10: concept 12 pretty table https://www.telebort.com/demo/ai1/lesson/12  https://www.telebort.com/demo/ai1/activity/12   concept 13 data visualization https://www.telebort.com/demo/ai1/lesson/13  https://www.telebort.com/demo/ai1/activity/13 ', 'attendance': 'No Class', 'progress': '-'},
            {'date': '05/07/2025', 'session': '11', 'lesson': '-', 'attendance': 'Absent', 'progress': '-'},
            {'date': '28/06/2025', 'session': '11', 'lesson': 'L9 Numpy: COMPLETED', 'attendance': 'Soumiya', 'progress': ''}
        ]
    },
    {
        'student_id': 's10710',
        'student_name': 'Shawn Lee Shan Wei',
        'program': 'F (AI-1)',
        'sessions': [
            {'date': '02/08/2025', 'session': '6', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '26/07/2025', 'session': '6', 'lesson': 'L2: Concept 3 Variables & Operators https://www.telebort.com/demo/ai1/lesson/3  https://www.telebort.com/demo/ai1/activity/3 https://forms.gle/EzCaqwFv25TbC2qV9 L3: Concept 4 List https://www.telebort.com/demo/ai1/lesson/4 https://www.telebort.com/demo/ai1/activity/4 https://forms.gle/xoyG4q1JrYxi4CkV6 ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '19/07/2025', 'session': '5', 'lesson': 'L4: concept 6 activity https://www.telebort.com/demo/ai1/activity/6  L5: project 1 https://www.telebort.com/demo/ai1/project/1 ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '12/07/2025', 'session': '4', 'lesson': 'L4: concept 6 activity https://www.telebort.com/demo/ai1/activity/6  L5: project 1 https://www.telebort.com/demo/ai1/project/1 ', 'attendance': 'No Class', 'progress': '-'},
            {'date': '05/07/2025', 'session': '4', 'lesson': '-', 'attendance': 'Absent', 'progress': '-'},
            {'date': '28/06/2025', 'session': '4', 'lesson': 'L3 Conditional Statement: COMPLETED\nL4 Loops: IN PROGRESS', 'attendance': 'Soumiya', 'progress': ''}
        ]
    },
    {
        'student_id': 's10213',
        'student_name': 'Low Yue Yuan',
        'program': 'G (AI-2)',
        'sessions': [
            {'date': '02/08/2025', 'session': '24', 'lesson': '-', 'attendance': '-', 'progress': '-'},
            {'date': '26/07/2025', 'session': '24', 'lesson': 'Quiz 2 https://forms.gle/VE31bFQVGTczFWnX9 ', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '19/07/2025', 'session': '23', 'lesson': 'L23 prepare presentation https://www.telebort.com/demo/ai2/project/7', 'attendance': 'Soumiya', 'progress': 'In Progress'},
            {'date': '12/07/2025', 'session': '22', 'lesson': 'L23 prepare presentation https://www.telebort.com/demo/ai2/project/7', 'attendance': 'No Class', 'progress': '-'},
            {'date': '05/07/2025', 'session': '22', 'lesson': 'L22 Project Prototype: COMPLETED', 'attendance': 'Soumiya', 'progress': 'Completed'},
            {'date': '28/06/2025', 'session': '21', 'lesson': 'L22 Project Prototype: IN PROGRESS', 'attendance': 'Soumiya', 'progress': ''}
        ]
    }
]

def process_missing_students():
    """Process missing students with proper data structure"""
    processor = DataProcessor()
    generator = ReportGenerator()
    
    processed_count = 0
    error_count = 0
    
    for student in missing_students:
        try:
            student_id = student['student_id']
            student_name = student['student_name']
            
            print(f"\n{processed_count+1}. Processing {student_id} - {student_name}")
            
            # Create student data structure expected by processor
            student_data = {
                'info': {
                    'student_id': student_id,
                    'student_name': student_name,
                    'program': student['program'],
                    'day': '',
                    'start_time': '',
                    'end_time': '',
                    'teacher': ''
                },
                'sessions': student['sessions']
            }
            
            # Process the data
            processed_data = processor.process_student(student_data)
            
            # Generate report
            report_path = generator.generate_report(processed_data)
            print(f"   ✓ Report generated: {report_path}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"   ✗ Error processing {student_id}: {str(e)}")
            error_count += 1
    
    return processed_count, error_count

def main():
    print("Processing 18 missing students from batches 7 and 8...")
    
    processed, errors = process_missing_students()
    
    print("\n" + "="*60)
    print("MISSING STUDENTS PROCESSING SUMMARY")
    print("="*60)
    print(f"Total students: {len(missing_students)}")
    print(f"Processed: {processed}")
    print(f"Reports generated: {processed}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()