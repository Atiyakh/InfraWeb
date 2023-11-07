import os, sqlite3 as sql

application_py = lambda application_path: f"""from importlib.machinery import SourceFileLoader
import os, pathlib

class Application:
    def __init__(self):
        __file__ = '{application_path.replace('\\', '/')}/application.py'
        self._application_path = __file__
        self.application_path = pathlib.Path(__file__).parent
        self.views_path = os.path.join(self.application_path, 'views.py')
        self.views = SourceFileLoader('views', self.views_path).load_module()
        self.models_path = os.path.join(self.application_path, 'models.py')
        self.models = SourceFileLoader('models', self.models_path).load_module()
        self.urls_path = os.path.join(self.application_path, 'urls.py')
        self.urls = SourceFileLoader('urls', self.urls_path).load_module()
        self.mapping = self.urls.URLMapping.raw_urls
        self.assets_path = os.path.join(self.application_path, 'assets')
        self.static_path = os.path.join(self.assets_path, 'static')
        self.media_path = os.path.join(self.assets_path, 'media')
        self.database_schemas_path = os.path.join(self.assets_path, 'database_schemas')
        self.sqlite3_path = os.path.join(self.application_path, 'sqlite3')
"""

def CreateApplication(application_name, application_path):
    if os.path.exists(application_path):
        print(f"[InfraWeb] Application {application_name} already exists.")
    else:
        os.mkdir(application_path)
        os.mkdir(os.path.join(application_path, 'assets'))
        for dir_ in ['database_schemas', 'media', 'static']:
            os.mkdir(os.path.join(application_path, 'assets', dir_))
        application_file = open(os.path.join(application_path, 'application.py'), 'w')
        application_file.write(application_py(application_path))
        application_file.close()
        models_file = open(os.path.join(application_path, 'models.py'), 'w')
        models_file.write("""from InfraWeb.Database import Models

# write your models here
""")
        models_file.close()
        urls_file = open(os.path.join(application_path, 'urls.py'), 'w')
        urls_file.write("""from InfraWeb.MiddleWare.Routing import Mapping, URL, MEDIA
import views

# bind your views and media directories to their proper urls

URLMapping = Mapping()
URLMapping.Structure(
)
""")
        urls_file.close()
        views_file = open(os.path.join(application_path, 'views.py'), 'w')
        views_file.write("""from InfraWeb.MiddleWare.Views import HttpResponse

# write your views here
""")
        views_file.close()
        init_file = open(os.path.join(application_path, '__init__.py'), 'w')
        init_file.write("""from importlib.machinery import SourceFileLoader
import os, pathlib

application = SourceFileLoader(
    'application',
    os.path.join(pathlib.Path(__file__).parent, 'application.py')
).load_module()

Application = application.Application
""")
        init_file.close()
        sqlite3 = open(os.path.join(application_path, 'sqlite3'), 'x')
        sqlite3.close()
        print(f"[InfraWeb] Application {application_name} has been created successfully.")
