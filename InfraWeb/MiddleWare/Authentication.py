from InfraWeb.MiddleWare.Views import HttpResponse, Template, verify_csrf
from InfraWeb.MiddleWare.Cryptography import Hash
import pathlib, os, base64, time, sqlite3 as sql
from inspect import currentframe

# Custom cookies-based authentication system

WEBSITE_DATA = None

def ExtractDatabasePath(caller_path):
    path = pathlib.Path(caller_path)
    file_name = path.name
    if file_name == 'views.py':
        return os.path.join(path.parent.parent.parent, 'website_data')
    elif file_name == 'mapping.py':
        return os.path.join(path.parent, 'website_data')
    else: raise NotImplementedError(
        "[InfraWeb] AccessDenied: Unable to authorize or authenticate users outside the views or mapping scope."
    )

def ConnectDatabase(path):
    global WEBSITE_DATA
    caller_path = path.f_back.f_code.co_filename
    database_path = ExtractDatabasePath(caller_path)
    WEBSITE_DATA = sql.connect(database_path)

class SuperUser():
    def create_superuser(request, username, password, email=None, first_name=None, last_name=None):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        hashed_password = Hash.Sha384(password)
        try:
            cur.execute("INSERT INTO auth_InfraWeb_default_user_table (username, password, email, first_name, last_name, authentication)\nVALUES(?, ?, ?, ?, ?, ?)", (
                username, hashed_password, email, first_name, last_name, None
            ))
            ApplicationDB.commit()
            user_id = cur.lastrowid
            cur.close()
            ApplicationDB.close()
            return user_id
        except sql.IntegrityError:
            cur.close()
            ApplicationDB.close()
            return False

    def login_superuser(request, password, email=None, username=None):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        authentication = base64.b64encode(f'{request.remote_ip}|{time.ctime()}'.encode('utf-8')).decode('utf-8')[:-2]
        hashed_password = Hash.Sha384(password)
        if email:
            cur.execute("UPDATE auth_InfraWeb_default_superuser_table set authentication=? WHERE email=? AND password=?", (
                authentication, email, hashed_password
            )); ApplicationDB.commit()
        elif username:
            cur.execute("UPDATE auth_InfraWeb_default_superuser_table set authentication=? WHERE username=? AND password=?", (
                authentication, username, hashed_password
            )); ApplicationDB.commit()
        else: return None
        if cur.rowcount == 1: auth = True
        else: auth = False
        if auth:
            cur.execute("SELECT * FROM auth_InfraWeb_default_superuser_table WHERE authentication=?", (authentication,))
            request.superuser_creditentials = cur.fetchone()[1:]
            request.authenticated_superuser = True
            request.superuser_session = authentication
            request.cookies['superuser_session'] = authentication
        cur.close()
        ApplicationDB.close()
        return auth

    def logout_superuser(request, password, username=None, email=None):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        hashed_password = Hash.Sha384(password)
        if email:
            cur.execute("UPDATE auth_InfraWeb_default_superuser_table SET authentication=? WHERE email=? AND password=?", (
                None, email, hashed_password
            ))
        elif username:
            cur.execute("UPDATE auth_InfraWeb_default_superuser_table SET authentication=? WHERE username=? AND password=?", (
                None, username, hashed_password
            ))
        else: return None
        if cur.rowcount == 1:
            request.superuser_session = ''
            request.cookies['superuser_session'] = ''
            request.authenticated_superuser = False
            request.superuser_creditentials = None
            return True
        else: return False

    def set_username(request, username):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        cur.execute("UPDATE auth_InfraWeb_default_superuser_table SET username=? WHERE authentication=?", (
            username, request.remote_ip
        ))
        request.superuser_creditentials['username'] = username
        ApplicationDB.commit()
        cur.close()
        ApplicationDB.close()

    def set_password(request, password):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        hashed_password = Hash.Sha384(password)
        cur.execute("UPDATE auth_InfraWeb_default_superuser_table SET password=? WHERE authentication=?", (
            hashed_password , request.remote_ip
        ))
        request.superuser_creditentials['password'] = hashed_password
        ApplicationDB.commit()
        cur.close()
        ApplicationDB.close()

    def set_email(request, email):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        cur.execute("UPDATE auth_InfraWeb_default_superuser_table SET email=? WHERE authentication=?", (
            email, request.remote_ip
        ))
        request.superuser_creditentials['email'] = email
        ApplicationDB.commit()
        ApplicationDB.close()
        cur.close()

    def set_first_name(request, first_name):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        cur.execute("UPDATE auth_InfraWeb_default_superuser_table SET first_name=? WHERE authentication=?", (
            first_name, request.remote_ip
        ))
        request.superuser_creditentials['first_name'] = first_name
        ApplicationDB.commit()
        cur.close()
        ApplicationDB.close()

    def set_last_name(request, last_name):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        cur.execute("UPDATE auth_InfraWeb_default_superuser_table SET last_name=? WHERE authentication=?", (
            last_name, request.remote_ip
        ))
        request.superuser_creditentials['last_name'] = last_name
        ApplicationDB.commit()
        cur.close()
        ApplicationDB.close()

class User():
    def create_user(request, username, password, email=None, first_name=None, last_name=None):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        cur.execute("UPDATE auth_InfraWeb_default_user_table SET authentication=? WHERE authentication=?", (
            None, request.remote_ip
        )); ApplicationDB.commit()
        hashed_password = Hash.Sha384(password)
        try:
            authentication = base64.b64encode(f'{request.remote_ip}|{time.ctime()}'.encode('utf-8')).decode('utf-8')[:-2]
            cur.execute("INSERT INTO auth_InfraWeb_default_user_table (username, password, email, first_name, last_name, authentication)\nVALUES(?, ?, ?, ?, ?, ?)", (
                username, hashed_password, email, first_name, last_name, authentication
            ))
            ApplicationDB.commit()
            user_id = cur.lastrowid
            cur.close()
            ApplicationDB.close()
            request.cookies['session'] = authentication
            request.session = authentication
            request.user_creditentials = {
                'username': username,
                'password': hashed_password,
                'email': email,
                'first_name': first_name,
                'last_name': first_name,
                'authentication': authentication
            }
            request.authenticated_user = True
            return user_id
        except sql.IntegrityError:
            cur.close()
            ApplicationDB.close()
            return False

    def login_user(request, password, email=None, username=None):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        authentication = base64.b64encode(f'{request.remote_ip}|{time.ctime()}'.encode('utf-8')).decode('utf-8')[:-2]
        hashed_password = Hash.Sha384(password)
        if email:
            cur.execute("UPDATE auth_InfraWeb_default_user_table set authentication=? WHERE email=? AND password=?", (
                authentication, email, hashed_password
            )); ApplicationDB.commit()
        elif username:
            cur.execute("UPDATE auth_InfraWeb_default_user_table set authentication=? WHERE username=? AND password=?", (
                authentication, username, hashed_password
            )); ApplicationDB.commit()
        else: return None
        if cur.rowcount == 1: auth = True
        else: auth = False
        if auth:
            cur.execute("SELECT * FROM auth_InfraWeb_default_user_table WHERE authentication=?", (authentication,))
            request.user_creditentials = cur.fetchone()[1:]
            request.authenticated_user = True
            request.session = authentication
            request.cookies['session'] = authentication
        cur.close()
        ApplicationDB.close()
        return auth

    def logout_user(request, password, username=None, email=None):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        hashed_password = Hash.Sha384(password)
        if email:
            cur.execute("UPDATE auth_InfraWeb_default_user_table SET authentication=? WHERE email=? AND password=?", (
                None, email, hashed_password
            ))
        elif username:
            cur.execute("UPDATE auth_InfraWeb_default_user_table SET authentication=? WHERE username=? AND password=?", (
                None, username, hashed_password
            ))
        else: return None
        if cur.rowcount == 1:
            request.session = ''
            request.cookies['session'] = ''
            request.authenticated_user = False
            request.user_creditentials = None
            return True
        else: return False

    def set_username(request, username):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        cur.execute("UPDATE auth_InfraWeb_default_user_table SET username=? WHERE authentication=?", (
            username, request.remote_ip
        ))
        request.user_creditentials['username'] = username
        ApplicationDB.commit()
        cur.close()
        ApplicationDB.close()

    def set_password(request, password):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        hashed_password = Hash.Sha384(password)
        cur.execute("UPDATE auth_InfraWeb_default_user_table SET password=? WHERE authentication=?", (
            hashed_password , request.remote_ip
        ))
        request.user_creditentials['password'] = hashed_password
        ApplicationDB.commit()
        cur.close()
        ApplicationDB.close()

    def set_email(request, email):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        cur.execute("UPDATE auth_InfraWeb_default_user_table SET email=? WHERE authentication=?", (
            email, request.remote_ip
        ))
        request.user_creditentials['email'] = email
        ApplicationDB.commit()
        ApplicationDB.close()
        cur.close()

    def set_first_name(request, first_name):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        cur.execute("UPDATE auth_InfraWeb_default_user_table SET first_name=? WHERE authentication=?", (
            first_name, request.remote_ip
        ))
        request.user_creditentials['first_name'] = first_name
        ApplicationDB.commit()
        cur.close()
        ApplicationDB.close()

    def set_last_name(request, last_name):
        if not WEBSITE_DATA:
            ConnectDatabase(currentframe())
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
        cur = ApplicationDB.cursor()
        cur.execute("UPDATE auth_InfraWeb_default_user_table SET last_name=? WHERE authentication=?", (
            last_name, request.remote_ip
        ))
        request.user_creditentials['last_name'] = last_name
        ApplicationDB.commit()
        cur.close()
        ApplicationDB.close()
