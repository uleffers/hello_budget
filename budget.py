import numpy as np
import sqlite3
import time

def new(folder, name):
    conn = sqlite3.connect('{}/{}.db'.format(folder,name))

    c = conn.cursor()

    #Definer din sql kommando
    command = """CREATE TABLE budget
    (amount FLOAT, allocate FLOAT, account INTEGER, category TEXT, day INTEGER, month INTEGER, year INTEGER, memo TEXT);
    """
    c.execute(command)
    #HUSK at commit'e! 
    conn.commit()

    #Når du er færdig kan du lukke forbindelsen
    conn.close()

def income(amount,account,date=0,memo=0,folder='data',name='budget'):
    conn = sqlite3.connect('{}/{}.db'.format(folder,name))
    c = conn.cursor()
    transaction = (amount, account.title())

    if date == 0:
        transaction = transaction + (int(time.strftime("%d")), int(time.strftime("%m")),int(time.strftime("%Y")),)
    else:
        dato = date.split('/')
        transaction = transaction + (int(dato[0]),int(dato[1]),int(dato[2]),)

    if memo != 0:
        transaction = transaction + (memo,)
        c.execute('INSERT INTO budget (amount, account, day, month, year, memo) VALUES (?,?,?,?,?,?)',transaction)
    else:
        c.execute('INSERT INTO budget (amount, account, day, month, year) VALUES (?,?,?,?,?)',transaction)

    conn.commit()
    conn.close()

def newtransaction(category,amount,account,accountto=0,date=0,memo=0,folder='data',name='budget'):
    conn = sqlite3.connect('{}/{}.db'.format(folder,name))
    c = conn.cursor()

    transaction = (-amount,account.title(), category.title())

    if date == 0:
        transaction = transaction + (int(time.strftime("%d")), int(time.strftime("%m")),int(time.strftime("%Y")),)
    else:
        dato = date.split('/')
        transaction = transaction + (int(dato[0]),int(dato[1]),int(dato[2]),)

    if memo != 0:
        transaction = transaction + (memo,)
        c.execute('INSERT INTO budget (amount, account, category, day, month, year, memo) VALUES (?,?,?,?,?,?,?)',transaction)
    else:
        c.execute('INSERT INTO budget (amount, account, category, day, month, year) VALUES (?,?,?,?,?,?)',transaction)
    conn.commit()
    conn.close()

def allocate(category,amount,date=0,folder='data',name='budget'):
    allocation = (category.title(), amount)
    if date == 0:
        day = int(time.strftime("%d"))
        month = int(time.strftime("%m"))
        year = int(time.strftime("%Y"))

    else:
        dato = date.split('/')
        day = int(dato[0])
        month = int(dato[1])
        year = int(dato[2])
    allocation = allocation + (day,month,year,)
    conn = sqlite3.connect('{}/{}.db'.format(folder,name))
    c = conn.cursor()
    c.execute('INSERT INTO budget (category,allocate, day, month, year) VALUES (?,?,?,?,?)',allocation)
    conn.commit()
    conn.close()

def accountinfo(folder='data',name='budget',month=0):
    conn = sqlite3.connect('{}/{}.db'.format(folder,name))
    c = conn.cursor()
    overview = []
    if month == 0:
        month = int(time.strftime("%m"))
    for row in c.execute('SELECT SUM(amount), account FROM budget WHERE account IS NOT NULL GROUP BY account;'):
        overview.append(row)
    just=15
    print("Kontooverblik")
    print("".ljust(just*4,'-'))
    for element in overview:
        print("{}:".format(element[1]).ljust(just)+"{}".format(element[0]).ljust(just))
    conn.commit()
    conn.close()

def update(wrong_columns,wrong_input,new_input,folder='data',name='budget'):
    conn = sqlite3.connect('{}/{}.db'.format(folder,name))
    c = conn.cursor()
    if wrong_columns.lower()=='category':
        c.execute("""UPDATE budget SET category = ? WHERE category=?;""",(new_input.title(),wrong_input.title()))
    elif wrongcolumns.lower()=='account':
        c.execute("""UPDATE budget SET account = ? WHERE account=?;""",(new_input.title(),wrong_input.title()))
    conn.commit()
    conn.close()

def showtransactions(folder='data',name='budget',month=0):
    conn = sqlite3.connect('{}/{}.db'.format(folder,name))
    c = conn.cursor()
    overview = []
    if month == 0:
        month = int(time.strftime("%m"))
    for row in c.execute('SELECT amount, category, memo, account FROM budget WHERE month=? AND allocate IS NULL;',(month,)):
        overview.append(row)
    month_translate = {1:'januar',2:'februar',3:'marts',4:'april',5:'maj',6:'juni',7:'juli',8:'august',9:'september',10:'oktober',11:'november',12:'december'}
    dist = 20
    print("Følgende transaktioner er foretaget i {} måned".format(month_translate[month]))
    print("")
    print("Konto".ljust(dist)+"Beløb".ljust(dist)+"Kategori".ljust(dist)+"Memo".ljust(dist))
    print("".ljust(4*dist,'-'))
    for i in range(0,len(overview)):
        if overview[i][1]==None:
            lst = list(overview[i])
            lst[1]="Indkomst"
            overview[i]=tuple(lst)
    for element in overview:
        if element[2]==None:
            print("{}".format(element[3]).ljust(dist)+"{}".format(element[0]).ljust(dist)+"{}".format(element[1]).ljust(dist))
        else:
            print("{}".format(element[3]).ljust(dist)+"{}".format(element[0]).ljust(dist)+"{}".format(element[1]).ljust(dist)+"{}".format(memo))
    conn.commit()
    conn.close()

def showbudget(folder='data',name='budget',month=0):
    month_translate = {1:'januar',2:'februar',3:'marts',4:'april',5:'maj',6:'juni',7:'juli',8:'august',9:'september',10:'oktober',11:'november',12:'december'}
    conn = sqlite3.connect('{}/{}.db'.format(folder,name))
    c = conn.cursor()
    budget_month = []
    budget_tot = []
    if month == 0:
        month=int(time.strftime("%m"))

    #Okay, first I'll look what's been budgeted and spend this month
    for row in c.execute('SELECT SUM(amount), SUM(allocate), category FROM budget WHERE month=? AND category IS NOT NULL GROUP BY category;',(month,)):
        budget_month.append(row)

    #And compare total income to total amount budgeted
    to_be_budgeted = []
    for row in c.execute("""SELECT SUM(amount) FROM budget WHERE amount>0;"""):
        to_be_budgeted.append(row)
    for row in c.execute("""SELECT SUM(allocate) FROM budget;"""):
        to_be_budgeted.append(row)

    #Which I'll need to substract any non liqued assets
    aktier = []
    for row in c.execute("""SELECT SUM(amount) FROM budget WHERE account='Aktier';"""):
        aktier.append(row)
    if aktier[0][0]==None:
        aktier=[[0]]

    for row in c.execute('SELECT SUM(amount), SUM(allocate), category FROM budget WHERE category IS NOT NULL GROUP BY category;'):
        budget_tot.append(row)

    print_var = []
    for element in budget_tot:
        for thing in budget_month:
            if thing[2]==element[2]:
                print_var.append(element + (thing[0],thing[1],))

    just = 20
    faste = ['Husleje','Fællesindkøb']
    variable =['Telefon','Forsikring','Medicin','Tøj', 'Gaver', 'Elektronik','Streaming','Uforudsete Faste','Studie','Transport']
    fun = ['Byen','Fælles Hygge', 'Musik Og Film','Sjov']
    future = ['Overskud Til Hygge','Lejlighed', 'Sydafrika', 'Emergency']

    print("")
    print("Budget for {} måned".format(month_translate[month]))
    print("To be Budgeted: {0:.2f}".format(to_be_budgeted[0][0]-to_be_budgeted[1][0]-aktier[0][0]))
    print("".ljust(4*just,'-'))
    print("Kategori".ljust(just)+"Budgetteret".ljust(just)+"Forbrug".ljust(just)+"Tilgængeligt".ljust(just))
    print("".ljust(4*just,'-'))
    for i in range(0,len(print_var)):
        for j in range(0,len(print_var[i])):
            if print_var[i][j] == None:
                lst = list(print_var[i])
                lst[j]=0
                print_var[i]=tuple(lst)
    print("")
    print("Faste Udgifter")
    print("".ljust(just*4,'-'))
    antal = 0
    for i in range(0,len(print_var)):
        if len(print_var[i])==5 and print_var[i][2] in faste:
            antal = antal+1
            faste.remove(print_var[i][2])
            print("{}".format(print_var[i][2]).ljust(just)+"{0:.2f}".format(print_var[i][4]).ljust(just)+"{0:.2f}".format(abs(print_var[i][3])).ljust(just)+"{0:.2f}".format(print_var[i][1]+print_var[i][0]).ljust(just))
    for i in range(0,len(faste)):
        print("{}".format(faste[i]).ljust(just))
    print("")
    print("Variable")
    print("".ljust(just*4,'-'))
    for i in range(0,len(print_var)):
        if len(print_var[i])==5 and print_var[i][2] in variable:
            variable.remove(print_var[i][2])
            antal = antal+1
            print("{}".format(print_var[i][2]).ljust(just)+"{0:.2f}".format(print_var[i][4]).ljust(just)+"{0:.2f}".format(abs(print_var[i][3])).ljust(just)+"{0:.2f}".format(print_var[i][1]+print_var[i][0]).ljust(just))
    for i in range(0,len(variable)):
        print("{}".format(variable[i]).ljust(just))
    print("")
    print("Sjov og Hygge")
    print("".ljust(just*4,'-'))
    for i in range(0,len(print_var)):
        if len(print_var[i])==5 and print_var[i][2] in fun:
            fun.remove(print_var[i][2])
            antal = antal+1
            print("{}".format(print_var[i][2]).ljust(just)+"{0:.2f}".format(print_var[i][4]).ljust(just)+"{0:.2f}".format(abs(print_var[i][3])).ljust(just)+"{0:.2f}".format(print_var[i][1]+print_var[i][0]).ljust(just))
    for i in range(0,len(fun)):
        print("{}".format(fun[i]).ljust(just))
    print("")
    print("Fremtid")
    print("".ljust(just*4,'-'))
    for i in range(0,len(print_var)):
        if len(print_var[i])==5 and print_var[i][2] in future:
            future.remove(print_var[i][2])
            antal = antal+1
            print("{}".format(print_var[i][2]).ljust(just)+"{0:.2f}".format(print_var[i][4]).ljust(just)+"{0:.2f}".format(abs(print_var[i][3])).ljust(just)+"{0:.2f}".format(print_var[i][1]+print_var[i][0]).ljust(just))
    for i in range(0,len(future)):
        print("{}".format(future[i]).ljust(just))
    if (antal-len(print_var))!=0:
        print("")
        print("Uden for Kategori")
        print("".ljust(just*4,'-'))
        for i in range(0,len(print_var)):
            if len(print_var[i])==5 and not (print_var[i][2] in faste or print_var[i][2] in variable or print_var[i][2] in fun or print_var[i][2] in future):
                print("{}".format(print_var[i][2]).ljust(just)+"{0:.2f}".format(print_var[i][4]).ljust(just)+"{0:.2f}".format(abs(print_var[i][3])).ljust(just)+"{0:.2f}".format(print_var[i][1]+print_var[i][0]).ljust(just))
    conn.commit()
    conn.close()

mappe = 'data'
database = 'budget'
