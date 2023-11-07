import traceback, json
from urllib.parse import parse_qs
import time, sqlite3 as sql
import http.cookies
import pathlib, os
from InfraWeb.MiddleWare.Views import HttpResponse
import inspect

#  This is the request processing unit, as the name suggests,
# it provides the core  "async_server" with the functions and
# classes needed to route and generate  the client's request.
# it's also generates an appropriate response and returns it.
# see EXCEPTIONS_LOOKUP_TABLE below for proper web errors and
# exceptions catching.

EXCEPTIONS_LOOKUP_TABLE = {
    '/csrf-error': ['csrf_exception', 'Request Rejected:<br>INVALID_CSRF_TOKEN'],
} #   error url    viewf unction name             default response

def parse_cookie_string(cookie_string):
    cookie = http.cookies.SimpleCookie()
    cookie.load(cookie_string)
    cookie_dict = {key: morsel.value for key, morsel in cookie.items()}
    return cookie_dict

class HttpRequest:
    def __init__(self, method, url, http_version, headers, payload, peername, caller_path):
        self.caller_path_ = caller_path
        self.url = url
        self.method = method
        self.headers = headers
        self.http_version = http_version
        self.payload = payload
        if 'Cookie' in self.headers:
            self.raw_cookies = self.headers['Cookie']
        else: self.raw_cookies = ''
        if self.raw_cookies:
            self.cookies = parse_cookie_string(self.raw_cookies)
        else: self.cookies = dict()
        if 'session' in self.cookies: self.session = self.cookies['session']
        else: self.session = None
        if self.session:
            ApplicationDB = sql.connect(os.path.join(pathlib.Path(caller_path).parent, "website_data"))
            cur = ApplicationDB.cursor()
            try: cur.execute("SELECT username, password, email, first_name, last_name, authentication FROM auth_InfraWeb_default_user_table WHERE authentication=?", (self.session,))
            except sql.IntegrityError:
                cur.close()
                ApplicationDB.close()
                return False
            query = cur.fetchone()
            ApplicationDB.commit()
            cur.close()
            ApplicationDB.close()
        else: query = False
        if query:
            rows = ['username', 'password', 'email', 'first_name', 'last_name', 'authentication']
            self.user_creditentials = {rows[num]: query[num] for num in range(len(rows))}
            self.authenticated_user = True
        else:
            self.user_creditentials = None
            self.authenticated_user = False
        if 'superuser_session' in self.cookies: self.superuser_session = self.cookies['superuser_session']
        else: self.superuser_session = None
        if self.superuser_session:
            ApplicationDB = sql.connect(os.path.join(pathlib.Path(caller_path).parent, "website_data"))
            cur = ApplicationDB.cursor()
            try: cur.execute("SELECT username, password, email, first_name, last_name, authentication FROM auth_InfraWeb_default_superuser_table WHERE authentication=?", (self.session,))
            except sql.IntegrityError:
                cur.close()
                ApplicationDB.close()
                return False
            query = cur.fetchone()
            ApplicationDB.commit()
            cur.close()
            ApplicationDB.close()
        else: query = False
        if query:
            rows = ['username', 'password', 'email', 'first_name', 'last_name', 'authentication']
            self.superuser_creditentials = {rows[num]: query[num] for num in range(len(rows))}
            self.authenticated_superuser = True
        else:
            self.superuser_creditentials = None
            self.authenticated_superuser = False
        self.remote_peername = peername
        self.remote_ip = self.remote_peername[0]
        self.remote_port = self.remote_peername[1]

def user_definded_exception_views(url, req, mapping):
    if url in EXCEPTIONS_LOOKUP_TABLE:
        exception_, default_error_message = EXCEPTIONS_LOOKUP_TABLE[url]
        if hasattr(mapping, exception_):
            return mapping.__getattribute__(exception_)(req)
        else: return HttpResponse(default_error_message, status_code=404, status_text='CSRF Error')

class ResponseHolder:
    def __init__(self, content):
        self.response = content

async def request_processor_(request, peername, mapping):
    caller_path = inspect.currentframe().f_back.f_code.co_filename
    try:
        try:
            request_headers, request_payload = request.decode('utf-8').split("\r\n\r\n")
        except:
            if not request:
                print('[InfraWeb] Empty request.')
                return
        request_headers = request_headers.splitlines()
        method, url, http_version = request_headers[0].split(' ')
        headers_format = '{\n'
        for line in request_headers[1:]:
            key, val = line.split(':', 1)
            val = val.replace('"', '\\"')
            if line == request_headers[1:][-1]: headers_format += f'''"{key}": "{val[1:]}"\n'''
            else: headers_format += f'''"{key}": "{val[1:]}",\n'''
        headers_format += '}'
        headers = json.loads(headers_format)
        url_query_p = parse_qs(request_payload)
        url_query_parsed = {key: val[0] for key, val in url_query_p.items()}
        req = HttpRequest(method, url, http_version, headers, url_query_parsed, peername, caller_path)
        print(f"[InfraWeb] {method} Request - {url} - {time.ctime()}")
        try:
            view_function = await mapping.URLMapping.RetrieveView(url)
            if view_function:
                processed_request = await view_function(req)
                return processed_request
            else:
                exception_view = user_definded_exception_views(url, req, mapping)
                if exception_view: return exception_view
                if url == '/':
                    welcome_file = open(os.path.join(pathlib.Path(__file__).parent, 'welcome.html'), 'rb')
                    data = welcome_file.read()
                    welcome_file.close()
                    return HttpResponse(data)
                print(f"[InfraWeb] {req.url} - Not Found 404 - {time.ctime()}")
                if hasattr(mapping, 'NotFound404'):
                    return mapping.__getattribute__('NotFound404')(req)
        except:
            traceback.print_exc()
            print('[InfraWeb] Request processing failure.')
    except:
        traceback.print_exc()
        print('[InfraWeb] Request processing failure.')
