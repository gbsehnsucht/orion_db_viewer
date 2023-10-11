from code_funcs import *
import datetime
import pyodbc


drivers_list = pyodbc.drivers()


def get_connection(driver, server, db, uid, pwd):

    connection_string = (
        f"Driver={driver};"
        f"Server={server};"
        f"Database={db};"
        f"UID={uid};"
        f"PWD={pwd};"
    )
    conn = pyodbc.connect(connection_string)

    return conn


def get_data(conn):

    query = '''select ID, Name, FirstName, MidName, Gtype, CodeP, Group_name, Start, Finish from
    (select * from (select * from (select ID, Gtype, Owner, CodeP, GroupID, Start, Finish from pMark) as pmark join
    (select ID as group_id, Name as Group_name from Groups) as groups on pmark.GroupID = groups.group_id) as sub join
    (select ID as owner_id, Name, FirstName, MidName from pList) as plist on sub.Owner = plist.owner_id) as result;'''
    result = conn.execute(query)
    rows = result.fetchall()
    db_data = []

    for row in rows:
        row_list = []
        for cell in range(len(row)):
            if cell == 5 and row[4] == 4:
                row_list.extend(['Карта', encoding_ascii(row[cell])[:-2]])
            if cell == 5 and row[4] == 1:
                row_list.extend(['Пароль', encoding_pass(row[cell])])
            if cell == 7 or cell == 8:
                row_list.append(row[cell].date()) if row[cell] else row_list.append('')
            elif cell != 4 and cell != 5:
                row_list.append(row[cell])
        db_data.append(row_list)

    return db_data


def get_groups(conn):
    query = 'select ID, Name from Groups;'
    result = conn.execute(query)
    rows = result.fetchall()
    groups = {}

    for row in rows:
        groups[row[1]] = row[0]

    return groups


def insert_data(conn, modified_data):
    query_owner = f'select Owner from pMark where ID = {modified_data[0]};'
    owner = conn.execute(query_owner).fetchall()[0][0]

    query_modify_plist = f"update pList set Name = '{modified_data[1]}', " \
                         f"FirstName = '{modified_data[2]}', MidName = '{modified_data[3]}' where ID = '{owner}';"
    conn.execute(query_modify_plist)
    conn.commit()

    code_p = modified_data[5]
    if modified_data[4] == 'Карта':
        code_p = decoding_card(code_p)
    if modified_data[4] == 'Пароль':
        code_p = decoding_pass(code_p)
    if "'" in code_p:
        code_p = code_p.replace("'", "''")

    group_id = get_groups(conn)[modified_data[6]]
    start = modified_data[7].replace('-', '')
    finish = modified_data[8].replace('-', '')

    query_modify_pmark = f"update pMark set CodeP = '{code_p}', GroupID = {group_id}," \
                         f"Start = '{start}', Finish = '{finish}' where ID = {modified_data[0]};"
    conn.execute(query_modify_pmark)
    conn.commit()
