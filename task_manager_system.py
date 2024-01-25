
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta


class TaskManager:
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
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks_ (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                due_date DATE NOT NULL,
                priority INT DEFAULT 1,
                assigned_to VARCHAR(255),
                status VARCHAR(20) DEFAULT 'Pending',
                completed BOOLEAN NOT NULL
            )
        ''')
        self.connection.commit()
    


    def add_task(self, title, description, due_date, priority=1, assigned_to=None):
        query = "INSERT INTO tasks_ (title, description, due_date, priority, assigned_to, completed) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (title, description, due_date, priority, assigned_to, False)
        self.cursor.execute(query, values)
        self.connection.commit()
        print(f'Task "{title}" added successfully!')

    def view_tasks(self, assigned_to=None):
        if assigned_to:
            query = "SELECT id, title, due_date, priority, status, completed FROM tasks_ WHERE assigned_to = %s"
            values = (assigned_to,)
        else:
            query = "SELECT id, title,  due_date, priority, status, completed FROM tasks_"
            values = None

        self.cursor.execute(query, values)
        tasks = self.cursor.fetchall()

        if not tasks:
            print("No tasks available.")
        
        else:
            
            for task in tasks:
                status = "Completed" if task[5] else task[4]
                print(f"{task[0]} task title: {task[1]} - Due Date: {task[2]} - Priority: {task[3]} - Status: {status}")

        

    def update_task_details(self, task_id, status=None, due_date=None):
        updates = []
        if status:
            updates.append(("status", status))
        if due_date:
            updates.append(("due_date", due_date))

        if not updates:
            print("No updates provided.")
            return

        set_clause = ", ".join([f"{field} = %s" for field, _ in updates])
        values = [value for _, value in updates]
        values.append(task_id)

        query = f"UPDATE tasks_ SET {set_clause} WHERE id = %s"
        self.cursor.execute(query, values)
        self.connection.commit()
        print(f'Task with ID {task_id} updated successfully.')

    def assign_task(self, task_id, assigned_to):
        query = "UPDATE tasks_ SET assigned_to = %s WHERE id = %s"
        values = (assigned_to, task_id)
        self.cursor.execute(query, values)
        self.connection.commit()
        print(f'Task with ID {task_id} assigned to {assigned_to}.')

    
    def view_assign_task(self, assigned_to=None):
        if assigned_to:
            query = "SELECT id, title, due_date, priority, status FROM tasks_ WHERE assigned_to = %s"
            values = (assigned_to,)
        else:
            query = "SELECT id, title,  due_date, priority, status FROM tasks_"
            values = None

        self.cursor.execute(query, values)
        tasks = self.cursor.fetchall()

        if not tasks:
            print("No tasks available.")
        
        else:
            
            for task in tasks:
                print(f"{task[0]} task title: {task[1]} - Due Date: {task[2]} - Priority: {task[3]} - Status: {task[4]}")
        
    
    def mark_task_completed(self, task_id):
        query = "UPDATE tasks_ SET status = 'completed' WHERE id = %s"
        values = (task_id,)
        self.cursor.execute(query, values)
        self.connection.commit()
        print(f'Task with ID {task_id} marked as completed.')

    def remove_task(self, task_id):
        query = "DELETE FROM tasks_ WHERE id = %s"
        values = (task_id,)
        self.cursor.execute(query, values)
        self.connection.commit()
        print(f'Task with ID {task_id} removed successfully.')

    def members(self):
        query = "SELECT assigned_to FROM tasks_"
        values = None
        self.cursor.execute(query, values)
        tasks = self.cursor.fetchall()
        self.connection.commit()

        if not tasks:
            print("No tasks available.")
        
        else:  
            for task in tasks:
                print(task)



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

def main():
    db_host = "localhost"
    db_user = "root"
    db_password = "Master#123"
    db_database = "Task_db"

    task_manager = TaskManager(db_host, db_user, db_password, db_database)
    task_comments = TaskComments(db_host, db_user, db_password, db_database)

    while True:
        print("\n===== Task Management System Menu  =====")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task Details")
        print("4. Assign Task")
        print("5. View Assigned Tasks")
        print("6. Mark Task completed")
        print("7. Delete the task")
        print("8. Add Task Comment")
        print("9. View All Task Comments")
        print("10. Generate Reports")
        print("11. Notify Team Members")
        print("12. Exit")

        choice = input("Enter your choice (1-12): ")

        try:
            if choice == '1':
                try:
                    title = input("Enter task title: ")
                    description = input("Enter task description: ")
                    due_date_str = input("Enter due date (YYYY-MM-DD): ")
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                    priority = int(input("Enter priority (1-5): "))
                    assigned_to = input("Assign task to (leave blank for unassigned): ")
                    task_manager.add_task(title, description, due_date, priority, assigned_to)
                except (ValueError, TypeError) as e:
                    print("Error adding task:", e)

            elif choice == '2':
                try:
                    assigned_to = input("Enter team member's name (leave blank to view all tasks): ")
                    task_manager.view_tasks(assigned_to)
                except mysql.connector.Error as e:
                    print("MySQL Error:", e)

            elif choice == '3':
                try:
                    task_manager.view_tasks()
                    task_id = int(input("Enter the ID of the task to update: "))
                    status = input("Enter new status (leave blank to keep current): ")
                    due_date_str = input("Enter new due date (YYYY-MM-DD, leave blank to keep current): ")
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
                    task_manager.update_task_details(task_id, status, due_date)
                except (ValueError, TypeError) as e:
                    print("Error updating task details:", e)

            elif choice == '4':
                try:
                    task_manager.view_tasks()
                    task_id = int(input("Enter the ID of the task to assign: "))
                    assigned_to = input("Enter the team member's name: ")
                    task_manager.assign_task(task_id, assigned_to)
                except (ValueError, TypeError) as e:
                    print("Error assigning task:", e)

            elif choice =='5':
                try:
                    assigned_to = input("Enter the team member's name(leave blank to get all assigned tasks): ")
                    task_manager.view_assign_task(assigned_to)
                except mysql.connector.Error as e:
                    print("MySQL Error:", e)

            elif choice == '6':
                try:
                    task_manager.view_tasks()
                    task_id = int(input("Enter the ID of the task to mark as completed: "))
                    task_manager.mark_task_completed(task_id)
                except (ValueError,TypeError) as e:
                    print("Error while marking task completed:",e)

            elif choice == '7':
                try:
                    task_manager.view_tasks()
                    task_id = int(input("Enter the ID of the task to remove: "))
                    task_manager.remove_task(task_id)
                except (ValueError,TypeError) as e:
                    print("Error while removing the task:",e)

            elif choice == '8':
                try:
                    task_manager.view_tasks()
                    task_id = int(input("Enter the ID of the task to add a comment: "))
                    comment = input("Enter the comment: ")
                    task_comments.add_task_comment(task_id, comment)
                except (ValueError, TypeError) as e:
                    print("Error adding task comment:", e)

            elif choice == '9':
                try:
                    task_comments.view_commnts()
                except mysql.connector.Error as e:
                    print("MySQL Error:", e)

            elif choice == '10':
                try:
                    print("Report details are downloading ")
                    task_comments.generate_reports()
                except (ValueError, TypeError) as e:
                    print("Error generating reports:", e)

            elif choice == '11':
                try:
                    task_manager.members()
                    assigned_to = input("Enter the team member name to generate their task report: ")
                    task_comments.view_assign_task_by_member(assigned_to)
                except (ValueError, TypeError) as e:
                    print("Error viewing task report by member:", e)

            elif choice == '12':
                print("Exiting Task Management System. Have a great day!")
                break

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
