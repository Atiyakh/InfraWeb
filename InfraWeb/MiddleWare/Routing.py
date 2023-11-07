from InfraWeb.MiddleWare.Views import HttpResponse, ImportMedia, ImportStatic
from urllib.parse import urlparse, parse_qs
import time, sys, os, traceback
import inspect, pathlib

# custom routing system.
# direct static and media routing and simple html inserting inside your template file.
# facilitated template processing, and easy views-based assets importation.

def FilesUrlsGenerator(dir_, path):
    file_paths = []
    for root, _, files in os.walk(dir_):
        for file in files:
            file_path = os.path.join(root, file)
            path_ = file_path.replace(dir_, path).replace('\\', '/')
            file_paths.append(path_)
    return file_paths

def ExtractApplicationsMapping(installed_apps:dict):
    apps = list(installed_apps.values())
    mapping = []
    for app in apps:
        mapping.extend(app.mapping)
    return mapping

class STATIC:
    def __init__(self, path):
        caller_path = inspect.currentframe().f_back.f_code.co_filename
        self.static_path = os.path.join(pathlib.Path(caller_path).parent, 'assets', 'static')
        if os.path.isdir(self.static_path):
            self.path = path
        else: raise ValueError(
            f"[InfraWeb] Unable to find your static folder."
        )
    def static_route_parser(self, req):
        file = os.path.join(self.static_path, req.url.split('/')[-1])
        return HttpResponse(ImportStatic(file, complete_path=True))

class MEDIA:
    def __init__(self, path):
        caller_path = inspect.currentframe().f_back.f_code.co_filename
        self.media_path = os.path.join(pathlib.Path(caller_path).parent, 'assets', 'media')
        if os.path.isdir(self.media_path):
            self.path = path
        else: raise ValueError(
            f"[InfraWeb] Unable to find your media folder."
        )
    def media_route_parser(self, req):
        file = os.path.join(self.media_path, *req.url.split('/')[2:])
        return HttpResponse(ImportMedia(file, complete_path=True))

async def response_extractor(route, req, param):
    try:
        if type(route).__name__ == 'coroutine':
            route = await route
        if type(route).__name__ == 'function' or type(route).__name__ == 'method':
            route = route(req, **param)
        if type(route).__name__ in ('HttpResponse', 'ResponseHolder'):
            return route
        if type(route).__name__ not in ('HttpResponse', 'ResponseHolder', 'function', 'coroutine'):
            raise RecursionError(
                "[SockServer] Unable to extract a proper response.", route
            )
        route = await response_extractor(route, req, param)
        return route
    except: traceback.print_exc()

async def enhanced_response_generation(path, route, query, param, req):
    req.url_query = query
    req.param = param
    req.path = path
    return await response_extractor(route, req, param)


class ArgumentURL(list):
    def __init__(self, view_function):
        self.view_function = view_function
    def add_fragment(self, fragment):
        self.append(fragment)
    def compare_urls(self, url):
        url_fragments = url.split('/')[1:]
        args_dictionary = dict()
        if len(url_fragments) == len(self):
            valid = True
            for fragment_number in range(len(self)):
                if not (self.__getitem__(fragment_number) == url_fragments[fragment_number]):
                    valid = False
                elif type(self.__getitem__(fragment_number)).__name__ == 'FragmentArgumentURL':
                    args_dictionary[self.__getitem__(fragment_number).arg_name] = url_fragments[fragment_number]
            if valid: return self.view_function, args_dictionary
            else: return False
        else: return False

class FragmentArgumentURL:
    def __eq__(self, __value:str):
        val_type = 'str'
        if __value.isnumeric():
            val_type = 'int'
        elif (len(__value.split('.')) == 2):
            if (__value.split('.')[0].isnumeric()) and (__value.split('.')[1].isnumeric()):
                val_type = 'float'
        if val_type == self.arg_type: return True
        else: return False
    def __init__(self, arg_type, arg_name):
        self.arg_type = arg_type
        self.arg_name = arg_name

class Mapping:
    def __init__(self):
        self.urls = dict()
        self.arg_urls = []
        self.raw_urls = []
    def seek_argument_urls(self, url):
        for arg_url in self.arg_urls:
            result = arg_url.compare_urls(url)
            if result: return result
    def parse_argument(self, url, view_function):
        is_arg = False
        url_fragments = []
        fragments = url.path.split('/')[1:]
        for fragment_number in range(len(fragments)):
            fragment = fragments[fragment_number]
            if (fragment[0] == '<') and (fragment[-1] == '>'):
                is_arg = True
                arg_cmd = fragment[1:-1]
                if ':' in arg_cmd:
                    arg_type, arg_name = arg_cmd.split(':')
                    if arg_type in ['str', 'int', 'float']:
                        url_fragments.append(FragmentArgumentURL(
                            arg_type=arg_type,
                            arg_name=arg_name
                        ))
                else: raise SyntaxError(
                    "[InfraWeb] Invalid argument URL syntax."
                )
            else: url_fragments.append(fragment)
        if is_arg:
            argument_url = ArgumentURL(view_function)
            for fragment in url_fragments:
                argument_url.add_fragment(fragment)
            self.arg_urls.append(argument_url)

    def Structure(self, *urls):
        self.raw_urls += urls
        for url in urls:
            if isinstance(url, MEDIA):
                for file in FilesUrlsGenerator(url.media_path, url.path):
                    self.urls[file] = url.media_route_parser
            elif isinstance(url, STATIC):
                for file in FilesUrlsGenerator(url.static_path, url.path):
                    self.urls[file] = url.static_route_parser
            elif isinstance(url, URL):
                self.urls[url.path] = url.application_view
                self.parse_argument(url, url.application_view)
            else:
                print(f"- Warning: Route ({url}) is not a URL nor MEDIA   [ROUTE IGNORED]")
    async def RetrieveView(self, url):
        try:
            async def asynchronous_asset(path_, importer):
                return HttpResponse(importer(path_))
            if url.split('/')[1] == 'media':
                path_ = url[url.find('/media/')+7:]
                return lambda _: asynchronous_asset(path_, ImportMedia)
            elif url.split('/')[1] == 'static':
                path_ = url[url.find('/static/')+8:]
                return lambda _: asynchronous_asset(path_, ImportStatic)
            else:
                url_parsed = urlparse(url)
                url_path = url_parsed.path
                if url_path[-1] in '\\/': url_path = url_path[:-1]
                url_query = {key: val for key, val in parse_qs(url_parsed.query).items()}
                if url_path in self.urls:
                    url_route = self.urls[url_path]
                    async def asynchronous_enhanced_response_holder(req):
                        return await enhanced_response_generation(
                        path=url_path, route=url_route,
                        query=url_query, param={}, req=req
                    )
                    return asynchronous_enhanced_response_holder
                else:
                    arg_url = self.seek_argument_urls(url)
                    if arg_url:
                        async def asynchronous_enhanced_response_holder(req):
                            return await enhanced_response_generation(
                            path=url_path, route=arg_url[0],
                            query=url_query, param=arg_url[1], req=req
                        )
                        return asynchronous_enhanced_response_holder
                    else: return False
        except:
            traceback.print_exc()
            print(f"[InfraWeb] GET Request - {url} - page not avaliable - {time.ctime()}")
            sys.exit()

class URL:
    def __init__(self, path, view):
        if path[-1] in '\\/': path = path[:-1]
        self.path = path
        self.application_view = view
