# %%
import warnings

import pyodbc
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\Users\\podonnell\\Desktop\\RTC\\database_revisions\\sdDatabase_rev1.accdb;')
cursor = conn.cursor()
   
sql_users = "SELECT * FROM users"
df_users = pd.read_sql(sql_users, conn)
sql_tools= "SELECT * FROM tools"
df_tools = pd.DataFrame(pd.read_sql(sql_tools, conn))



def refresh_data():
    sql_log = "SELECT * FROM activelog"
    df_log = pd.DataFrame(pd.read_sql(sql_log, conn))
def fetch_name(id):
    df2=df_users.query('Employee_ID == @id')['Employee_Name'].values[0]
    return df2

def fetch_title(id):
    df2=df_users.query('Employee_ID == @id')['Employee_Title'].values[0]
    return df2

def fetch_tool():
    sql_tools = "SELECT * FROM tools"
    df_tools = pd.DataFrame(pd.read_sql(sql_tools, conn))
    df2=df_tools
    df2['Tools'] = df2['Tools'].replace([df2.iloc[0]['Tools']], str(df2.iloc[0]['Tools']))
    df2['Tools'] = df2['Tools'].replace([df2.iloc[1]['Tools']], str(df2.iloc[1]['Tools']))
    df2['Tools'] = df2['Tools'].replace([df2.iloc[2]['Tools']], str(df2.iloc[2]['Tools']))

    df2['Parent ID'] = df2['Parent ID'].replace([df2.iloc[0]['Parent ID']], str(df2.iloc[0]['Parent ID']))
    df2['Parent ID'] = df2['Parent ID'].replace([df2.iloc[1]['Parent ID']], str(df2.iloc[1]['Parent ID']))
    df2['Parent ID'] = df2['Parent ID'].replace([df2.iloc[2]['Parent ID']], str(df2.iloc[2]['Parent ID']))

    df2['Specific ID'] = df2['Specific ID'].replace([df2.iloc[0]['Specific ID']], str(df2.iloc[0]['Specific ID']))
    df2['Specific ID'] = df2['Specific ID'].replace([df2.iloc[1]['Specific ID']], str(df2.iloc[1]['Specific ID']))
    df2['Specific ID'] = df2['Specific ID'].replace([df2.iloc[2]['Specific ID']], str(df2.iloc[2]['Specific ID']))

    df2['Location'] = df2['Location'].replace([df2.iloc[0]['Location']], str(df2.iloc[0]['Location']))
    df2['Location'] = df2['Location'].replace([df2.iloc[1]['Location']], str(df2.iloc[1]['Location']))
    df2['Location'] = df2['Location'].replace([df2.iloc[2]['Location']], str(df2.iloc[2]['Location']))

    df2['Images'] = df2['Images'].replace([df2.iloc[0]['Images']], str(df2.iloc[0]['Images']))
    df2['Images'] = df2['Images'].replace([df2.iloc[1]['Images']], str(df2.iloc[1]['Images']))
    df2['Images'] = df2['Images'].replace([df2.iloc[2]['Images']], str(df2.iloc[2]['Images']))
    return df2

def tmpdata(user, data, name, t_name):
    from datetime import datetime

    name = name
    tool_id = data[0]
    t_name = t_name
    if data[1] == 'Out':
        sql = "INSERT INTO activelog (User_ID, User_Name, Tool_ID, Tool_Name,Time_OUT, Time_IN) VALUES (?,?,?,?,?,?)"
        Time_OUT = str(datetime.now())
        Time_IN = None
        cursor.execute(sql, [user, name, tool_id, t_name, Time_OUT, Time_IN])
        print(data)

    elif data[1] == 'In':
        Time_IN = str(datetime.now())

        sql1 = "INSERT INTO historylog (User_ID, User_Name, Tool_ID, Tool_Name, Time_OUT, Time_IN, Trans_ID) SELECT User_ID, User_Name, Tool_ID, Tool_Name, Time_OUT, Time_IN, Trans_ID FROM activelog WHERE Tool_ID = '%s'"%tool_id
        sql = "UPDATE activelog set TIME_IN = '%s' WHERE Tool_ID = '%s'" %(Time_IN, tool_id)
        sql2 = "DELETE FROM activelog WHERE Tool_ID = '%s'" % (tool_id)
        cursor.execute(sql)
        cursor.execute(sql1)
        cursor.execute(sql2)
    conn.commit()

    # Will act as a plug in for changing a tool
def make_changes(new_tool, new_parent, new_specific, new_location, new_stock, new_image):
    #sql_new2 = "DELETE FROM tools WHERE Location = '%s'" % (new_location)
    #sql_new = "INSERT INTO tools (Tools, [Parent ID], [Specific ID],Location, Stock, Images) VALUES (?,?,?,?,?,?)"
    sql_new = "UPDATE tools SET Tools = '%s', `Parent ID` = '%s', `Specific ID` = '%s', Stock = '%s', Images = '%s' WHERE Location = '%s'" % (new_tool, new_parent, new_specific, new_stock, new_image, new_location)
    #sql_new = "UPDATE tools SET Tools = '$new_tool', `Parent ID` = '$new_parent', `Specific ID` = '$new_specific', Stock = '$new_stock', Images = '$new_image' WHERE Location = '$new_location'"

    #cursor.execute(sql_new, [new_tool, new_parent, new_specific, new_location, new_stock, new_image])
    #cursor.execute(sql_new2)
    cursor.execute(sql_new)


    conn.commit()










