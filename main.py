from flask import Flask, render_template, request, redirect, url_for, session, flash
from init_db import get_connection
from admin import db_name, secret_key

app = Flask(__name__)
app.secret_key = secret_key
DATABASE_NAME = db_name


def get_task(task_id):
    with get_connection(DATABASE_NAME) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""SELECT id, category, task_name, priority, status, time FROM tasks WHERE id = {task_id}""")
            task = cursor.fetchone()

    return {
            'id': task[0],
            'category': task[1],
            'task_name': task[2],
            'priority': task[3],
            'status': task[4],
            'time': task[5]
        }


@app.route('/')
def home():
    return redirect(url_for('register'))


@app.route('/index')
def index():
    user_id = session.get('user_id')

    if user_id:
        with get_connection(DATABASE_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, category, task_name, priority, status, time FROM tasks WHERE user_id = %s", (user_id,))
                tasks = cursor.fetchall()
        return render_template('index.html', tasks=tasks)
    else:
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with get_connection(DATABASE_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with get_connection(DATABASE_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('login'))


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        category = request.form['category']
        task_name = request.form['task_name']
        priority = request.form['priority']
        status = request.form['status']

        user_id = session.get('user_id')
        with get_connection(DATABASE_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO tasks (user_id, category, task_name, priority, status) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, category, task_name, priority, status))
                conn.commit()

            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:task_id>/edit', methods=['GET', 'POST'])
def edit(task_id):
    task = get_task(task_id)
    if request.method == 'POST':
        print(request.form)
        category = request.form['category']
        task_name = request.form['task_name']
        priority = request.form['priority']
        status = request.form['status']
        if not category or not task_name or not priority or not status:
            flash('Title, content and author are required!')
        else:
            with get_connection(DATABASE_NAME) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        UPDATE tasks
                        SET category = '{category}',
                        task_name  = '{task_name}',
                        priority = '{priority}',
                        status = '{status}'
                        WHERE id = {task_id}
                                        """)
                    conn.commit()
            return redirect(url_for('index'))
        return render_template('edit.html', task=task)


@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    with get_connection(DATABASE_NAME) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
