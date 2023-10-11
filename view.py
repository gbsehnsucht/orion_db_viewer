from sql_funcs import *
from tkinter import *
from tkinter import ttk


conn = None
code_id = 0
code_type = ''
patterns = {
               'Карта': r'^[0-9, A-F]{16}$',
               'Пароль': r'^.{1,}$',
               'date': r'^((19|20)\d\d)-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|'
                       r'((0[469]|11)-(0[1-9]|[12][0-9]|30))|'
                       r'((02)-(0[1-9]|1[0-9]|2[0-8])))$'
            }


def validate_code(code):
    return re.compile(patterns[code_type]).match(code) is not None


def validate_date(date):
    return re.compile(patterns['date']).match(date) is not None or date == 'NULL' or not date


def clear_table(event):
    table.delete(*table.get_children())


def disable_change_widgets():
    btn_change.configure(state='disabled')
    btn_save.configure(state='disabled')
    for widget in entry_of_change:
        widget.configure(state='normal')
        widget.delete(0, END)
        widget.configure(state='disabled')


def forget_err_frame(label, frame):
    label.configure(text='')
    frame.place_forget()


def check_changes(name, surname, code, start, finish):
    if not name or not surname:
        return 'Некорректные имя и фамилия!'
    if not validate_code(code):
        return 'Некорректный код!'
    if not validate_date(start) or not validate_date(finish):
        return 'Дата не соответствует формату: ГГГГ-ММ-ЧЧ!'


def conn_error_handle(exception):
    e_code, e_text = exception.args[0], exception.args[1]
    if e_code == 'HY000' or e_code == 'HYT00':
        return 'Неверно выбран драйвер!'
    if e_code == '08001':
        return 'Сервер не найден или недоступен!'
    if e_code == '28000' and 'Не удается открыть базу данных' in e_text:
        return 'Не найдена база данных!'
    if e_code == '28000':
        return 'Неверные UID/PWD!'


def connect_to_sql():
    global conn
    driver = combobox_driver.get()
    server = entry_server.get()
    db = entry_db.get()
    uid = entry_uid.get()
    pwd = entry_pwd.get()
    if '' in [driver, server, db, uid, pwd]:
        frame_err_conn.place(relx=0.74, rely=0.34, height=40, width=300)
        lbl_err_conn.configure(text='Введены неполные данные!')
    else:
        try:
            conn = get_connection(driver, server, db, uid, pwd)
            forget_err_frame(lbl_err_conn, frame_err_conn)
        except Exception as e:
            conn = None if conn else conn
            frame_err_conn.place(relx=0.74, rely=0.34, height=40, width=300)
            conn_error = conn_error_handle(e)
            lbl_err_conn.configure(text=conn_error)


def fill_table(sql_data):
    for row in sql_data:
        table.insert("", END, values=row)


def btn_connect_func():
    disable_change_widgets()
    connect_to_sql()
    if conn:
        fill_table(get_data(conn))


def btn_change_func():
    groups = get_groups(conn)
    combobox_level.configure(values=list(groups.keys()))
    btn_save.configure(state='normal')
    for widget in entry_of_change:
        widget.configure(state='normal')
    combobox_level.configure(state='readonly')


def btn_save_func():
    name = entry_name.get()
    surname = entry_surname.get()
    midname = entry_midname.get()
    code = entry_code.get()
    level = combobox_level.get()
    start = entry_start.get()
    finish = entry_finish.get()
    save_error = check_changes(name, surname, code, start, finish)
    if save_error:
        frame_err_save.place(relx=0.74, rely=0.87, height=40, width=300)
        lbl_err_save.configure(text=save_error)
    else:
        modified_data = [code_id, name, surname, midname, code_type, code, level, start, finish]
        forget_err_frame(lbl_err_save, frame_err_save)
        insert_data(conn, modified_data)
        clear_table('event')
        fill_table(get_data(conn))
        disable_change_widgets()


def get_selection(event):
    global code_id, code_type
    for selection in table.selection():
        item = table.item(selection)
        data = item['values']
        code_id, code_type = data[0], data[4]
        data = data[1:4] + data[5:]
        for widget in entry_of_change:
            widget.configure(state='normal')
            widget.delete(0, END)
            widget.insert(0, data[entry_of_change.index(widget)])
            widget.configure(state='readonly')
        combobox_level.configure(state='disabled')
    forget_err_frame(lbl_err_save, frame_err_save)
    btn_save.configure(state='disabled')
    if entry_name.cget('state') != 'disabled':
        btn_change.configure(state='normal')


window = Tk()
window.title('orion_db')
window.minsize(width=1300, height=600)
window.geometry('1300x600')

columns = ('#1', '#2', '#3', '#4', '#5', '#6', '#7', '#8', '#9')
table = ttk.Treeview(show='headings', columns=columns)
table.place(relx=0.01, rely=0.01, relwidth=0.7, relheight=0.96)

table.heading('#1', text='ID')
table.heading('#2', text='Имя')
table.heading('#3', text='Фамилия')
table.heading('#4', text='Отчество')
table.heading('#5', text='Тип кода')
table.heading('#6', text='Код')
table.heading('#7', text='Уровень доступа')
table.heading('#8', text='Начало')
table.heading('#9', text='Конец')

table.column('#1', width=40, stretch=False)
table.column('#2', width=110, stretch=False)
table.column('#3', width=110, stretch=False)
table.column('#4', width=110, stretch=False)
table.column('#5', width=75, stretch=False)
table.column('#6', width=150, stretch=False)
table.column('#7', width=120, stretch=False)
table.column('#8', width=95, stretch=False)
table.column('#9', width=95, stretch=False)

scrollbar_y = ttk.Scrollbar(orient=VERTICAL, command=table.yview)
scrollbar_y.place(relx=0.71, rely=0.01, relheight=0.94)
scrollbar_x = ttk.Scrollbar(orient=HORIZONTAL, command=table.xview)
scrollbar_x.place(relx=0.01, rely=0.95, relwidth=0.7)
table.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

table.bind('<<TreeviewSelect>>', get_selection)

lbl_driver = Label(text='Driver:')
lbl_driver.place(relx=0.73, rely=0.01)
lbl_server = Label(text='Server:')
lbl_server.place(relx=0.73, rely=0.06)
lbl_db = Label(text='Database:')
lbl_db.place(relx=0.73, rely=0.11)
lbl_uid = Label(text='UID:')
lbl_uid.place(relx=0.73, rely=0.16)
lbl_pwd = Label(text='Password:')
lbl_pwd.place(relx=0.73, rely=0.21)

combobox_driver = ttk.Combobox(values=drivers_list, state='readonly')
combobox_driver.place(relx=0.79, rely=0.01, width=250)
entry_server = Entry()
entry_server.place(relx=0.79, rely=0.06, width=250)
entry_db = Entry()
entry_db.place(relx=0.79, rely=0.11, width=250)
entry_uid = Entry()
entry_uid.place(relx=0.79, rely=0.16, width=250)
entry_pwd = Entry(show='*')
entry_pwd.place(relx=0.79, rely=0.21, width=250)

btn_connect = Button(window, text='Connect to SQL Server', command=btn_connect_func)
btn_connect.place(relx=0.75, rely=0.26, width=250)
btn_connect.bind('<ButtonPress-1>', clear_table)

frame_err_conn = Frame(borderwidth=4, relief=RIDGE)

lbl_err_conn = Label(frame_err_conn)
lbl_err_conn.pack(expand=True)

lbl_name = Label(text='Имя:')
lbl_name.place(relx=0.73, rely=0.46)
lbl_surname = Label(text='Фамилия:')
lbl_surname.place(relx=0.73, rely=0.51)
lbl_midname = Label(text='Отчество:')
lbl_midname.place(relx=0.73, rely=0.56)
lbl_code = Label(text='Код:')
lbl_code.place(relx=0.73, rely=0.61)
lbl_level = Label(text='Уровень:')
lbl_level.place(relx=0.73, rely=0.66)
lbl_start = Label(text='Начало:')
lbl_start.place(relx=0.73, rely=0.71)
lbl_finish = Label(text='Конец:')
lbl_finish.place(relx=0.73, rely=0.76)

entry_name = Entry()
entry_name.place(relx=0.79, rely=0.46, width=250)
entry_surname = Entry()
entry_surname.place(relx=0.79, rely=0.51, width=250)
entry_midname = Entry()
entry_midname.place(relx=0.79, rely=0.56, width=250)
entry_code = Entry()
entry_code.place(relx=0.79, rely=0.61, width=250)
combobox_level = ttk.Combobox(state='readonly')
combobox_level.place(relx=0.79, rely=0.66, width=250)
entry_start = Entry()
entry_start.place(relx=0.79, rely=0.71, width=250)
entry_finish = Entry()
entry_finish.place(relx=0.79, rely=0.76, width=250)

btn_change = Button(window, text='Изменить', command=btn_change_func)
btn_change.place(relx=0.75, rely=0.81, width=115)
btn_change.configure(state='disabled')

btn_save = Button(window, text='Сохранить', command=btn_save_func)
btn_save.place(relx=0.85, rely=0.81, width=115)
btn_save.configure(state='disabled')

frame_err_save = Frame(borderwidth=4, relief=RIDGE)

lbl_err_save = Label(frame_err_save)
lbl_err_save.pack(expand=True)

entry_of_change = [entry_name, entry_surname, entry_midname, entry_code, combobox_level, entry_start, entry_finish]
for entry in entry_of_change:
    entry.configure(state='disabled')

window.mainloop()
