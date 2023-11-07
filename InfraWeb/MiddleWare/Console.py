from InfraWeb.Database.models_formater import ModelsParser
from InfraWeb.Database.Models import UpdateSchema
from InfraWeb.MiddleWare.Cryptography import Hash
from InfraWeb.Applications.ApplicationsManager import CreateApplication
from InfraWeb.MiddleWare.Authentication import SuperUser
import asyncio, threading, traceback
import os, pathlib, inspect

def Execution(code):
    exec(code, globals())

def InteractiveConsole(server_runner, installed_apps):
    caller_path = inspect.currentframe().f_back.f_code.co_filename
    def RunServer(port, secure, installed_apps):
        asyncio.run(server_runner(port, installed_apps, secure))
    print('[InfraWeb] Interactive Console Activated...')
    while True:
        command = input()
        if command.find("SaveSchema ") == 0:
            application_name = command[11:].strip()
            if application_name in installed_apps:
                models = installed_apps[application_name].models_path
                database_schemas_dir = installed_apps[application_name].database_schemas_path
                try: ModelsParser(models, database_schemas_dir)
                except:
                    traceback.print_exc()
                    raise ValueError(
                        "[InfraWeb] Failed to save your schema."
                    )
            else: raise LookupError(
                "[InfraWeb] Cannot find your application."
            )
        elif command.find("StartApplication ") == 0:
            application_name = command[17:].strip()
            application_path = os.path.join(pathlib.Path(caller_path).parent, 'applications', application_name)
            CreateApplication(application_name, application_path)
        elif command.find("UpdateSchema ") == 0:
            application_name = command[13:].strip()
            if application_name in installed_apps:
                database_path = installed_apps[application_name].sqlite3_path
                try: UpdateSchema(database_path)
                except:
                    traceback.print_exc()
                    raise ValueError(
                        "[InfraWeb] Failed to update the database schema."
                    )
        elif command.find("RunServer") == 0:
            if len(command) > 11:
                port = int(command[9:].strip())
            else: port = 8888
            try: threading.Thread(target=RunServer, args=(port, installed_apps, False)).start()
            except:
                raise ValueError(
                    "[InfraWeb] Unable to run the the server."
                )
        elif command.find("RunSecure") == 0:
            if len(command) > 11:
                port = int(command[9:].strip())
            else: port = 8888
            try: threading.Thread(target=RunServer, args=(port, installed_apps, True)).start()
            except:
                raise ValueError(
                    "[InfraWeb] Unable to run the the server."
                )
        elif command.find("LoadCertificate") == 0:
            try:
                cert_path = command[15:].strip()
                cert_file = open(cert_path, 'rb')
                cert_content = cert_file.read()
                cert_file.close()
                inner_file = open(os.path.join(pathlib.Path(__file__).parent, 'Certificates\\ssl_tls_certificate.pem'), 'wb')
                inner_file.write(cert_content)
                inner_file.close()
            except:
                traceback.print_exc()
                print('[InfraWeb] Unable to load the certificate.')
        elif command.find("LoadCryptoKey") == 0:
            try:
                key_path = command[13:].strip()
                key_file = open(key_path, 'rb')
                key_content = key_file.read()
                key_file.close()
                inner_file = open(os.path.join(pathlib.Path(__file__).parent, 'Certificates\\cryptographic_key.pem'), 'wb')
                inner_file.write(key_content)
                inner_file.close()
            except:
                traceback.print_exc()
                print('[InfraWeb] Unable to load the certificate.')
        elif command == 'RegisterSuperuser':
            username = input("enter username: ")
            email = input("enter email: ")
            password = input("enter password: ")
            password_repeated = input("repeat password: ")
            if password != password_repeated:
                print("The passwords are not the same.")
            else:
                first_name = input("enter first name: ")
                last_name = input("enter last name: ")
                hashed_password = Hash.Sha384(password)
                SuperUser.create_superuser(
                    None, username=username,
                    password=hashed_password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                print(f"[InfraWeb] Superuser {first_name} registered successfully\n")
        elif command == 'StartApplication':
            pass
        else:
            threading.Thread(target=Execution, args=(command,)).start()
