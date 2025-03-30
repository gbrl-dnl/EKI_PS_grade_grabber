#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup
import re
import statistics

def fetch_grade_data(url):
    response = requests.get(url)
    return response.text

def find_student_line(html_content, student_id):
    soup = BeautifulSoup(html_content, 'html.parser')
    table_rows = soup.find_all('tr')
    
    for row in table_rows:
        cells = row.find_all('td')
        for cell in cells:
            text = cell.get_text().strip()
            if student_id in text:
                return row
    
    return None

def extract_grades(row):
    if not row:
        return []
    
    cells = row.find_all('td')
    grades = []
    
    # Skip the first cell as it typically contains the student ID
    for cell in cells[1:]:
        text = cell.get_text().strip()
        
        # Only process cells that look like grade data
        # Standard format: 4-5 digits, each 1-5
        if re.match(r'^[1-5]{4,5}$', text):
            for grade in text:
                grades.append(int(grade))
                
        # Special format with vertical bars: digits 1-5 separated by |
        elif '|' in text and re.match(r'^[1-5\|]+$', text):
            parts = text.split('|')
            for part in parts:
                for grade in part:
                    grades.append(int(grade))
    
    return grades

def calculate_grade(grades):
    if not grades:
        return "No grades found"
    
    average = statistics.mean(grades)
    
    # Apply grading rules based on the website's explanation
    if average < 3.5:
        return f"Current average: {average:.2f} - Good standing, no mandatory final test"
    elif average < 4.5:
        return f"Current average: {average:.2f} - Mandatory final test required"
    else:
        return f"Current average: {average:.2f} - Currently not passing"

def save_to_file(student_id, grades, result, filename):
    with open(filename, 'a') as f:  # Changed to append mode
        f.write(f"# Grade Calculation for Student ID ending with {student_id}\n\n")
        f.write(f"## Raw Grades\n")
        f.write(f"{grades}\n\n")
        f.write(f"## Result\n")
        f.write(f"{result}\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python grade_calc.py STUDENT_ID")
        sys.exit(1)
    
    student_id = sys.argv[1]
    
    # Validate that the input is a 3-digit number
    if not (student_id.isdigit() and len(student_id) == 3):
        print("Error: STUDENT_ID must be a 3-digit number")
        sys.exit(1)
    
    url = "https://www.cosy.sbg.ac.at/~uhl/points.html"
    
    try:
        html_content = fetch_grade_data(url)
        student_row = find_student_line(html_content, student_id)
        
        if not student_row:
            print(f"No data found for student ID ending with {student_id}")
            sys.exit(1)
        
        # Debug: Print the raw row data to see what we're dealing with
        print("Found student row:")
        cells = student_row.find_all('td')
        for i, cell in enumerate(cells):
            print(f"Cell {i}: '{cell.get_text().strip()}'")
            
        grades = extract_grades(student_row)
        print(f"Extracted grades: {grades}")
        
        result = calculate_grade(grades)
        
        # Clear the file before writing
        with open("calculations.md", 'w') as f:
            pass
            
        save_to_file(student_id, grades, result, "calculations.md")
        # print file content
        with open("calculations.md", "r") as f:
            print(f.read())
        print(f"Results saved to calculations.md")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 