import os, http.cookies
import base64, random
import pathlib
import sqlite3 as sql
import inspect

# Custom views-based response generating system.

class CSRF_Model():
    def add_csrf_token(self, request, caller_path):
        csrf_token = base64.b64encode(random.randbytes(25)).decode('utf-8')[:-2]
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(caller_path).parent, "website_data"))
        cur = ApplicationDB.cursor()
        cur.execute("DELETE FROM auth_InfraWeb_default_csrf_table WHERE client_ip=?", (request.remote_ip,))
        ApplicationDB.commit()
        cur.execute("INSERT INTO auth_InfraWeb_default_csrf_table (client_ip, csrf_token) VALUES(?,?)", (
            request.remote_ip, csrf_token
        )); ApplicationDB.commit()
        return csrf_token
    def verify_csrf_token(self, request):
        if 'csrf-token' in request.payload:
            ApplicationDB = sql.connect(os.path.join(pathlib.Path(request.caller_path_).parent, "website_data"))
            cur = ApplicationDB.cursor()
            cur.execute("SELECT csrf_token FROM auth_InfraWeb_default_csrf_table WHERE client_ip=?", (request.remote_ip,))
            query = cur.fetchone()
            if query:
                if request.payload['csrf-token'] == query[0]:
                    cur.execute("DELETE FROM auth_InfraWeb_default_csrf_table WHERE client_ip=?", (request.remote_ip,))
                    ApplicationDB.commit()
                    cur.close()
                    ApplicationDB.close()
                    return True
                else: return False
            else:
                cur.close()
                ApplicationDB.close()
                return False
        else: return False

def __load_csrf_to_database():
    try:
        ApplicationDB = sql.connect(os.path.join(pathlib.Path(__file__).parent, "Database\\sqlite3.db"))
        cur = ApplicationDB.cursor()
        cur.execute("""CREATE TABLE auth_InfraWeb_default_csrf_table(
    client_ip VARCHAR(50),
    csrf_token VARCHER(50)
);""")
        ApplicationDB.commit()
        cur.close()
        ApplicationDB.close()
    except sql.Error: pass

__load_csrf_to_database()

CSRF = CSRF_Model()

CONTENT_TYPE_LOCKUP_TABLE = {
    'html': 'text/html',
    'htm': 'text/html',
    'shtml': 'text/html',
    'txt': 'text/plain',
    'xml': 'application/xml',
    'json': 'application/json',
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'bmp': 'image/bmp',
    'ico': 'image/x-icon',
    'tif': 'image/tiff',
    'tiff': 'image/tiff',
    'svg': 'image/svg+xml',
    'mp3': 'audio/mpeg',
    'wav': 'audio/wav',
    'mp4': 'video/mp4',
    'avi': 'video/avi',
    'mkv': 'video/x-matroska',
    'css': 'text/css',
    'js': 'application/javascript',
    'zip': 'application/zip',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'jsonld': 'application/ld+json',
    'yaml': 'application/x-yaml',
    'rss': 'application/rss+xml',
    'atom': 'application/atom+xml',
    'csv': 'text/csv',
    'swf': 'application/x-shockwave-flash',
    'mpg': 'video/mpeg',
    'mpeg': 'video/mpeg',
    'php': 'application/x-httpd-php',
    'txt': 'text/plain',
    'rtf': 'text/rtf',
    'ogg': 'audio/ogg',
    'webm': 'video/webm',
    'ogv': 'video/ogg',
    'xhtml': 'application/xhtml+xml',
}

class Template():
    def __init__(self, content):
        if isinstance(content, str):
            self.content = content.encode('utf-8')
        elif isinstance(content, bytes):
            self.content = content
        else: raise ValueError(
            "[InfraWeb] Invalid Template content value (should be either str or bytes)."
        )

class InsertValues:
    def __init__(self, **values_dictionary):
        self.values_dictionary = values_dictionary

class ASSET:
    def __init__(self, source, content):
        self.source = source
        self.content = content

def ImportStatic(path, static_path=None, complete_path=False):
    if not complete_path:
        if not static_path:
            file_path = inspect.currentframe().f_back.f_code.co_filename
            static_path = os.path.join(pathlib.Path(file_path).parent, 'assets', 'static')
        file = open(os.path.join(static_path, path), 'rb')
        template = ASSET(
            source=path, content=file.read()
        ); file.close()
        return template
    else:
        file = open(path, 'rb')
        template = ASSET(
            source=path, content=file.read()
        ); file.close()
        return template

def ImportMedia(path, media_path=None, complete_path=False):
    if not complete_path:
        if not media_path:
            file_path = inspect.currentframe().f_back.f_code.co_filename
            media_path = os.path.join(pathlib.Path(file_path).parent, 'assets', 'media')
        file = open(os.path.join(media_path, path), 'rb')
        media = ASSET(
            source=path, content=file.read()
        ); file.close()
        return media
    else:
        file = open(path, 'rb')
        template = ASSET(
            source=path, content=file.read()
        ); file.close()
        return template

class HttpResponse:
    def ParseTemplate(self, template):
        if isinstance(template, bytes): template = template.decode('utf-8')
        if template.count("}}") == template.count("{{"):
            if template.count("}}") != 0:
                parsed_content = ''
                parsed_content += template[:template.find('{{')]
                template = template[:template.find('{{')]
            else: return template
        else: raise ValueError(
            "[InfraWeb] TemplateSytntaxError: Template extression left open."
        )
    def generate_response(self):
        if not isinstance(self.content, bytes):
            self.content = self.content.__str__().encode('utf-8')
        response = (
            f"{self.version} {self.status_code} {self.status_text}\n\r".encode('utf-8')+
            f"Content-Type: {self.content_type}\r\n\r\n".encode('utf-8')+
            self.content
        )
        return response
    def __init__(self, content, values:InsertValues=InsertValues(), request=None, status_code=200, status_text='OK', version="HTTP/1.1", content_type="text/html"):
        if isinstance(content, ASSET):
            content_type = CONTENT_TYPE_LOCKUP_TABLE[content.source.split('.')[-1]]
            if content_type == 'text/html':
                content = ParseTemplate(content.content, values.values_dictionary, request)
            else:
                content = content.content
        elif isinstance(content, Template):
            content = ParseTemplate(content.content, values.values_dictionary, request)
        elif isinstance(content, str):
            content = content.encode('utf-8')
        if type(content).__name__ not in ['str', 'ASSET', 'bytes']: raise ValueError(
            "[InfraWeb] Content should ONLY be str, bytes, or ASSET (use Views.ImportStatic or Views.ImportMedia) objects."
        )
        self.version = version
        self.status_code = status_code
        self.status_text = status_text
        self.content_type = content_type
        self.content = content
        self.cookies = dict()
        self.response = self.generate_response()

TEMPLATES_RESULTS = dict()

def LOADSTATIC(id_, path): TEMPLATES_RESULTS[id_] = "/static/"+path
def LOADMEDIA(id_, path): TEMPLATES_RESULTS[id_] = "/media/"+path
def INSERTHTML(id_, html): TEMPLATES_RESULTS[id_] = html

def ParseTemplateSyntax(id_, syntax, values):
    syntax = syntax.replace("LOADSTATIC(", f"LOADSTATIC({id_}, ")
    syntax = syntax.replace("LOADMEDIA(", f"LOADMEDIA({id_}, ")
    syntax = syntax.replace("INSERTHTML(", f"INSERTHTML({id_}, ")
    exec(f"values = {values}\n" + syntax, globals())
    return TEMPLATES_RESULTS[id_]

def ParseTemplate(template, values_dictionary, request):
    if isinstance(template, bytes): template = template.decode('utf-8')
    if template.count("}}") == template.count("{{"):
        parsed_content = ''
        id_ = id(parsed_content)
        while True:
            if template.count("}}") != 0:
                parsed_content += template[:template.find('{{')]
                template = template[template.find('{{')+2:]
                if template[:template.find('}}')] == "CSRF-TOKEN":
                    if request:
                        csrt_token = CSRF.add_csrf_token(request, request.caller_path_)
                        parsed_content += f'<input type="hidden" name="csrf-token" value="{csrt_token}">'
                    else:
                        print("- warning: no request object was provided [unable generate a csrf token]")
                else:
                    parsed_content += ParseTemplateSyntax(id_, template[:template.find('}}')], values_dictionary)
                template = template[template.find('}}')+2:]
                if id_ in TEMPLATES_RESULTS: del TEMPLATES_RESULTS[id_]
            else:
                parsed_content += template
                break
        if request:
            parsed_content += http.cookies.SimpleCookie(request.cookies).js_output()
        else:
            print("- warning: no request object was provided [unable to set user cookies]")
        return parsed_content
    else: raise ValueError(
        "[InfraWeb] TemplateSytntaxError: Template expression left open."
    )

class ResponseHolder:
    def __init__(self, response):
        self.response = response

def redirect(request, location, status_code=302, status_text='Found', version="HTTP/1.1"):
    version = version
    location = location
    status_code = status_code
    status_text = status_text
    cookies = request.cookies
    raw_cookies = ''
    if cookies:
        for cookie_name, cookie_value in cookies.items():
            if isinstance(cookie_value, bytes): cookie_value = cookie_value.decode('utf-8')
            raw_cookies += f"{cookie_name}={cookie_value}; "
    response = (
        f"{version} {status_code} {status_text}\n\r".encode('utf-8')+
        f"Location: {location}\r\n".encode('utf-8')
    )
    if raw_cookies:
        response += f"Set-Cookie: {raw_cookies[:-2]}\n\r".encode('utf-8')
    response += b"\n\r"
    return ResponseHolder(response)

def render(request, template_path, values:dict={}, content_type="application/xhtml+xml"):
    file_path = inspect.currentframe().f_back.f_code.co_filename
    static_path = os.path.join(pathlib.Path(file_path).parent, 'assets', 'static')
    response = HttpResponse(ImportStatic(template_path, static_path=static_path), InsertValues(**values), request=request, content_type=content_type)
    return response

def verify_csrf(view_function):
    async def csrf_constrain(request, **keywargs):
        if request.method == 'POST':
            if CSRF.verify_csrf_token(request):
                return view_function(request, **keywargs)
            else:
                return redirect(request, '/csrf-error')
        else: return view_function(request, **keywargs)
    return csrf_constrain

def login_needed(url):
    def decorator_wrapper(view_function):
        async def login_constrain(request, **keywargs):
            if request.authenticated_user:
                return view_function(request, **keywargs)
            else:
                if isinstance(url, str):
                    return redirect(request, url)
                else:
                    return redirect(request, '/login')
        return login_constrain
    return decorator_wrapper

def superusers_only(url):
    def decorator_wrapper(view_function):
        async def superuser_constrain(request, **keywargs):
            if request.authenticated_superuser:
                return view_function(request, **keywargs)
            else:
                if isinstance(url, str):
                    return redirect(request, url)
                else:
                    return redirect(request, '/admin')
        return superuser_constrain
    return decorator_wrapper
