from sys import argv
import os, sqlite3 as sql

def load_default_tables_to_database(database_path):
    ApplicationDB = sql.connect(database_path)
    cur = ApplicationDB.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS auth_InfraWeb_default_user_table(
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(300) NOT NULL,
    email VARCHAR(250) UNIQUE,
    first_name VARCHAR(250),
    last_name VARCHAR(250),
    authentication VARCHAR(700)
);""")
    ApplicationDB.commit()
    cur.execute("""CREATE TABLE auth_InfraWeb_default_superuser_table(
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(300) NOT NULL,
    email VARCHAR(250) UNIQUE,
    first_name VARCHAR(250),
    last_name VARCHAR(250),
    authentication VARCHAR(700)
);""")
    ApplicationDB.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS auth_InfraWeb_default_csrf_table(
    client_ip VARCHAR(50),
    csrf_token VARCHER(50)
);""")
    ApplicationDB.commit()
    cur.close()
    ApplicationDB.close()
project_name = argv[1]

os.mkdir(os.path.join(project_name))

os.mkdir(os.path.join(project_name, 'applications'))

init_file = open(os.path.join(project_name, 'applications', '__init__.py'), 'x')
init_file.close()

init_file = open(os.path.join(project_name, '__init__.py'), 'x')
init_file.close()

server_file = open(os.path.join(project_name, 'async_server.py'), 'w')
server_file.write("""from InfraWeb.MiddleWare.request_processor import request_processor_
from socket import gethostbyname, gethostname
import traceback, pathlib, os, asyncio, ssl
import mapping

# asynchronous HTTP-like low-level Server
# HTTPS-supported server. straightforward
# certificates loading. default port 8888

class AsyncServer:
    async def request_handler(self, reader, writer):
        try:
            self.far_host_peername = writer.get_extra_info('peername')
            request_content = await reader.read(65_000)
            generated_response = await request_processor_(request_content, self.far_host_peername, mapping)
            if generated_response:
                response = generated_response.response
            else:
                response = b'HTTP/1.1 404 Not Found\n\r\n\r404 Page Not Found'
            writer.write(response)
            await writer.drain()
            writer.close()
        except:
            traceback.print_exc()
    def set_port(self, port):
        self.port = port
    def set_secure(self, secure):
        self.secure = secure
    async def start_server(self):
        try:
            self.host = gethostbyname(gethostname())
            if self.secure:
                self.certificatePath = os.path.join(pathlib.Path(__file__).parent, 'Certificates\\ssl_tls_certificate.pem')
                self.privatKeyPath = os.path.join(pathlib.Path(__file__).parent, 'Certificates\\server_private_key.pem')
                self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                self.context.load_cert_chain(
                    certfile=self.certificatePath, 
                    keyfile=self.privatKeyPath
                )
                self.server_stream = await asyncio.start_server(
                    self.request_handler, self.host,
                    self.port, ssl=self.context
                )
            else:
                self.server_stream = await asyncio.start_server(
                    self.request_handler, self.host, self.port
                )
            print(f"[InfraWeb] Web server initiated successfully - http://{gethostbyname(gethostname())}:{self.port}/")
            await self.server_stream.serve_forever()
        except OSError as e:
            if e.errno == 10048:
                print("[InfraWeb] Server is already running.")

async def server_runner(port, secure, installed_apps_):
    global installed_apps
    installed_apps = installed_apps_
    server = AsyncServer()
    server.set_port(port)
    server.set_secure(secure)
    await server.start_server()
""")
server_file.close()

manage_file = open(os.path.join(project_name, 'manage.py'), 'w')
manage_file.write("""from InfraWeb.MiddleWare import Console
from settings import INSTALLED_APPLICATIONS
from async_server import server_runner

# InfraWeb (V1)

# Hit run and type the command "RunServer"!
# Follow the link the server will provide you with

if __name__ == '__main__':
    Console.InteractiveConsole(
        server_runner=server_runner,
        installed_apps=INSTALLED_APPLICATIONS
    )
""")
manage_file.close()

mapping_file = open(os.path.join(project_name, 'mapping.py'), 'w')
mapping_file.write("""from InfraWeb.MiddleWare.Routing import Mapping, ExtractApplicationsMapping
from settings import INSTALLED_APPLICATIONS

URLMapping = Mapping()
URLMapping.Structure(
    *ExtractApplicationsMapping(INSTALLED_APPLICATIONS),
)
""")
mapping_file.close()

settings_file = open(os.path.join(project_name, 'settings.py'), 'w')
settings_file.write("""from applications import *

INSTALLED_APPLICATIONS = {
}
""")
settings_file.close()

website_data = open(os.path.join(project_name, 'website_data'), 'x')
website_data.close()
load_default_tables_to_database(os.path.join(project_name, 'website_data'))

print("[InfraWeb] Your project has been created successfully.")
