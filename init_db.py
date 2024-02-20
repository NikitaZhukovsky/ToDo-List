import psycopg2
from admin import password


def get_connection(db_name):
    connection = psycopg2.connect(
        dbname=db_name,
        host='localhost',
        port='5432',
        user='postgres',
        password=password
    )
    return connection


def main():
    with get_connection('todo_db') as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                 CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
                );
                """
            )
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                user_id INTEGER, 
                FOREIGN KEY (user_id) REFERENCES users (id) ON UPDATE CASCADE ON DELETE CASCADE,
                category TEXT NOT NULL,
                task_name TEXT NOT NULL,
                priority TEXT,
                status TEXT,
                time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """
            )
            conn.commit()


if __name__ == '__main__':
    main()
