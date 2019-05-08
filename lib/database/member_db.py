from lib.database.database import Database
import sqlite3
import time


class MemberDB(Database):
    def __init__(self):
        Database.__init__(self, "MemberDB")
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        sql = """
            CREATE TABLE IF NOT EXISTS members (
                member_id integer PRIMARY KEY,
                gdpr_agreed integer,
                gdpr_agreed_date integer
            );
        """
        try:
            cursor.execute(sql)
            print("[MEMBERDB] Successfully initialised members table.")
        except sqlite3.Error as e:
            print("[MEMBERDB] Error creating members table.")
            print("[MEMBERDB] {}".format(e))
        except:
            print("[MEMBERDB] Unhandled exception whilst creating members table.")
            print("[MEMBERDB] {}".format(e))
        finally:
            self.conn.commit()
            cursor.close()

    def user_accepted_gdpr(self, user_record):
        user_id = user_record.get("user_id")
        (user_exists, member_object) = self._check_user_exists(user_id)
        if user_exists:
            gdpr_agreed = member_object[1]
            if gdpr_agreed is not None:
                return gdpr_agreed
            else:
                return -1
        else:
            return -1

    def _check_user_exists(self, user_id):
        cursor = self.conn.cursor()
        sql = "SELECT * FROM members WHERE member_id=?"
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        if len(rows) == 0:
            self._create_member(user_id)
            return (False, None)
        else:
            member_object = rows[0]
            return (True, member_object)

    def _create_member(self, user_id):
        cursor = self.conn.cursor()
        sql = """INSERT INTO members(member_id, gdpr_agreed, gdpr_agreed_date) VALUES (?,?,?)"""
        cursor.execute(sql, (user_id, None, None,))
        self.conn.commit()
        cursor.close()

    def update_gdpr(self, user_id, response):
        cursor = self.conn.cursor()
        sql = """UPDATE members SET gdpr_agreed=?, gdpr_agreed_date=? WHERE member_id = ?"""
        try:
            cursor.execute(sql, (response, int(time.time()), user_id,))
            self.conn.commit()
            cursor.close()
        except:
            print("Failed to update GDPR compliance.")
