import sqlite3
from src.config import TelegramBot


class Storage:

    def __init__(self, path, db_name):
        self.path = path
        self.connection = sqlite3.connect(f"{self.path}{db_name}")
        self.cursor = self.connection.cursor()

    def create_table(self):
        with self.connection:
            return self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id integer primary key,
            username text,
            name text,
            age integer,
            gender text,
            desc text,
            photo blob,
            partner text
            )""")

    def create_matching_table(self):
        with self.connection:
            return self.cursor.execute("""CREATE TABLE IF NOT EXISTS matching (
            id integer primary key,
            initiator_id integer,
            interes_id integer,
            like_initiator bool,
            like_interes bool,
            foreign key(initiator_id) references users(id),
            foreign key(interes_id) references users(id),
            unique (initiator_id, interes_id)
            )""")

    def add_users_info(self, id, username, name, age, gender, desc, photo, partner):
        with self.connection:
            return self.cursor.execute("""INSERT INTO users (id, username, name, age, gender, desc, photo, partner)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
                id, username, name, age, gender, desc, photo, partner))

    def check_users_existence(self, user_id: int) -> bool:
        with self.connection:
            return bool(self.cursor.execute("""SELECT id FROM users WHERE id = ?""", (user_id,)).fetchone())

    def printout_users_form(self, id: int):
        with self.connection:
            info = self.cursor.execute("""SELECT * FROM users WHERE id = ?""", (id, )).fetchall()
            return info

    def get_users(self, id_user: int):
        with self.connection:
            return self.cursor.execute("""SELECT * FROM users WHERE id = ?""", (id_user, )).fetchone()

    def get_users_age_gender_partner(self, id_user: int):
        with self.connection:
            return self.cursor.execute("""SELECT age, gender, partner FROM users WHERE id = ?""", (id_user, )).fetchone()

    def create_new_matchings(self, user_id, age, gender, partner):
        with self.connection:
            if partner != "Без разницы":
                partners = self.cursor.execute(
                    """SELECT id FROM users WHERE abs(age - ?) <= 2 and gender == ? and partner == ? and id != ? EXCEPT
                    SELECT initiator_id FROM matching""", (age, partner, gender, user_id)).fetchall()
            else:
                another_gender = "Парень" if gender == "Девушка" else "Девушка"
                partners = self.cursor.execute(
                    #"""SELECT * FROM users WHERE abs(age - ?) <= 2 and (partner == ? or partner == 'Без разницы') and
                    # id != ? EXCEPT ELECT initiator_id FROM matching""", (age, gender, user_id)).fetchall()

                    """SELECT id FROM users WHERE abs(age - ?) <= 2 and partner != ? and id != ? EXCEPT
                    SELECT initiator_id FROM matching""", (age, another_gender, user_id)).fetchall()

            res = [[user_id, partner[0]] for partner in partners]

            return self.cursor.executemany(
                """INSERT OR IGNORE INTO matching VALUES (NULL, ?, ?, NULL, NULL)""", res)

    def check_users_initiator_matching(self, user_id):
        with self.connection:
            return bool(self.cursor.execute("""SELECT initiator_id FROM matching WHERE initiator_id == ?""", (user_id, )
                                            ).fetchone())

    def search(self, user_id):
        with self.connection:
            return self.cursor.execute(
                """SELECT * FROM users WHERE id == 
                (SELECT interes_id FROM matching WHERE initiator_id == ? and like_initiator is NULL) or id == 
                (SELECT initiator_id FROM matching WHERE interes_id == ? and like_interes is NULL)""", (user_id,user_id)
            ).fetchone()

    def set_like(self, initiator_id, interes_id, like):
        if self.check_users_initiator_matching(initiator_id):
            with self.connection:
                return self.cursor.execute(
                    """UPDATE matching SET like_initiator = ? WHERE initiator_id == ? and interes_id == ?""",
                    (like, initiator_id, interes_id)).fetchone()
        else:
            with self.connection:
                return self.cursor.execute(
                    """UPDATE matching SET like_interes = ? WHERE interes_id == ? and initiator_id == ?""",
                    (like, initiator_id, interes_id)).fetchone()

    def is_relationship(self, initiator_id, interes_id):
        if self.check_users_initiator_matching(initiator_id):
            with self.connection:
                likes = self.cursor.execute(
                    """SELECT like_initiator, like_interes FROM matching WHERE initiator_id == ? and interes_id == ?""",
                    (initiator_id, interes_id)).fetchone()
        else:
            with self.connection:
                likes = self.cursor.execute(
                    """SELECT like_initiator, like_interes FROM matching WHERE interes_id == ? and initiator_id == ?""",
                    (initiator_id, interes_id)).fetchone()
        if likes is not None:
            if likes[0] is not None and likes[1] is not None:
                return likes[0] == likes[1]
        return False

    def update_user_photo(self, user_photo, usr_id):
        with self.connection:
            return self.cursor.execute("""UPDATE users SET photo = ? WHERE id = ?""", (user_photo, usr_id)).fetchall()

    def update_user_desc(self, user_desc, user_id):
        with self.connection:
            return self.cursor.execute("""UPDATE users SET desc = ? WHERE id = ?""", (user_desc, user_id)).fetchone()

    def delete_user_form(self, id_user):
        with self.connection:
            self.cursor.execute("""DELETE FROM users WHERE id = ?""", (id_user, ))
            self.cursor.execute("""DELETE FROM matching where initiator_id = ? or interes_id = ?""", (id_user, id_user))


db = Storage(path="C:\\Users\\хэй\\PycharmProjects\\FilesOrganizer\\src\\database\\", db_name=TelegramBot.database)
