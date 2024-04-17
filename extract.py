import pandas as pd 

data=  'Jumalon, Macy Jade O.\n8- RUBY\n462061150055\n'
student_name = data.split('\n')[0]
grade_section = data.split('\n')[1]
student_grade = grade_section.split('-')[0]
student_section = grade_section.split('-')[1][1:]
student_lrn = data.split('\n')[2]