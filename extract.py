import os
import pandas as pd
from datetime import datetime

# Data
data1 = 'Jarold, Macy Dane O.\n8- RUBY\n123456789014\n'
data2 = 'Doe, John\n9- DIAMOND\n123456789014\n'

# Splitting data1
grade_section1 = data1.split('\n')[1]
student_name1 = data1.split('\n')[0]
student_grade1 = grade_section1.split('-')[0].strip()
student_section1 = grade_section1.split('-')[1][1:].strip()
student_lrn1 = data1.split('\n')[2]

# Splitting data2
grade_section2 = data2.split('\n')[1]
student_name2 = data2.split('\n')[0]
student_grade2 = grade_section2.split('-')[0].strip()
student_section2 = grade_section2.split('-')[1][1:].strip()
student_lrn2 = data2.split('\n')[2]

# Creating DataFrame
df = pd.DataFrame({
    'Name': [student_name1, student_name2],
    'Grade': [student_grade1, student_grade2],
    'Section': [student_section1, student_section2],
    'LRN': [student_lrn1, student_lrn2]
})

# Creating output folder if not exists
output_folder = 'output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Generating file name with current date and time
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
file_name = f'student_data_{current_time}.csv'
file_path = os.path.join(output_folder, file_name)

# Export to CSV
df.to_csv(file_path, index=False)

print(f"File saved to: {file_path}")
