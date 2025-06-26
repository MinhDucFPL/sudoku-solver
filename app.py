from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import pytesseract
import os
from solver import solve
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_sudoku_grid(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ... đơn giản hóa: cắt 9x9 ô vuông theo tỷ lệ
    height, width = gray.shape
    cell_h, cell_w = height // 9, width // 9

    board = []
    for i in range(9):
        row = []
        for j in range(9):
            cell = gray[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
            text = pytesseract.image_to_string(cell, config='--psm 10 digits')
            try:
                row.append(int(text.strip()))
            except:
                row.append(0)
        board.append(row)
    return board

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files['sudoku_image']
        filename = secure_filename(f.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(path)
        grid = extract_sudoku_grid(path)
        return render_template('index.html', grid=grid)
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve_sudoku():
    board = []
    for i in range(9):
        row = []
        for j in range(9):
            val = request.form.get(f'cell-{i}-{j}')
            row.append(int(val) if val and val.isdigit() else 0)
        board.append(row)

    solved_board = [row[:] for row in board]
    solve(solved_board)
    return render_template('result.html', original=board, solved=solved_board)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
