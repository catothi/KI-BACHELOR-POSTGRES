# Importing packages
import psycopg2

# Forming connection
conn = psycopg2.connect(
    database="psy_demo",
    user='postgres',
    password='cato',
    host='127.0.0.1',
    port='5432'
)

conn.autocommit = True

# Creating a cursor
cursor = conn.cursor()

# Creating table emp_table
cursor.execute('''
    DROP TABLE IF EXISTS emp_table

''')
conn.commit()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS emp_table (
        emp_code INT PRIMARY KEY,
        emp_name VARCHAR(30),
        emp_salary DECIMAL
    )
''')

# List of rows to be inserted
values = [
    (34545, 'samuel', 48000.0),
    (34546, 'rachel', 23232.0),  # Ensure the salary is a float
    (34547, 'Sean', 92000.0)
]

# cursor.mogrify() to insert multiple values
args = ','.join(cursor.mogrify("(%s,%s,%s)", i).decode('utf-8')
                for i in values)

print("Das sind args " + args + " Ende")

# Executing the SQL statement
cursor.execute("INSERT INTO emp_table (emp_code, emp_name, emp_salary) VALUES " + args)

# Select statement to display output
sql1 = '''SELECT * FROM emp_table;'''

# Executing SQL statement
cursor.execute(sql1)

# Fetching rows
for i in cursor.fetchall():
    print(i)

# Committing changes
conn.commit()

# Closing connection
conn.close()
