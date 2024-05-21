import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox
import sms_app_logic as logic
import requests

class Page1:
    def __init__(self, parent):
        self.parent = parent
        self.logic = logic.SMSAppLogic()
        self.selected_group_indices = []

        self.create_widgets()

    def create_widgets(self):
        self.groups_label = tk.Label(self.parent, text="Groups:")
        self.groups_label.place(x=20, y=20)

        self.groups_listbox = tk.Listbox(self.parent, width=30, height=10, selectmode=tk.MULTIPLE)
        self.groups_listbox.place(x=20, y=50, width=120)

        self.refresh_groups()

        self.groups_listbox.bind("<<ListboxSelect>>", self.on_group_select)

        self.recipients_label = tk.Label(self.parent, text="Recipients:")
        self.recipients_label.place(x=350, y=20)

        self.recipients_listbox = tk.Listbox(self.parent, width=30, height=10, selectmode=tk.EXTENDED)
        self.recipients_listbox.place(x=350, y=50)

        # Read-only recipients listbox
        self.readonly_recipients_label = tk.Label(self.parent, text="All Recipients in Selected Groups:")
        self.readonly_recipients_label.place(x=150, y=20)

        self.readonly_recipients_listbox = tk.Listbox(self.parent, width=30, height=10, selectmode=tk.SINGLE)
        self.readonly_recipients_listbox.place(x=150, y=50)
        self.readonly_recipients_listbox.configure(state=tk.DISABLED)

        self.text_entry_label = tk.Label(self.parent, text="Text of the SMS:")
        self.text_entry_label.place(x=20, y=265, width=500)

        # Text entry field
        self.text_entry = tk.Text(self.parent, wrap='word', width=50, height=10)
        self.text_entry.place(x=20, y=285, width=490, height=100)
        
        # Add a scrollbar to the text entry field
        self.text_scrollbar = tk.Scrollbar(self.parent, command=self.text_entry.yview)
        self.text_scrollbar.place(x=520, y=285, height=100)
        self.text_entry.config(yscrollcommand=self.text_scrollbar.set)

        # Send SMS button
        self.send_sms_button = tk.Button(self.parent, text="Send SMS", command=self.on_send_sms, bg="#32CD32")
        self.send_sms_button.place(x=350, y=225, width=185)
        
        # Send SMS to Group button
        self.send_sms_group_button = tk.Button(self.parent, text="Send SMS to Group", command=self.on_send_sms_to_group, bg="#32CD32")
        self.send_sms_group_button.place(x=150, y=225, width=185)

    def refresh_groups(self):
        self.groups_listbox.delete(0, tk.END)
        groups = self.logic.get_groups()
        for group in groups:
            self.groups_listbox.insert(tk.END, group[1])

    def on_group_select(self, event=None):
        self.selected_group_indices = self.groups_listbox.curselection()
        if self.selected_group_indices:
            self.refresh_recipients()
            self.refresh_all_recipients_in_groups()

    def refresh_recipients(self, event=None):
        self.recipients_listbox.delete(0, tk.END)
        if self.selected_group_indices:
            last_selected_group_index = self.selected_group_indices[-1]
            group_name = self.groups_listbox.get(last_selected_group_index)
            group_id = self.logic.get_group_id(group_name)
            if group_id:
                self.recipients_label.config(text=f"Recipients from Group {group_name}")
                recipients = self.logic.get_recipients_in_group(group_id)
                for recipient in recipients:
                    self.recipients_listbox.insert(tk.END, f"{recipient[1]}: {recipient[2]}")

    def refresh_all_recipients_in_groups(self):
        self.readonly_recipients_listbox.configure(state=tk.NORMAL)
        self.readonly_recipients_listbox.delete(0, tk.END)
        if self.selected_group_indices:
            all_recipients = set()
            for group_index in self.selected_group_indices:
                group_name = self.groups_listbox.get(group_index)
                group_id = self.logic.get_group_id(group_name)
                if group_id:
                    recipients = self.logic.get_recipients_in_group(group_id)
                    for recipient in recipients:
                        all_recipients.add((recipient[1], recipient[2]))

            for recipient in all_recipients:
                self.readonly_recipients_listbox.insert(tk.END, f"{recipient[0]}: {recipient[1]}")

        self.readonly_recipients_listbox.configure(state=tk.DISABLED)

    def on_send_sms(self):
        selected_recipients = self.recipients_listbox.curselection()
        if not selected_recipients:
            messagebox.showwarning("Warning", "Please select at least one recipient.")
            return
        
        message = self.text_entry.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message.")
            return

        for recipient_index in selected_recipients:
            recipient = self.recipients_listbox.get(recipient_index)
            name, phone_number = recipient.split(": ")
            self.send_sms(message, phone_number.strip())

    def on_send_sms_to_group(self):
        if not self.selected_group_indices:
            messagebox.showwarning("Warning", "Please select at least one group.")
            return
        
        message = self.text_entry.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message.")
            return

        all_recipients = set()
        for group_index in self.selected_group_indices:
            group_name = self.groups_listbox.get(group_index)
            group_id = self.logic.get_group_id(group_name)
            if group_id:
                recipients = self.logic.get_recipients_in_group(group_id)
                for recipient in recipients:
                    all_recipients.add(recipient[2])  # recipient[2] is the phone number

        for phone_number in all_recipients:
            self.send_sms(message, phone_number)

    def send_sms(self, message, number):
        url = "https://im.smsclub.mobi/sms/send"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer EUybGg2oqejS6Fk"  # Замініть your_token на ваш токен
        }
        payload = {
            "phone": [str(number)],
            "message": message,
            "src_addr": "TAXI"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if "success_request" in result:
                    info = result["success_request"]["info"]
                    messagebox.showinfo("API Response", f"Message was successfully sent to {number}.")
                else:
                    messagebox.showerror("API Error", "Error sending message.")
            else:
                messagebox.showerror("API Error", f"Error sending message. Status code: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


class Page2:
    def __init__(self, parent):
        self.parent = parent
        self.logic = logic.SMSAppLogic()

        self.create_widgets()

    def create_widgets(self):
        self.groups_label = tk.Label(self.parent, text="Groups:")
        self.groups_label.pack()

        self.groups_listbox = tk.Listbox(self.parent, width=30, height=10, selectmode=tk.SINGLE)
        self.groups_listbox.pack(pady=(0,10))

        self.refresh_groups()

        self.add_group_button = ttk.Button(self.parent, text="Add Group", command=self.add_group)
        self.add_group_button.pack()

        self.edit_group_button = ttk.Button(self.parent, text="Edit Group", command=self.edit_group)
        self.edit_group_button.pack()

        self.delete_group_button = ttk.Button(self.parent, text="Delete Group", command=self.delete_group)
        self.delete_group_button.pack()

    def refresh_groups(self):
        self.groups_listbox.delete(0, tk.END)
        groups = self.logic.get_groups()
        for group in groups:
            self.groups_listbox.insert(tk.END, group[1])

    def add_group(self):
        group_name = simpledialog.askstring("Add Group", "Enter group name:")
        if group_name:
            self.logic.add_group(group_name)
            self.refresh_groups()

    def edit_group(self):
        selected_index = self.groups_listbox.curselection()
        if selected_index:
            group_name = self.groups_listbox.get(selected_index[0])
            new_name = simpledialog.askstring("Edit Group", "Enter new group name:", initialvalue=group_name)
            if new_name:
                self.logic.edit_group(selected_index[0]+1, new_name)
                self.refresh_groups()

    def delete_group(self):
        selected_index = self.groups_listbox.curselection()
        if selected_index:
            confirmation = messagebox.askyesno("Delete Group", "Are you sure you want to delete this group?")
            if confirmation:
                self.logic.delete_group(selected_index[0]+1)
                self.refresh_groups()

class Page3:
    def __init__(self, parent):
        self.parent = parent
        self.logic = logic.SMSAppLogic()

        self.create_widgets()

    def create_widgets(self):
        self.recipients_label = tk.Label(self.parent, text="Recipients:")
        self.recipients_label.pack()

        self.recipients_listbox = tk.Listbox(self.parent, width=30, height=10, selectmode=tk.SINGLE)
        self.recipients_listbox.pack(pady=(0,10))

        self.refresh_recipients()

        self.add_recipient_button = ttk.Button(self.parent, text="Add Recipient", command=self.add_recipient)
        self.add_recipient_button.pack()

        self.edit_recipient_button = ttk.Button(self.parent, text="Edit Recipient", command=self.edit_recipient)
        self.edit_recipient_button.pack()

        self.delete_recipient_button = ttk.Button(self.parent, text="Delete Recipient", command=self.delete_recipient)
        self.delete_recipient_button.pack()

        self.add_to_group_button = ttk.Button(self.parent, text="Add to Group", command=self.add_to_group)
        self.add_to_group_button.pack()

        self.remove_from_group_button = ttk.Button(self.parent, text="Remove from Group", command=self.remove_from_group)
        self.remove_from_group_button.pack()

    def refresh_recipients(self):
        self.recipients_listbox.delete(0, tk.END)
        recipients = self.logic.get_recipients()
        for recipient in recipients:
            self.recipients_listbox.insert(tk.END, f"{recipient[1]}: {recipient[2]}")

    def add_recipient(self):
        recipient_name = simpledialog.askstring("Add Recipient", "Enter recipient name:")
        if recipient_name:
            recipient_phone = simpledialog.askstring("Add Recipient", "Enter recipient phone number:")
            if recipient_phone:
                self.logic.add_recipient(recipient_name, recipient_phone)
                self.refresh_recipients()

    def edit_recipient(self):
        selected_index = self.recipients_listbox.curselection()
        if selected_index:
            recipient_name, recipient_phone = self.recipients_listbox.get(selected_index[0]).split(":")
            recipient_name = recipient_name.strip()
            recipient_phone = recipient_phone.strip()
            new_name = simpledialog.askstring("Edit Recipient", "Enter new recipient name:", initialvalue=recipient_name)
            if new_name:
                new_phone = simpledialog.askstring("Edit Recipient", "Enter new recipient phone number:", initialvalue=recipient_phone)
                if new_phone:
                    self.logic.edit_recipient(recipient_name, recipient_phone, new_name, new_phone)
                    self.refresh_recipients()

    def delete_recipient(self):
        selected_index = self.recipients_listbox.curselection()
        if selected_index:
            confirmation = messagebox.askyesno("Delete Recipient", "Are you sure you want to delete this recipient?")
            if confirmation:
                recipient_name, recipient_phone = self.recipients_listbox.get(selected_index[0]).split(":")
                recipient_name = recipient_name.strip()
                recipient_phone = recipient_phone.strip()
                self.logic.delete_recipient(recipient_name, recipient_phone)
                self.refresh_recipients()

    def add_to_group(self):
        selected_index = self.recipients_listbox.curselection()
        if selected_index:
            recipient_name, recipient_phone = self.recipients_listbox.get(selected_index[0]).split(":")
            recipient_name = recipient_name.strip()
            recipient_phone = recipient_phone.strip()
            AddToGroupWindow(self.parent, recipient_name, recipient_phone, self.logic)

    def remove_from_group(self):
        selected_index = self.recipients_listbox.curselection()
        if selected_index:
            recipient_name, recipient_phone = self.recipients_listbox.get(selected_index[0]).split(":")
            recipient_name = recipient_name.strip()
            recipient_phone = recipient_phone.strip()
            RemoveFromGroupWindow(self.parent, recipient_name, recipient_phone, self.logic)

class Page4:
    def __init__(self, parent):
        self.parent = parent
        self.logic = logic.SMSAppLogic()
        self.selected_group_index = None

        self.create_widgets()

    def create_widgets(self):
        self.groups_label = tk.Label(self.parent, text="Groups:")
        self.groups_label.pack()

        self.groups_listbox = tk.Listbox(self.parent, width=30, height=10, selectmode=tk.SINGLE)
        self.groups_listbox.pack(pady=(0, 10))

        self.refresh_groups()

        self.groups_listbox.bind("<<ListboxSelect>>", self.on_group_select)

        self.recipients_label = tk.Label(self.parent, text="Recipients:")
        self.recipients_label.pack()

        self.recipients_listbox = tk.Listbox(self.parent, width=30, height=10, selectmode=tk.SINGLE)
        self.recipients_listbox.pack(pady=(0, 10))

        self.add_to_group_button = ttk.Button(self.parent, text="Add to Group", command=self.open_add_to_group_dialog)
        self.add_to_group_button.pack()

        self.remove_from_group_button = ttk.Button(self.parent, text="Remove from Group", command=self.remove_from_group)
        self.remove_from_group_button.pack()

    def refresh_groups(self):
        self.groups_listbox.delete(0, tk.END)
        groups = self.logic.get_groups()
        for group in groups:
            self.groups_listbox.insert(tk.END, group[1])

    def on_group_select(self, event=None):
        selected_group_index = self.groups_listbox.curselection()
        if selected_group_index:
            self.selected_group_index = selected_group_index[0]
            self.refresh_recipients()

    def refresh_recipients(self, event=None):
        if self.selected_group_index is not None:
            group_name = self.groups_listbox.get(self.selected_group_index)
            group_id = self.logic.get_group_id(group_name)
            if group_id:
                self.recipients_listbox.delete(0, tk.END)
                recipients = self.logic.get_recipients_in_group(group_id)
                for recipient in recipients:
                    self.recipients_listbox.insert(tk.END, f"{recipient[1]}: {recipient[2]}")

    def open_add_to_group_dialog(self):
        if self.selected_group_index is not None:
            group_name = self.groups_listbox.get(self.selected_group_index)
            group_id = self.logic.get_group_id(group_name)
            if group_id:
                AddToGroupDialog(self.parent, group_id, self.logic, self.refresh_recipients)

    def remove_from_group(self):
        selected_recipient_index = self.recipients_listbox.curselection()
        if self.selected_group_index is not None and selected_recipient_index:
            group_name = self.groups_listbox.get(self.selected_group_index)
            group_id = self.logic.get_group_id(group_name)
            recipient_data = self.recipients_listbox.get(selected_recipient_index[0])
            recipient_name, recipient_phone = recipient_data.split(":")
            recipient_name = recipient_name.strip()
            recipient_phone = recipient_phone.strip()
            recipient_id = self.logic.get_recipient_id(recipient_name, recipient_phone)
            if group_id and recipient_id:
                self.logic.remove_recipient_from_group(recipient_id, group_id)
                self.refresh_recipients()

class AddToGroupDialog:
    def __init__(self, parent, group_id, logic, refresh_callback):
        self.group_id = group_id
        self.logic = logic
        self.refresh_callback = refresh_callback

        self.window = tk.Toplevel(parent)
        self.window.title("Add Recipients to Group")

        self.recipients_listbox = tk.Listbox(self.window, width=30, height=10, selectmode=tk.MULTIPLE)
        self.recipients_listbox.pack(pady=(0, 10))

        self.refresh_recipients()

        self.add_button = ttk.Button(self.window, text="Add", command=self.add_recipients_to_group)
        self.add_button.pack()

    def refresh_recipients(self):
        self.recipients_listbox.delete(0, tk.END)
        recipients = self.logic.get_recipients()
        group_recipients = self.logic.get_recipients_in_group(self.group_id)
        group_recipient_ids = {rec[0] for rec in group_recipients}
        for recipient in recipients:
            if recipient[0] not in group_recipient_ids:
                self.recipients_listbox.insert(tk.END, f"{recipient[1]}: {recipient[2]}")

    def add_recipients_to_group(self):
        selected_indices = self.recipients_listbox.curselection()
        for index in selected_indices:
            recipient_data = self.recipients_listbox.get(index)
            recipient_name, recipient_phone = recipient_data.split(":")
            recipient_name = recipient_name.strip()
            recipient_phone = recipient_phone.strip()
            recipient_id = self.logic.get_recipient_id(recipient_name, recipient_phone)
            if recipient_id:
                self.logic.add_recipient_to_group(recipient_id, self.group_id)
        self.refresh_callback()
        self.window.destroy()

class AddToGroupDialog:
    def __init__(self, parent, group_id, logic, refresh_callback):
        self.group_id = group_id
        self.logic = logic
        self.refresh_callback = refresh_callback

        self.window = tk.Toplevel(parent)
        self.window.title("Add Recipients to Group")

        self.recipients_listbox = tk.Listbox(self.window, width=30, height=10, selectmode=tk.MULTIPLE)
        self.recipients_listbox.pack(pady=(0, 10))

        self.refresh_recipients()

        self.add_button = ttk.Button(self.window, text="Add", command=self.add_recipients_to_group)
        self.add_button.pack()

    def refresh_recipients(self):
        self.recipients_listbox.delete(0, tk.END)
        recipients = self.logic.get_recipients()
        group_recipients = self.logic.get_recipients_in_group(self.group_id)
        group_recipient_ids = {rec[0] for rec in group_recipients}
        for recipient in recipients:
            if recipient[0] not in group_recipient_ids:
                self.recipients_listbox.insert(tk.END, f"{recipient[1]}: {recipient[2]}")

    def add_recipients_to_group(self):
        selected_indices = self.recipients_listbox.curselection()
        for index in selected_indices:
            recipient_data = self.recipients_listbox.get(index)
            recipient_name, recipient_phone = recipient_data.split(":")
            recipient_name = recipient_name.strip()
            recipient_phone = recipient_phone.strip()
            recipient_id = self.logic.get_recipient_id(recipient_name, recipient_phone)
            if recipient_id:
                self.logic.add_recipient_to_group(recipient_id, self.group_id)
        self.refresh_callback()
        self.window.destroy()

class EditDependenciesWindow:
    def __init__(self, parent, recipient_name, recipient_phone, logic):
        self.parent = parent
        self.recipient_name = recipient_name
        self.recipient_phone = recipient_phone
        self.logic = logic

        self.window = tk.Toplevel(parent)
        self.window.title("Edit Dependencies")

        self.create_widgets()

    def create_widgets(self):
        self.groups_label = tk.Label(self.window, text="Groups:")
        self.groups_label.pack()

        self.groups_listbox = tk.Listbox(self.window, width=30, height=5, selectmode=tk.MULTIPLE)
        self.groups_listbox.pack()

        self.refresh_groups()

        self.add_to_group_button = ttk.Button(self.window, text="Add to Group", command=self.add_to_group)
        self.add_to_group_button.pack()

        self.remove_from_group_button = ttk.Button(self.window, text="Remove from Group", command=self.remove_from_group)
        self.remove_from_group_button.pack()

    def refresh_groups(self):
        self.groups_listbox.delete(0, tk.END)
        groups = self.logic.get_groups()
        recipient_id = self.logic.get_recipient_id(self.recipient_name, self.recipient_phone)
        if recipient_id:
            recipient_groups = self.logic.get_recipient_groups(recipient_id)
            for group in groups:
                if group[1] in recipient_groups:
                    self.groups_listbox.insert(tk.END, group[1])

    def add_to_group(self):
        selected_indices = self.groups_listbox.curselection()
        if selected_indices:
            selected_groups = [self.groups_listbox.get(index) for index in selected_indices]
            recipient_id = self.logic.get_recipient_id(self.recipient_name, self.recipient_phone)
            for group_name in selected_groups:
                group_id = self.logic.get_group_id(group_name)
                if group_id and recipient_id:
                    self.logic.add_recipient_to_group(recipient_id, group_id)
            self.refresh_groups()

    def remove_from_group(self):
        selected_indices = self.groups_listbox.curselection()
        if selected_indices:
            selected_groups = [self.groups_listbox.get(index) for index in selected_indices]
            recipient_id = self.logic.get_recipient_id(self.recipient_name, self.recipient_phone)
            for group_name in selected_groups:
                group_id = self.logic.get_group_id(group_name)
                if group_id and recipient_id:
                    self.logic.remove_recipient_from_group(recipient_id, group_id)
            self.refresh_groups()

class AddToGroupWindow:
    def __init__(self, parent, recipient_name, recipient_phone, logic):
        self.parent = parent
        self.recipient_name = recipient_name
        self.recipient_phone = recipient_phone
        self.logic = logic

        self.window = tk.Toplevel(parent)
        self.window.title("Add to Group")

        self.create_widgets()

    def create_widgets(self):
        self.groups_label = tk.Label(self.window, text="Groups:")
        self.groups_label.pack()

        self.groups_listbox = tk.Listbox(self.window, width=30, height=5, selectmode=tk.SINGLE)
        self.groups_listbox.pack()

        self.refresh_groups()

        self.add_to_group_button = ttk.Button(self.window, text="Add to Group", command=self.add_to_group)
        self.add_to_group_button.pack()

    def refresh_groups(self):
        self.groups_listbox.delete(0, tk.END)
        groups = self.logic.get_groups()
        for group in groups:
            self.groups_listbox.insert(tk.END, group[1])

    def add_to_group(self):
        selected_index = self.groups_listbox.curselection()
        if selected_index:
            group_name = self.groups_listbox.get(selected_index[0])
            group_id = self.logic.get_group_id(group_name)
            recipient_id = self.logic.get_recipient_id(self.recipient_name, self.recipient_phone)
            if group_id and recipient_id:
                self.logic.add_recipient_to_group(recipient_id, group_id)
                self.window.destroy()

class RemoveFromGroupWindow:
    def __init__(self, parent, recipient_name, recipient_phone, logic):
        self.parent = parent
        self.recipient_name = recipient_name
        self.recipient_phone = recipient_phone
        self.logic = logic

        self.window = tk.Toplevel(parent)
        self.window.title("Remove from Group")

        self.create_widgets()

    def create_widgets(self):
        self.groups_label = tk.Label(self.window, text="Groups:")
        self.groups_label.pack()

        self.groups_listbox = tk.Listbox(self.window, width=30, height=5, selectmode=tk.SINGLE)
        self.groups_listbox.pack()

        self.refresh_groups()

        self.remove_from_group_button = ttk.Button(self.window, text="Remove from Group", command=self.remove_from_group)
        self.remove_from_group_button.pack()

    def refresh_groups(self):
        self.groups_listbox.delete(0, tk.END)
        groups = self.logic.get_groups()
        recipient_id = self.logic.get_recipient_id(self.recipient_name, self.recipient_phone)
        if recipient_id:
            recipient_groups = self.logic.get_recipient_groups(recipient_id)
            for group in groups:
                if group[1] in recipient_groups:
                    self.groups_listbox.insert(tk.END, group[1])

    def remove_from_group(self):
        selected_index = self.groups_listbox.curselection()
        if selected_index:
            group_name = self.groups_listbox.get(selected_index[0])
            group_id = self.logic.get_group_id(group_name)
            recipient_id = self.logic.get_recipient_id(self.recipient_name, self.recipient_phone)
            if group_id and recipient_id:
                self.logic.remove_recipient_from_group(recipient_id, group_id)
                self.window.destroy()