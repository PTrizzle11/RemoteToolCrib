# Importing libraries (tkinter for GUI, PIL for pictures, rtc_inter to communicate between back end and front end, fpdf and os for printing function)
from tkinter import *
from PIL import ImageTk, Image
from rtc_inter import *
from tkinter import messagebox
from tkinter import filedialog
from data_access import *
from email.message import EmailMessage
import ssl
import smtplib
import os
import mimetypes



# Start of the main application loop
m = Tk(className=" Remote Tool Crib ")
m.attributes('-fullscreen', True)
m.configure(bg='white')

# getdata function checks the validity of the employee number
def getdata():
    global enum
    enum = str(main_enum.get())
    valid, name, status = checkenum(enum)
    main_enum.delete(0, END)
    if valid == True:
        main_menu_func(name, status)
    else:
        try_again_label = Label(m, text='Invalid User. Try Again.', fg='red', font = ('Times', 24, 'bold'), bg='white')
        try_again_label.place(relx = 0.5, rely = 0.75, anchor=CENTER)
        try_again_label.after(2000, try_again_label.destroy)

# checkenum takes the enum as an input and returns if it is valid and the employees name if valid
def checkenum(input):
        try:
            global emp_name
            global status
            emp_name=fetch_name(int(input))
            status=fetch_title(int(input))
            return(True,emp_name, status)
        except:
            return(False, 'None','None')

# total_data gets all data gathered from the user checkout sequence. Will act as a plug-in for sending info to backend.
def total_data(user, data, name, t_name):
    tmpdata(user, data, name, t_name)



# open_locker will receive the data gathered from checkout sequence. Will act as plug-in for opening locker
def open_locker_out(data):
    print('open for check out ' + data)

# open_locker receive data gathered from return process. Will act as plug-in for opening locker
def open_locker_in(data):
    print('open for return ' + data)

# generate_total_report will be used as the plug-in for generating the entire check out report
def generate_total_report():
    sql_history = "SELECT * FROM historylog"
    sql_active = "SELECT * FROM activelog"
    df_history = DataFrame(read_sql(sql_history, conn))
    df_active = DataFrame(read_sql(sql_active, conn))

    df_combined = df_history.append(df_active, ignore_index = True)

    from datetime import date
    today = str(date.today())
    output = r"C:/Users/podonnell/Desktop/Admin Reports/"
    new_output = output+today+".xlsx"
    df_combined.to_excel(new_output,index = False, header=True)

    email_sender = 'RemoteToolCrib@gmail.com'
    email_password = 'brsakfvlbivfszcv'
    email_receiver = 'patrickjodonnell@comcast.net'

    subject = 'Remote Tool Crib Report'
    body = """
    The attached file contains the requested checkout history.
    """
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    attachment_filename = os.path.basename(new_output)
    mime_type, _ = mimetypes.guess_type(new_output)
    mime_type, mime_subtype = mime_type.split('/', 1)
    with open(new_output, 'rb') as ap:
        em.add_attachment(ap.read(), maintype=mime_type, subtype=mime_subtype,filename=os.path.basename(new_output))
    context = ssl.create_default_context()


    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

# generate_single_report will be used as the plug-in for generate the single check out report
def generate_single_report():
    sql_active = "SELECT * FROM activelog"
    df_active = DataFrame(read_sql(sql_active, conn))

    from datetime import date
    today = str(date.today())
    output = r"C:/Users/podonnell/Desktop/Employee Reports/"
    new_output = output + today + "-" + str(enum) + ".xlsx"
    df_active.to_excel(new_output, index=False, header=True)

    email_sender = 'RemoteToolCrib@gmail.com'
    email_password = 'brsakfvlbivfszcv'
    email_receiver = 'patrickjodonnell@comcast.net'

    subject = 'Remote Tool Crib Report'
    body = """
    The attached file contains the requested checkout history.
    """
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    attachment_filename = os.path.basename(new_output)
    mime_type, _ = mimetypes.guess_type(new_output)
    mime_type, mime_subtype = mime_type.split('/', 1)
    with open(new_output, 'rb') as ap:
        em.add_attachment(ap.read(), maintype=mime_type, subtype=mime_subtype,filename=os.path.basename(new_output))
    context = ssl.create_default_context()


    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

# Allows admins to open a file from their file directory
def open_file(change_tool_window, change_image_ent):
    file_location = filedialog.askopenfilename(parent=change_tool_window, initialdir=r"C:\Users\podonnell\Desktop\RTC", title="Picture Selection", filetypes=([('JPEGs','*.jpg'),('PNGs','*.png')]))
    change_image_ent.insert(0,file_location)



# Main menu function that opens a toplevel window upon successful login
def main_menu_func(name, status):

    # checkout module sequence begins
    def checkout():

        # check_availability will check the quanitity of each tool
        def check_availability(tool):
            available = 'active'
            s_ID = tool['Specific ID']
            sql_avail = "SELECT * FROM activelog"
            df_available = DataFrame(read_sql(sql_avail, conn))
            tool_ID = df_available['Tool_ID']
            for i in tool_ID.values.tolist():
                if i == s_ID:
                    available = 'disabled'
            return(available)


        # checkout confirmation page begins. Takes the desired tool and picture as inputs.
        def checkout_confirm(tools, pics):

            # c_destroy will return users to the main menu after checking out a tool
            def c_destroy():
                c_confirm.destroy()
                check_out.destroy()
                main_menu.destroy()
                messagebox.showinfo('Complete', 'Your Tools Have Been Checked Out')

            tool = tools
            global pic
            pic = pics
            c_confirm = Toplevel(check_out)
            c_confirm.attributes('-fullscreen', True)
            c_confirm.title('Checkout Confirmation')
            c_confirm.configure(bg='white')

            c_lab = Label(c_confirm, text = 'Confirm Tool Checkout', font = ('Times', 32, 'bold'), bg='white')
            c_lab.place(relx = 0.5, rely = 0.05, anchor = CENTER)

            t_name = tool['Tools']
            tool_name = Label(c_confirm, text = 'Selected Tool: ' + t_name, font = ('Times', 24, 'bold'), bg='white')
            tool_name.place(relx = 0.10, rely = 0.25, anchor = W)

            tool_p_id = Label(c_confirm, text = 'Parent ID Number: ' + tool['Parent ID'], font = ('Times', 24, 'bold'), bg='white')
            tool_p_id.place(relx = 0.10, rely = 0.35, anchor = W)

            tool_s_id = Label(c_confirm, text = 'Specific ID Number: ' + tool['Specific ID'], font = ('Times', 24, 'bold'), bg='white')
            tool_s_id.place(relx = 0.10, rely = 0.45, anchor = W)

            tool_location = Label(c_confirm, text = 'Tool Location: ' + tool['Location'], font = ('Times', 24, 'bold'), bg='white')
            tool_location.place(relx = 0.10, rely = 0.55, anchor = W)

            pic_label = Label(c_confirm, image=pic, bg='white')
            pic_label.place(relx=0.75, rely=0.425, anchor=CENTER)

            c_cancel = Button(c_confirm, text = 'Cancel', font = ('Times', 18, 'bold'), command = c_confirm.destroy, background='#9d9f9f', height = 3, width = 12)
            c_cancel.place(relx = 0.4, rely = 0.9, anchor = CENTER)

            checking_data = [tool['Specific ID'], 'Out']
            which_locker_out = tool['Location']

            c_conf = Button(c_confirm, text = 'Confirm', font = ('Times', 18, 'bold'), command = lambda: [total_data(enum, checking_data, name, t_name), open_locker_out(which_locker_out), c_destroy()], background='#9d9f9f', height = 3, width = 12)
            c_conf.place(relx = 0.6, rely = 0.9, anchor = CENTER)

            c_confirm.mainloop()

        check_out = Toplevel(main_menu)
        check_out.attributes('-fullscreen', True)
        check_out.title('Tool Checkout')
        check_out.configure(bg='white')
        sql_please = "SELECT * from tools"
        cursor.execute(sql_please)
        lab = Label(check_out, text = 'Tool Checkout', font = ('Times', 32), bg='white')
        lab.place(relx = 0.5, rely = 0.05, anchor = CENTER)
        check_q = Label(check_out, text = 'Which tool would you like to check out?', font = ('Times', 24), bg='white')
        check_q.place(relx = 0.5, rely = 0.1, anchor = CENTER)
        t1 = fetch_tool().iloc[0]
        t2 = fetch_tool().iloc[1]
        t3 = fetch_tool().iloc[2]

        global t1_img
        t1_img = Image.open(t1['Images'])
        t1_resized = t1_img.resize((300,300), Image.ANTIALIAS)
        t1_img_new = ImageTk.PhotoImage(t1_resized)
        t1_label = Label(check_out, image = t1_img_new, bg='white')
        t1_label.place(relx = 0.25, rely = 0.5, anchor = CENTER)
        t1_button = Button(check_out, text = 'Check Out ' + t1['Tools'], height = 5, width = 25, font = ('Times', 18, 'bold'), background='#9d9f9f', command = lambda: checkout_confirm(t1, t1_img_new), activebackground='#9d9f9f')
        t1_available = check_availability(t1)
        t1_button['state'] = t1_available
        t1_button.place(relx = 0.25, rely = 0.75, anchor = CENTER)

        global t2_img
        t2_img = Image.open(t2[r'Images'])
        t2_resized = t2_img.resize((300, 300), Image.ANTIALIAS)
        t2_img_new = ImageTk.PhotoImage(t2_resized)
        t2_label = Label(check_out, image=t2_img_new, bg='white')
        t2_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        t2_button = Button(check_out, text = 'Check Out ' + t2['Tools'], height = 5, width = 25, font = ('Times', 18, 'bold'), background='#9d9f9f', command = lambda: checkout_confirm(t2, t2_img_new), activebackground='#9d9f9f')
        t2_available = check_availability(t2)
        t2_button['state'] = t2_available
        t2_button.place(relx=0.5, rely=0.75, anchor=CENTER)

        global t3_img
        t3_img = Image.open(t3[r'Images'])
        t3_resized = t3_img.resize((300, 300), Image.ANTIALIAS)
        t3_img_new = ImageTk.PhotoImage(t3_resized)
        t3_label = Label(check_out, image=t3_img_new, bg='white')
        t3_label.place(relx=0.75, rely=0.5, anchor=CENTER)
        t3_button = Button(check_out, text = 'Check Out ' + t3['Tools'], height = 5, width = 25, font = ('Times', 18, 'bold'), background='#9d9f9f', command = lambda: checkout_confirm(t3, t3_img_new), activebackground='#9d9f9f')
        t3_available = check_availability(t3)
        t3_button['state'] = t3_available
        t3_button.place(relx=0.75, rely=0.75, anchor=CENTER)

        checkout_cancel_button = Button(check_out, text = 'Cancel', command = check_out.destroy, font = ('Times', 18, 'bold'), background='#9d9f9f', height = 3, width = 12)
        checkout_cancel_button.place(relx = 0.925, rely = 0.925, anchor = CENTER)

        check_out.mainloop() ##Here and up for format editsJNFJNF>NSJFNLJKFNJLSFNLJSFJN
    # user_status opens the user status menu for tool return or visuals
    def user_status():
        # return_tools is the window of confirming a tool return
        def return_tools():

            #formats the data to be sent to the total data function
            def return_data():
                sel_list=[]
                for i in ret_list.curselection():
                    sel_list.append(ret_list.get(i))
                tool_returned = sel_list[0]
                dash_index = tool_returned.rfind('-')
                tool_returned = tool_returned[dash_index+2:len(tool_returned)]
                t_name = tool_returned[0:dash_index-2]
                returning_data = [tool_returned, 'In']
                correct_index = 0
                temp_count = 0
                for i in df_tools['Specific ID']:
                    if i == tool_returned:
                        correct_index = temp_count
                    temp_count += 1
                loc_to_open = df_tools.iloc[correct_index]['Location']
                total_data(enum, returning_data, name, t_name)
                open_locker_in(loc_to_open)
                return_page.destroy()
                u_status.destroy()
                main_menu.destroy()
                messagebox.showinfo('Complete', 'Your Tools Have Been Returned')
            return_page = Toplevel(u_status)
            return_page.attributes('-fullscreen', True)
            return_page.title('Tool Return')
            return_page.configure(bg='white')
            ret_lab = Label(return_page, text = 'Which tool would you like to return?', font = ('Times', 32, 'bold'), bg='white')
            ret_lab.place(relx = 0.5, rely = 0.05, anchor = CENTER)
            ret_ins = Label(return_page, text = 'Tool Name - Tool Specific ID', font = ('Times', 24, 'bold'), bg='white')
            ret_ins.place(relx = 0.5, rely = 0.25, anchor = CENTER)
            ret_list = Listbox(return_page, font = ('Times', 18, 'bold'), height=15, width = 32)
            for i in u_list:
                t_count = 0
                t_index = 0
                l_index = 1
                for x in df_tools['Specific ID']:
                    if i == x:
                        t_index = t_count
                    t_count += 1
                ret_list.insert(l_index, df_tools['Tools'][t_index] + ' - ' + df_tools['Specific ID'][t_index])
                l_index += 1
            ret_list.place(relx = 0.5, rely = 0.475, anchor = CENTER)
            ret_conf = Button(return_page, text = 'Return', font = ('Times', 18, 'bold'), command = lambda: return_data(), height = 4, width = 16, background='#9d9f9f')
            ret_conf.place(relx = 0.5, rely = 0.75, anchor = CENTER)

            ret_canc = Button(return_page, text = 'Cancel', font = ('Times', 18, 'bold'), command = return_page.destroy, height = 4, width = 16, background='#9d9f9f')
            ret_canc.place(relx = 0.9, rely = 0.9, anchor = CENTER)

        # single_generate_report generates the report of tools checked out to a single employee
        def single_report_generator():
            generate_single_report()
            u_status.destroy()
            main_menu.destroy()
            messagebox.showinfo('Complete', 'Your report has been generated and sent to your email.')

        u_status = Toplevel(main_menu)
        u_status.attributes('-fullscreen', True)
        u_status.title('User Status')
        u_status.configure(bg='white')

        u_lab = Label(u_status, text='User Status/Tool Return', font=('Times', 32, 'bold'), bg='white')
        u_lab.place(relx=0.5, rely=0.05, anchor=CENTER)
        df_log = pd.DataFrame(pd.read_sql(sql_log, conn))
        u_list = list()
        counter = 0
        for person in df_log['User_ID']:
            if int(enum) == person:
                u_list.append(df_log['Tool_ID'].values[counter])
            counter+=1
        u_name_lab = Label(u_status, text = 'Tools Checked Out To: ' + name, font = ('Times', 24, 'bold'), bg='white')
        u_name_lab.place(relx = 0.25, rely = 0.15, anchor = CENTER)
        u_do_lab = Label(u_status, text = 'What would you like to do?', font = ('Times', 24, 'bold'), bg='white')
        u_do_lab.place(relx = 0.75, rely = 0.15, anchor = CENTER)
        initial_x = 0.25
        initial_y = 0.25
        pic_list = []
        if len(u_list) == 0:
            t_lab = Label(u_status, text='No Tools Checked Out!', font=('Times', 24, 'bold'), fg = 'red', bg='white')
            t_lab.place(relx=0.25, rely=0.2, anchor=CENTER)
        for i in u_list:
            t_count = 0
            t_index = 0

            for x in df_tools['Specific ID']:
                print(x)
                if i == x:
                    t_index = t_count
                t_count +=1
            t_lab_1 = Label(u_status, text = 'Tool: ' + df_tools['Tools'][t_index], font = ('Times', 18, 'bold'), bg='white')
            t_lab_1.place(relx = initial_x, rely = initial_y, anchor = E)

            t_lab_2 = Label(u_status, text= 'Parent ID: ' + df_tools['Parent ID'][t_index], font=('Times', 18, 'bold'), bg='white')
            t_lab_2.place(relx=initial_x, rely=initial_y + 0.05, anchor=E)

            t_lab_3 = Label(u_status, text= 'Specific ID: ' + df_tools['Specific ID'][t_index], font=('Times', 18, 'bold'), bg='white')
            t_lab_3.place(relx=initial_x, rely=initial_y + 0.1, anchor=E)

            t_lab_4 = Label(u_status, text= 'Location: ' + df_tools['Location'][t_index], font=('Times', 18, 'bold'), bg='white')
            t_lab_4.place(relx=initial_x, rely=initial_y + 0.15, anchor=E)

            t = df_tools.iloc[t_index]
            t_img = Image.open(t['Images'])
            t_resized = t_img.resize((175, 175), Image.ANTIALIAS)
            t_img_new = ImageTk.PhotoImage(t_resized)
            pic_list.append(t_img_new)
            t_label = Label(u_status, image=pic_list[-1], bg='white')
            t_label.place(relx=0.575-0.25, rely=initial_y + 0.075, anchor=CENTER)
            initial_y += 0.25

        status_cancel_button = Button(u_status, text='Exit To Main Menu', command=u_status.destroy, font=('Times', 18, 'bold'), height = 4, width = 24, background='#9d9f9f')
        status_cancel_button.place(relx=0.75, rely=0.25, anchor=CENTER)

        if len(u_list) != 0:
            return_but = Button(u_status, text='Return Items', font=('Times', 18, 'bold'), height=4, width = 24, command = return_tools, background='#9d9f9f')
            return_but.place(relx=0.75, rely=0.45, anchor=CENTER)

            print_but = Button(u_status, text='Generate Checkout Report', font=('Times', 18, 'bold'), height=4, width = 24, command = single_report_generator, background='#9d9f9f')
            print_but.place(relx=0.75, rely=0.65, anchor=CENTER)


        u_status.mainloop()
    # Block of code that sets up the admin function home page
    def admin_func():
        # total_check_out pulls all data and displays a total check out log for admins
        def total_check_out():
            generate_total_report()
            admin_screen.destroy()
            main_menu.destroy()
            messagebox.showinfo('Complete', 'Your report has been generated and sent to your email.')
        def change_tool():
            ##Will send the changes to the interface to make them occur in the database
            def gather_changes():
                new_tool = change_tool_name.get()
                new_parent = change_parent_ID.get()
                new_specific = change_specific_ID.get()
                new_location = clicked.get()
                new_stock = int(change_stock.get())
                new_image = change_image_ent.get()
                change_tool_name.delete(0,END)
                change_parent_ID.delete(0,END)
                change_specific_ID.delete(0,END)
                #change_stock.delete(0,END)
                change_image_ent.delete(0,END)
                make_changes(new_tool, new_parent, new_specific, new_location, new_stock, new_image)
                change_tool_window.destroy()
                admin_screen.destroy()
                main_menu.destroy()
                messagebox.showinfo('Complete', 'Your tool changes have been made. Insert the new tool.')
            change_tool_window = Toplevel(admin_screen)
            change_tool_window.attributes('-fullscreen', True)
            change_tool_window.title('Change Tool Request')
            change_tool_window.configure(bg='white')
            change_label1 = Label(change_tool_window, text="Tool Change Request", font=('Times', 32, 'bold'), bg='white')
            change_label1.place(relx = 0.5, rely = 0.1, anchor=CENTER)
            change_label2 = Label(change_tool_window, text='Please fill out the form below', font=('Times', 24, 'bold'), bg='white')
            change_label2.place(relx=0.5, rely=0.15, anchor=CENTER)
            change_tool_name = Entry(change_tool_window, width=40, font = ('Times', 18, 'bold'))
            change_parent_ID = Entry(change_tool_window, width=40, font = ('Times', 18, 'bold'))
            change_specific_ID = Entry(change_tool_window, width=40, font = ('Times', 18, 'bold'))
            options = ["Cabinet 1", "Cabinet 2", "Cabinet 3"]
            clicked = StringVar()
            clicked.set("Cabinet 1")
            change_location = OptionMenu(change_tool_window, clicked, *options)
            change_location.config(width = 30, font = ('Time', 18, 'bold'))
            change_stock = Entry(change_tool_window, width=40, font = ('Times', 18, 'bold'))
            change_stock.insert(0,"1")
            change_stock.config(state="disabled")
            change_image_ent = Entry(change_tool_window, width=40, font=('Times', 18, 'bold'))
            change_image = Button(change_tool_window, text="Choose File", font=('Times',18, 'bold'), background='#9f9d9d', command=lambda: open_file(change_tool_window,change_image_ent))
            change_tool_name.place(relx=0.5, rely=0.2, anchor=W)
            change_parent_ID.place(relx=0.5, rely=0.3, anchor=W)
            change_specific_ID.place(relx=0.5,rely=0.4, anchor=W)
            change_location.place(relx=0.5,rely=0.5, anchor=W)
            change_stock.place(relx=0.5,rely=0.6, anchor=W)
            change_image.place(relx=0.5,rely=0.75, anchor=CENTER)
            change_image_ent.place(relx=0.5,rely=0.7,anchor=W)
            change_tool_name_lab = Label(change_tool_window, text = 'Tool Name:', font = ('Times', 24, 'bold'), bg='white')
            change_tool_name_lab.place(relx=0.5, rely=0.2, anchor=E)
            change_parent_ID_lab = Label(change_tool_window, text='Parent ID:', font=('Times', 24, 'bold'), bg='white')
            change_parent_ID_lab.place(relx=0.5, rely=0.3, anchor=E)
            change_specific_ID_lab = Label(change_tool_window, text='Specific ID:', font=('Times', 24, 'bold'), bg='white')
            change_specific_ID_lab.place(relx=0.5, rely=0.4, anchor=E)
            change_location_lab = Label(change_tool_window, text='Location:', font=('Times', 24, 'bold'), bg='white')
            change_location_lab.place(relx=0.5, rely=0.5, anchor=E)
            change_stock_lab = Label(change_tool_window, text='Stock:', font=('Times', 24, 'bold'), bg='white')
            change_stock_lab.place(relx=0.5, rely=0.6, anchor=E)
            change_image_lab = Label(change_tool_window, text='Image:', font=('Times', 24, 'bold'), bg='white')
            change_image_lab.place(relx=0.5, rely=0.7, anchor=E)
            submit_tool = Button(change_tool_window, text='Submit', font=('Times', 18, 'bold'), background='#9f9d9d', height=4, width=15, command=gather_changes)
            cancel_tool = Button(change_tool_window, text='Cancel', font=('Times', 18, 'bold'), background='#9f9d9d', height=4, width=15, command=change_tool_window.destroy)
            submit_tool.place(relx=0.375, rely=0.85, anchor=CENTER)
            cancel_tool.place(relx=0.625, rely=0.85, anchor=CENTER)

        def lock_device():
            def locked():
                def admin_check():
                    admin_num = str(locked_entry.get())
                    valid, name, status = checkenum(admin_num)

                    if (status == 'Admin'):
                        lock_window.destroy()
                        admin_screen.destroy()
                        main_menu.destroy()
                    else:
                        invalid_label = Label(lock_window, text="Not an Admin ID", bg='white', fg='red', font=('Times',24, 'bold'))
                        invalid_label.place(relx=0.5, rely=0.9, anchor=CENTER)
                        invalid_label.after(2000, invalid_label.destroy)
                        locked_entry.delete(0, END)

                locked_lab1 = Label(lock_window, text='This device is LOCKED', bg='white', font =('Times', 32,'bold'))
                locked_lab2 = Label(lock_window, text='Scan an admin badge to unlock and logout', bg='white', font=('Times', 24, 'bold'))
                yes_but['state']=DISABLED
                no_but['state']=DISABLED
                locked_lab1.place(relx=0.5, rely=0.4, anchor=CENTER)
                locked_lab2.place(relx=0.5, rely=0.5, anchor=CENTER)
                locked_lab3 = Label(lock_window, text='Employee ID Number', font=('Times', 24, 'bold'), bg='white')
                locked_lab3.place(relx=0.5, rely=0.65, anchor=CENTER)
                locked_entry=Entry(lock_window, width=40, font = ('Times', 18, 'bold'))
                locked_entry.place(relx=0.5, rely=0.7, anchor=CENTER)
                unlock_but = Button(lock_window, text='Unlock Device', font=('Times',18,'bold'), background='#9f9d9d', height=4, width=15,command=admin_check)
                unlock_but.place(relx=0.5, rely=0.8, anchor=CENTER)
                global lock_img_new1
                lock_img1 = Image.open(r'C:\Users\podonnell\Desktop\RTC\lock.jpg')
                lock_img_res1 = lock_img1.resize((100, 100), Image.ANTIALIAS)
                lock_img_new1 = ImageTk.PhotoImage(lock_img_res1)
                lock_label1 = Label(lock_window, image=lock_img_new1, bg='white')
                lock_label1.place(relx=0.25, rely=0.4, anchor=CENTER)
                global lock_img_new2
                lock_img2 = Image.open(r'C:\Users\podonnell\Desktop\RTC\lock.jpg')
                lock_img_res2 = lock_img2.resize((100, 100), Image.ANTIALIAS)
                lock_img_new2 = ImageTk.PhotoImage(lock_img_res2)
                lock_label2 = Label(lock_window, image=lock_img_new2, bg='white')
                lock_label2.place(relx=0.75, rely=0.4, anchor=CENTER)

            lock_window = Toplevel(admin_screen)
            lock_window.attributes('-fullscreen', True)
            lock_window.title("Confirm Device Lock?")
            lock_window.configure(bg='white')
            confirm_lock = Label(lock_window,text="Are you sure you want to lock the device?",bg='white', font = ('Times', 32, 'bold'))
            confirm_lock2 = Label(lock_window,text="Only another admin will be able to unlock this device.",bg='white', font = ('Times', 24, 'bold'), fg='red')
            confirm_lock.pack()
            confirm_lock2.pack()
            yes_but = Button(lock_window, text="YES", font = ('Times', 18, 'bold'), background='#9d9f9f', height=4, width=15, command=locked)
            yes_but.place(relx=0.375, rely = 0.2, anchor=CENTER)
            no_but = Button(lock_window, text="NO", font=('Times', 18, 'bold'), background='#9d9f9f', height=4,width=15, command=lock_window.destroy)
            no_but.place(relx=0.625, rely=0.2, anchor=CENTER)
        admin_screen = Toplevel(main_menu)
        admin_screen.attributes('-fullscreen', True)
        admin_screen.title("Admin Functions")
        admin_screen.configure(bg='white')
        admin_label = Label(admin_screen, text = 'Admin Functions', bg='white', font = ('Times', 32, 'bold'))
        admin_label.place(relx=0.5, rely=0.1,anchor=CENTER)
        admin_cancel_button = Button(admin_screen, text='Cancel', command=admin_screen.destroy, font=('Times', 18, 'bold'), background='#9d9f9f', height=3, width=12)
        admin_cancel_button.place(relx = 0.925, rely = 0.925, anchor = CENTER)
        admin_main_label = Label(admin_screen, text = 'What would you like to do?', bg='white', font = ('Times', 18, 'bold'))
        admin_main_label.place(relx=0.5, rely=0.2, anchor=CENTER)
        tot_check_but = Button(admin_screen, text='Generate Checkout Report', font=('Times', 18, 'bold'), background='#9d9f9f', height=16, width=30, command = total_check_out)
        tot_check_but.place(relx = 0.20, rely = 0.5, anchor=CENTER)
        change_tool_but = Button(admin_screen, text = 'Change Tools', font=('Times', 18, 'bold'), background='#9d9f9f', height=16, width=30, command = change_tool)
        change_tool_but.place(relx = 0.5, rely = 0.5, anchor = CENTER)
        lock_device_but = Button(admin_screen, text = 'Lock Device', font = ('Times', 18, 'bold'), background = '#9d9f9f', height=16, width=30, command=lock_device)
        lock_device_but.place(relx = 0.80, rely = 0.5, anchor = CENTER)


    # Block of code associated with creating the main menu
    main_menu = Toplevel(m)
    main_menu.attributes('-fullscreen', True)
    main_menu.title("Main Menu")
    main_menu.configure(bg='white')
    sql = "SELECT * from tools"
    sql_log = "SELECT * FROM activelog"
    cursor.execute(sql)
    cursor.execute(sql_log)
    df_tools = pd.DataFrame(pd.read_sql(sql_tools, conn))
    wel_label = Label(main_menu, text = 'Welcome, ' + name+'!', fg = 'green', bg='white')
    wel_label.config(font=("Times",32, 'bold'))
    wel_label.place(relx=0.5, rely=0.1, anchor=CENTER)
    q_label = Label(main_menu, text = 'What would you like to do?', font = ('Times', 24, 'bold'), bg='white')
    q_label.place(relx = 0.5, rely = 0.15, anchor = CENTER)
    if status == 'Employee':
        check_out_button = Button(main_menu, text='Check Out Tools', width = 30, height = 15, font = ('Times', 18, 'bold'), command = checkout, background='#9d9f9f')
        user_status_button = Button(main_menu, text='View User Status/Return Tools', width=30, height=15, font=('Times', 18, 'bold'), command = user_status, background='#9d9f9f')
        log_out_button = Button(main_menu, text='Log Out', width=30, height=15, font=('Times', 18, 'bold'),command = main_menu.destroy, background='#9d9f9f')
        log_out_button.place(relx=0.8, rely=0.5, anchor=CENTER)
        user_status_button.place(relx=0.5, rely=0.5, anchor=CENTER)
        check_out_button.place(relx = 0.2, rely = 0.5, anchor = CENTER)
    else:
        check_out_button = Button(main_menu, text='Check Out Tools', width=25, height=15, font=('Times', 18, 'bold'), command=checkout, background='#9d9f9f')
        user_status_button = Button(main_menu, text='View User Status/Return Tools', width=25, height=15, font=('Times', 18, 'bold'), background='#9d9f9f', command= lambda: [user_status(), refresh_data()])
        log_out_button = Button(main_menu, text='Log Out', width=25, height=15, font=('Times', 18, 'bold'), command=main_menu.destroy, background='#9d9f9f')
        admin_screen_button = Button(main_menu, text='Admin Tools', width = 25, height=15, font=('Times', 18, 'bold'), command=admin_func, background='#9d9f9f')
        log_out_button.place(relx=0.875, rely=0.5, anchor=CENTER)
        user_status_button.place(relx=0.625, rely=0.5, anchor=CENTER)
        check_out_button.place(relx=0.375, rely=0.5, anchor=CENTER)
        admin_screen_button.place(relx = 0.125, rely = 0.5, anchor=CENTER)

    main_menu.mainloop()

# Block of code associated with creating login screen
main_enum_label = Label(m, text = 'Employee ID Number', width = 20, bg='white')
main_enum_label.config(font=('Times',32, 'bold'))
main_enum_label.place(relx=0.5, rely=0.45, anchor = CENTER)
main_enum = Entry(m, width=40, font = ('Times', 18, 'bold'))
main_enum.place(relx=0.5, rely=0.5, anchor = CENTER)
main_cont = Button(m, text = 'Continue', width=15, height=5, command = getdata, font=('Times', 18, 'bold'), background='#9d9f9f')
main_cont.place(relx=0.5, rely=0.6, anchor = CENTER)

m.mainloop()