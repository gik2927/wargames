from flask import (
    Flask, request, redirect, url_for, render_template, 
    session, abort, g, flash, get_flashed_messages
)
import os
import hashlib
from datetime import datetime
import sqlite3
import click

from system.firewall import is_safe
import glob 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'redacted')
app.config['UPLOADS_DIR'] = 'uploads' 

DATABASE = 'database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            subject TEXT NOT NULL,
            grade TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    try:
        alice_pw = hashlib.sha256("pw11037".encode()).hexdigest()
        db.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("202511037", alice_pw, 'student')
        )
        db.commit()
        print("Default user '11037' (student) created.")
    except sqlite3.IntegrityError:
        print("Default user '11037' already exists.")
        
    try:
        teacher_pw = hashlib.sha256(os.urandom(16)).hexdigest()
        db.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("pro2153", teacher_pw, 'teacher')
        )
        db.commit()
        print("Flag user 'pro2153' created.")
    except sqlite3.IntegrityError:
        print("Flag user 'pro2153' already exists.")

    try:
        db.execute(
            "INSERT INTO grades (username, subject, grade) VALUES (?, ?, ?)",
            ("202511037", "사회언어학", "C")
        )
        db.commit()
    except sqlite3.IntegrityError:
        print("error")


@app.cli.command('init-db')
def init_db_command():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        click.echo('Dropped existing database.')
    init_db()
    click.echo('Initialized the database.')


@app.route('/')
def index():
    if not session.get('id'):
        return redirect(url_for('login'))
    
    visible_announcements = [a for a in announcements if not a.get('hidden', False)]
    
    return render_template(
        'index.html',
        user=session.get('id'), 
        announcements=visible_announcements, 
        role=session.get('role')
    )

announcements = [
    {
        'id': 2,
        'title': '사회언어학 시험 공지',
        'content': '시험 일시: 2025/10/10  <br>시험 장소: 213호 강의실',
        'created_at': datetime(2025, 10, 8, 12, 0, 0),
        'hidden': False  
    },
    {
        'id': 1,
        'title': '보안 담당자 메모',
        'content': '방화벽 업데이트 예정 <br> 필터링 키워드들을 system/key.txt에서 관리 중<br>key.txt 삭제 시 무력화되기 때문에 주의',
        'created_at': datetime(2025, 10, 2, 9, 43, 12),
        'hidden': True 
    },
        {
        'id': 0,
        'title': '보안 업데이트',
        'content': '과제 관리 페이지 필터링 추가 <br> ..와 /로 시작할 때 필터링 추가',
        'created_at': datetime(2025, 9, 24, 1, 23, 17),
        'hidden': True  
    },
]

@app.route('/announce/<int:aid>')
def view_announcement(aid):
    if not session.get('id'):
        return redirect(url_for('login'))
        
    found_ann = None
    
    for a in announcements:
        if a['id'] == aid:
            found_ann = a
            break
            
    if found_ann:
        return render_template('view.html', ann=found_ann)
    else:
        abort(404)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not is_safe(username) or not is_safe(password):
            error = "Firewall: Malicious input detected."
            return render_template('login.html', error=error)

        db = get_db()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password_hash}'"
        
        try:
            user = db.execute(query).fetchone()
            
            if user:
                session['id'] = user['username']
                session['role'] = user['role'] 
                return redirect(url_for('index'))
            else:
                error = "id/pw가 틀렸습니다."
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
            error = "잘못된 요청입니다."
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('role', None) 
    return redirect(url_for('login'))

@app.route('/grades', methods=['GET', 'POST'])
def manage_grades():
    if not session.get('id'):
        return redirect(url_for('login'))
    
    db = get_db()
    role = session.get('role')
    
    if role == 'teacher':
        
        if request.method == 'POST':
            student_username = request.form['username']
            new_grade = request.form['new_grade']
            
            current_grade_row = db.execute(
                'SELECT grade FROM grades WHERE username = ?',
                (student_username,)
            ).fetchone()

            if not current_grade_row:
                flash(f"오류: '{student_username}' 학생을 찾을 수 없습니다.", "error")
                return redirect(url_for('manage_grades'))
            
            old_grade = current_grade_row['grade']
            
            db.execute(
                'UPDATE grades SET grade = ? WHERE username = ?',
                (new_grade, student_username)
            )
            db.commit()
            success_message = f"성공: {student_username} 학생의 성적을 '{old_grade}'에서 '{new_grade}'로 변경했습니다."
            
            if student_username == '202511037' and old_grade == 'C' and new_grade == 'A':
                flag = "4TH3N3{redacted}"
                flash(f"{success_message} - {flag}", "success")
            else:
                flash(success_message, "success")
                
            return redirect(url_for('manage_grades'))
        
        all_grades = db.execute(
            'SELECT username, subject, grade FROM grades'
        ).fetchall()
        
        return render_template('grades.html', grades=all_grades)

    else:
        
        if request.method == 'POST':
            abort(403) 
        
        my_username = session.get('id')
        
        my_grades = db.execute(
            'SELECT username, subject, grade FROM grades WHERE username = ?',
            (my_username,)
        ).fetchall()
        
        return render_template('gradestu.html', grades=my_grades)


@app.route('/assignments', methods=['GET'])
def assignments():
    if not session.get('id'):
        return redirect(url_for('login'))

    search_query = request.args.get('q', '')
    search_results = []
    error = None
    
    base_dir = os.path.join(app.config['UPLOADS_DIR'], session['id'])
    os.makedirs(base_dir, exist_ok=True)

    if search_query.startswith('..') or search_query.startswith('/'):
        error = "SecurityError: 부적절한 경로 탐색이 감지되었습니다."
    elif search_query:
        search_path = os.path.join(base_dir, search_query)
        try:
            full_paths = glob.glob(search_path)

            search_results = [os.path.relpath(p, base_dir) for p in full_paths]
            
        except Exception as e:
            error = f"SearchError: {e}"

    return render_template('assignments.html',
                           query=search_query,
                           results=search_results, 
                           error=error)


@app.route('/assignment/delete', methods=['POST'])
def delete_assignment():
    if not session.get('id'):
        return redirect(url_for('login'))

    rel_filepath = request.form.get('filepath', '')
    if not rel_filepath:
        flash("파일 경로가 지정되지 않았습니다.", "error")
        return redirect(url_for('assignments',q='*'))


    if rel_filepath.startswith('..') or rel_filepath.startswith('/'):
        flash("SecurityError: 부적절한 경로 접근입니다. ('..' 또는 '/' 사용 불가)", "error")
        return redirect(url_for('assignments',q='*'))

    base_dir = os.path.join(app.config['UPLOADS_DIR'], session['id'])
    target_path = os.path.join(base_dir, rel_filepath)

    safe_target_path = os.path.abspath(target_path)
    
    print(f"[DEBUG] 5. 최종 절대 경로 (safe_target_path): '{safe_target_path}'")

    try:
        exists = os.path.exists(safe_target_path)

        if not exists:
            flash(f"파일을 찾을 수 없습니다: {rel_filepath}", "error")
        elif os.path.isdir(safe_target_path):
             flash(f"디렉토리는 삭제할 수 없습니다: {rel_filepath}", "error")
        else:
            os.remove(safe_target_path)
            flash(f"파일이 성공적으로 삭제되었습니다: {rel_filepath}", "success")
            
    except Exception as e:
        flash(f"파일 삭제 중 오류 발생: {e}", "error")
    return redirect(url_for('assignments',q='*'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

