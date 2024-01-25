import mysql.connector 
import pandas as pd
from datetime import datetime
class TaskComments(TaskManager):
    def __init__(self, db_host, db_user, db_password, db_database):
        self.connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_database
        )
        self.cursor = self.connection.cursor()
        self.initialize_database()

    def initialize_database(self):
        # Create a 'task_comments' table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id INT NOT NULL,
                comment TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks_(id) ON DELETE CASCADE
            )
        ''')
        self.connection.commit()

    def add_task_comment(self, task_id, comment):
        query = "INSERT INTO task_comments (task_id, comment) VALUES (%s, %s)"
        values = (task_id, comment)
        self.cursor.execute(query, values)
        self.connection.commit()
        print(f'Comment added to task with ID {task_id}.')

    
    def view_commnts(self, assigned_to=None):
        if assigned_to:
            query = "SELECT * FROM task_comments WHERE assigned_to = %s"
            values = (assigned_to,)
        else:
            query = "SELECT * FROM task_comments "
            values = None

        self.cursor.execute(query, values)
        comments = self.cursor.fetchall()

        if not comments:
            print("No tasks available.")
        else:
            for comment in comments:
                # status = "Completed" if comment[5] else task[4]
                print(f" Task_id:  {comment[1]} commented:{comment[2]}")



    # def generate_reports(self):
    #     query = "SELECT * FROM tasks_ LEFT JOIN task_comments ON tasks_.id = task_comments.task_id"
    #     self.cursor.execute(query)
    #     values = self.cursor.fetchall()
    #     if not values:
    #         print("no values recorded")
    #     else:
    #         for value in values:
    #             print(value)


    #here i am generating the excel report 
    def generate_reports(self):
        query = "SELECT tasks_.id, title, description, due_date, priority, assigned_to, status, task_comments.id, task_id, comment FROM tasks_ LEFT JOIN task_comments ON tasks_.id = task_comments.task_id"
        self.cursor.execute(query)
        values = self.cursor.fetchall()
        if not values:
            print("No values recorded")
        else:
            df = pd.DataFrame(values, columns=['tasks_.id', 'title', 'description', 'due_date', 'priority','assigned_to','status','task_comments.id','task_id','comment'])
            df.to_excel('reports.xlsx', index=False)
            print("Excel report generated successfully.")

    def view_assign_task_by_member(self, assigned_to=None):
        if assigned_to:
            query = "SELECT id, title, due_date, priority, status FROM tasks_ WHERE assigned_to = %s"
            values = (assigned_to,)
        else:
            return "Please slecet valid memeber name"

        self.cursor.execute(query, values)
        tasks = self.cursor.fetchall()

        if not tasks:
            print("No tasks available.")
            return  

        df = pd.DataFrame(tasks, columns=['ID', 'Title', 'Due Date', 'Priority', 'Status'])

        # Convert 'due_date' column to datetime format
        df['Due Date'] = pd.to_datetime(df['Due Date'])


        # Save the DataFrame to Excel with specified encoding
        file_name = assigned_to+'.xlsx'
        df.to_excel(file_name, index=False)
        print(f"Excel report generated successfully: {file_name}")