from flask import Flask
import re
from flask_cors import CORS
from PyPDF2 import PdfReader
import json
import io
from flask import Flask, request
import requests

app = Flask(__name__)
CORS(app)



@app.route("/send", methods=["POST"])
def receive_data():
    data = request.json  # Extract JSON data from the request body
    # Process the received data as needed
    # print("Received data:", data)

    url = data

    response = requests.get(url)
    pdf_bytes = io.BytesIO(response.content)

    # Read the PDF content using PdfReader
    reader = PdfReader(pdf_bytes)
    page = reader.pages[0]
    text = page.extract_text()

    # reader = PdfReader("pdf/22eskcy011.pdf")
    # page = reader.pages[0]
    # text = page.extract_text()

    gradeMapping = {
        "A++": 10,
        "A+": 9,
        "A": 8.5,
        "B+": 8,
        "B": 7.5,
        "C+": 7,
        "C": 6.5,
        "D+": 6,
        "D": 5.5,
        "E+": 5,
        "E": 4.5,
        "F": 0,
    }

    roll_no_pattern = r"Roll No\s*:\s*(\w+)"
    roll_no_match = re.search(roll_no_pattern, text)
    roll_no = roll_no_match.group(1) if roll_no_match else ""

    remark_pattern = r"REMARKS\s*:\s*(\w+)"
    remark_match = re.search(remark_pattern, text)
    remark = remark_match.group(1) if remark_match else ""

    name_pattern = r"Name\s*:\s*(.*)\s*Father's Name"
    name_match = re.search(name_pattern, text)
    name = name_match.group(1).strip() if name_match else ""

    sem_name_pattern = r"B. Tech\s*(.*)\s*"
    sem_name_match = re.search(sem_name_pattern, text)
    sem_name = sem_name_match.group(1).strip() if sem_name_match else ""

    father_name_pattern = r"Father's Name\s*:\s*(.*)\s*"
    father_name_pattern = re.search(father_name_pattern, text)
    father_name = father_name_pattern.group(1).strip() if father_name_pattern else ""

    sem_no_pattern = r"(\w+-\d+)"
    sem_no_pattern = re.search(sem_no_pattern, text)
    sem_no = sem_no_pattern.group(1).strip() if sem_no_pattern else ""

    College_name_pattern = r"College Name\s*:\s*(.*)\s*"
    College_name_pattern = re.search(College_name_pattern, text)
    College_name = College_name_pattern.group(1).strip() if College_name_pattern else ""

    Sodeca_name_pattern = r"SODECA (\w+-\d+) (\d+) (\w\++)"
    matches = re.findall(Sodeca_name_pattern, text)
    sodeca_data = [
        {"Sodeca_Code": match1[0], "Sodeca_EndTerm": match1[1], "Grade:": match1[2]}
        for match1 in matches
    ]

    # pattern = r"(.+?) (\w+-\d+) (\d+) (\d+) (\w+\+*)"

    # matches = re.findall(pattern, text)

    patterns = [
        r"(.+?) (\w+-\d+) (\d+) (\d+) (\w+\+*)",  # Pattern to matches like 8CS4-01
        r"(.+?) (\w+-\d+\.\d+) (\d+) (\d+) (\w+\+*)",  # Pattern to match like   8AG6-60.1
    ]

    # Find all matches in the text
    matches = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, text))

    table_data = [
        {
            "Subject_Name": match[0],
            "Subject_Code": match[1],
            "Internal_Marks": match[2],
            "External_Marks": match[3],
            "Total_Marks": str(int(match[2]) + int(match[3])),
            "Grade": match[4],
            "Final_Marks": int(match[2]) + int(match[3]),
            "Points": gradeMapping.get(match[4], 0),
        }
        for match in matches
    ]

    # table_data = sorted(table_data, key=lambda x: x['Total_Marks'], reverse=True)

    final_marks = sum(row["Final_Marks"] for row in table_data)
    total_points = sum(row["Points"] for row in table_data)

    total_rows = len(table_data)
    data = {
        "Name": name,
        "father_name": father_name,
        "College_name": College_name,
        "Roll_No": roll_no,
        "sem_name": sem_name,
        "Result": remark,
        "Percentage": final_marks / total_rows,
        "Subjects": table_data,
        "Sodeca": sodeca_data,
        "total_points": total_points,
        "semester": sem_no[0:1],
    }
    json_data = json.dumps(data, indent=4)

    # Send back a response
    # response_data = {"message": "Data received successfully"}

    return json_data, 200


# if __name__ == "__main__":
#     app.run()
