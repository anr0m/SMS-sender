import sqlite3

class SMSAppLogic:
    def __init__(self):
        self.connection = sqlite3.connect("sms_app.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS recipients (
                                id INTEGER PRIMARY KEY,
                                name TEXT NOT NULL,
                                phone_number TEXT NOT NULL
                                )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
                                id INTEGER PRIMARY KEY,
                                name TEXT NOT NULL
                                )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS recipient_groups (
                                recipient_id INTEGER,
                                group_id INTEGER,
                                FOREIGN KEY (recipient_id) REFERENCES recipients(id),
                                FOREIGN KEY (group_id) REFERENCES groups(id)
                                )''')
        self.connection.commit()



    def add_recipient(self, name, phone_number):
        self.cursor.execute("INSERT INTO recipients (name, phone_number) VALUES (?, ?)",
                            (name, phone_number))
        self.connection.commit()

    def add_group(self, name):
        self.cursor.execute("INSERT INTO groups (name) VALUES (?)", (name,))
        self.connection.commit()

    def get_groups(self):
        self.cursor.execute("SELECT * FROM groups")
        return self.cursor.fetchall()

    def get_group_id(self, group_name):
        self.cursor.execute("SELECT id FROM groups WHERE name=?", (group_name,))
        group_id = self.cursor.fetchone()
        return group_id[0] if group_id else None

    def edit_group(self, group_id, new_name):
        self.cursor.execute("UPDATE groups SET name=? WHERE id=?", (new_name, group_id))
        self.connection.commit()

    def delete_group(self, group_id):
        self.cursor.execute("DELETE FROM groups WHERE id=?", (group_id,))
        self.connection.commit()

    def get_recipients(self):
        self.cursor.execute("SELECT * FROM recipients")
        return self.cursor.fetchall()

    def edit_recipient(self, old_name, old_phone, new_name, new_phone):
        self.cursor.execute("UPDATE recipients SET name=?, phone_number=? WHERE name=? AND phone_number=?",
                            (new_name, new_phone, old_name, old_phone))
        self.connection.commit()

    def delete_recipient(self, name, phone_number):
        self.cursor.execute("DELETE FROM recipients WHERE name=? AND phone_number=?", (name, phone_number))
        self.connection.commit()

    def get_recipient_id(self, name, phone_number):
        self.cursor.execute("SELECT id FROM recipients WHERE name=? AND phone_number=?", (name, phone_number))
        recipient_id = self.cursor.fetchone()
        return recipient_id[0] if recipient_id else None

    def add_recipient_to_group(self, recipient_id, group_id):
        self.cursor.execute("INSERT INTO recipient_groups (recipient_id, group_id) VALUES (?, ?)",
                            (recipient_id, group_id))
        self.connection.commit()

    def remove_recipient_from_group(self, recipient_id, group_id):
        self.cursor.execute("DELETE FROM recipient_groups WHERE recipient_id=? AND group_id=?",
                            (recipient_id, group_id))
        self.connection.commit()

    def close(self):
        self.connection.close()

    def get_recipient_groups(self, recipient_id):
        self.cursor.execute("SELECT group_id FROM recipient_groups WHERE recipient_id=?", (recipient_id,))
        group_ids = self.cursor.fetchall()
        group_names = []
        for group_id in group_ids:
            group_name = self.get_group_name(group_id[0])
            if group_name:
                group_names.append(group_name)
        return group_names
    
    def get_group_name(self, group_id):
        self.cursor.execute("SELECT name FROM groups WHERE id=?", (group_id,))
        group_name = self.cursor.fetchone()
        return group_name[0] if group_name else None

    def get_recipients_in_group(self, group_id):
        self.cursor.execute('''SELECT r.id, r.name, r.phone_number
                               FROM recipients AS r
                               JOIN recipient_groups AS rg
                               ON r.id = rg.recipient_id
                               WHERE rg.group_id = ?''', (group_id,))
        return self.cursor.fetchall()

    def get_recipients_in_group(self, group_id):
        self.cursor.execute('''
            SELECT recipients.id, recipients.name, recipients.phone_number 
            FROM recipients 
            JOIN recipient_groups ON recipients.id = recipient_groups.recipient_id 
            WHERE recipient_groups.group_id = ?
        ''', (group_id,))
        return self.cursor.fetchall()
