import datetime, traceback
import sqlite3 as sql
import pathlib, os
import inspect

# the database databse handling unit [models-based system]

DATABASES_IN_USE = dict()

class __WHERE_STATEMENT:
    def __getitem__(self, params):
        if type(params) != 'str':
            return params
        else: raise ValueError(
            "[InfraWeb] Unable to parse your query."
        )

class __WHERE_FRAGMENT:
    def __and__(self, data_):
        self.data = f"({self.data} AND {data_.data})"
        self.val = self.val + data_.val
        return self
    def __or__(self, data_):
        self.data = f"({self.data} OR {data_.data})"
        return self
    def __init__(self, data):
        self.val = []
        self.data = data

_FIELD__WHERE_FRAGMENT = __WHERE_FRAGMENT

class __FIELD:
    where_fragment = __WHERE_FRAGMENT
    def __hash__(self):
        return id(self)
    def __eq__(self, param):
        result = self.where_fragment(f'({self.__fieldname__} = ?)')
        result.val.append(param)
        return result

    def __ne__(self, param):
        result = self.where_fragment(f'({self.__fieldname__} != ?)')
        result.val.append(param)
        return result

    def __lt__(self, param):
        result =  self.where_fragment(f'({self.__fieldname__} < ?)')
        result.val.append(param)
        return result

    def __le__(self, param):
        result = self.where_fragment(f'({self.__fieldname__} <= ?)')
        result.val.append(param)
        return result

    def __ne__(self, param):
        result = self.where_fragment(f'({self.__fieldname__} != ?)')
        result.val.append(param)
        return result
    
    def __ge__(self, param):
        result = self.where_fragment(f'({self.__fieldname__} >= ?)')
        result.val.append(param)
        return result
    
    def __gt__(self, param):
        result = self.where_fragment(f'({self.__fieldname__} > ?)')
        result.val.append(param)
        return result

class __NULL: val = None
NULL = __NULL()
class __CASCADE: val = "CASCADE"
CASCADE = __CASCADE()
class __NO_ACTION: val = "NO ACTION"
NO_ACTION = __NO_ACTION()
class __STRICT: val = "STRICT"
STRICT = __STRICT()
class __DEFAULT_VALUE: val = "DEFAULT"
DEFAULT_VALUE = __DEFAULT_VALUE()
class SET:
    def __init__(self, value):
        self.val = f"SET {value}"

Where = __WHERE_STATEMENT()

class CharField(__FIELD):
    def __init__(self, max_length:int=250, choices:list=None, allow_null:bool=False, primary_key:bool=False, default=None, unique:bool=False):
        if(not isinstance(max_length,int))or(50_000_000<max_length)or(max_length<1):
            raise ValueError(
                "[InfraWeb] max_length should be an integer between (1-50,000,000)."
            )
        else: self.max_length = max_length
        if choices:
            if isinstance(choices, dict):
                if len(choices) < 2:
                    raise ValueError(
                        "[InfraWeb] The dictionary of choices the choices should contain at least two values."
                    )
                else:
                    for val in choices:
                        if not isinstance(val, str):
                            raise ValueError(
                                "[InfraWeb] The keys of the choices dictionary should be string values."
                            )
                        self.choices = choices
            else: raise ValueError(
                "[InfraWeb] The choices argument should be a dictionary"
            )
        else:
            self.choices = None
        if allow_null in [True, 1]:
            self.allow_null = True
        else:
            self.allow_null = False
        if primary_key in [True, 1]:
            self.primary_key = True
        else:
            self.primary_key = False
        if unique in [True, 1]:
            self.unique = True
        else:
            self.unique = False
        if default != None:
            self.default = default.__str__()
        else:
            self.default = None

class IntegerField(__FIELD):
    def __init__(self, allow_null:bool=False, primary_key:bool=False, default=None, unique:bool=False):
        if allow_null in [True, 1]:
            self.allow_null = True
        else:
            self.allow_null = False
        if primary_key in [True, 1]:
            self.primary_key = True
        else:
            self.primary_key = False
        if unique in [True, 1]:
            self.unique = True
        else:
            self.unique = False
        if default != None:
            if isinstance(default, int):
                self.default = default
            else:
                raise ValueError(
                    "[InfraWeb] The default value should be integer."
                )
        else: self.default = None

class AutoField(__FIELD):
    def __init__(self, primary_key:bool=False, unique:bool=False):
        if primary_key in [True, 1]:
            self.primary_key = True
        else:
            self.primary_key = False
        if unique in [True, 1]:
            self.unique = True
        else:
            self.unique = False

class BooleanField(__FIELD):
    def __init__(self, allow_null:bool=False, default=None):
        if allow_null in [True, 1]:
            self.allow_null = True
        else:
            self.allow_null = False
        if default:
            if isinstance(default, bool):
                if default == True: self.default = True
                else: self.default = False
            else: raise ValueError(
                "[InfraWeb] The default value should be bool."
            )
        else:
            self.default = None

class DateField(__FIELD):
    def __init__(self, auto_now_created:bool=False, auto_now_modified:bool=False, allow_null:bool=False, default:datetime.date=None):
        if auto_now_created in [True, 1]:
            self.auto_now_created = True
        else: self.auto_now_created = False
        if auto_now_modified in [True, 1]:
            self.auto_now_modified = True
        else: self.auto_now_modified = False
        if auto_now_created and auto_now_modified:
            raise AssertionError(
                "[InfraWeb] You could choose either auto_now_create or auto_now_modified but not both."
            )
        if default != None:
            if type(default) == "<class 'datetime.date'>":
                self.default = default
            else: raise ValueError(
                "[InfraWeb] The default value should be datetime.date object."
            )
        else:
            self.default = None
        if allow_null in [True, 1]:
            if auto_now_created or auto_now_modified:
                raise ValueError(
                    "[InfraWeb] cannot set allow_null to True with auto_now_created or auto_now_modified." # FIXME Message
                )
            else: self.allow_null = True
        else: self.allow_null = False

class DateTimeField(__FIELD):
    def __init__(self, auto_now_created:bool=False, auto_now_modified:bool=False, allow_null:bool=False, default:datetime.datetime=None):
        if auto_now_created in [True, 1]:
            self.auto_now_created = True
        else: self.auto_now_created = False
        if auto_now_modified in [True, 1]:
            self.auto_now_modified = True
        else: self.auto_now_modified = False
        if auto_now_created and auto_now_modified:
            raise AssertionError(
                "[InfraWeb] You could choose either auto_now_create or auto_now_modified but not both."
            )
        if allow_null in [True, 1]:
            if auto_now_created or auto_now_modified:
                raise ValueError(
                    "[InfraWeb] cannot set allow_null to True with auto_now_created or auto_now_modified."
                )
            else:
                self.allow_null = True
        else:
            self.allow_null = False
        if default != None:
            if type(default) == "<class 'datetime.datetime'>":
                self.default = default
            else: raise ValueError(
                "[InfraWeb] The default value should be datetime.datetime object."
            )
        else:
            self.default = None

class TimeField(__FIELD):
    def __init__(self, auto_now_created:bool=False, auto_now_modified:bool=False, allow_null:bool=False, default:datetime.time=None):
        if auto_now_created in [True, 1]:
            self.auto_now_created = True
        else: self.auto_now_created = False
        if auto_now_modified in [True, 1]:
            self.auto_now_modified = True
        else: self.auto_now_modified = False
        if auto_now_created and auto_now_modified:
            raise AssertionError(
                "[InfraWeb] You could choose either auto_now_create or auto_now_modified but not both."
            )
        if allow_null in [True, 1]:
            if auto_now_created or auto_now_modified:
                raise ValueError(
                    "[InfraWeb] cannot set allow_null to True with auto_now_created or auto_now_modified."
                )
            else:
                self.allow_null = True
        else: self.allow_null = False
        if default != None:
            if type(default) == "<class 'datetime.time'>":
                self.default = default
            else: raise ValueError(
                "[InfraWeb] The default value should be datetime.time object."
            )
        else:
            self.default = None

class DecimalField(__FIELD):
    def __init__(self, max_digits:int=None, decimal_places:int=None, allow_null:bool=False, unique:bool=False, default:float=None):
        if (not isinstance(max_digits, int))or(not isinstance(decimal_places, int)):
            if ((max_digits == None)and(decimal_places != None))or((max_digits != None)and(decimal_places == None)):
                raise ValueError(
                    "[InfraWeb] max_digits and decimal_places should be assigned together"
                )
            raise ValueError(
                "[InfraWeb] max_digits and decimal_places should be integer values."
            )
        else:
            if isinstance(max_digits, int) and isinstance(decimal_places, int):
                self.max_digits = max_digits
                self.decimal_places = decimal_places
            else:
                raise ValueError(
                    "[InfraWeb] Error assigning DecimalField."
                )
        if default != None:
            if type(default) == "<class 'float'>":
                self.default = default
            else: raise ValueError(
                "[InfraWeb] The default value should be float."
            )
        else:
            self.default = None
        if allow_null in [True, 1]:
            self.allow_null = True
        else:
            self.allow_null = False
        if unique in [True, 1]:
            self.unique = True
        else:
            self.unique = False

class FilePathField(__FIELD):
    def __init__(self, allow_null:bool=False, primary_key:bool=False, default=None, unique:bool=False):
        if allow_null in [True, 1]:
            self.allow_null = True
        else:
            self.allow_null = False
        if primary_key in [True, 1]:
            self.primary_key = True
        else:
            self.primary_key = False
        if unique in [True, 1]:
            self.unique = True
        else:
            self.unique = False
        if default != None:
            if isinstance(default, pathlib.Path):
                self.default = default.__str__()
            else:
                raise ValueError(
                    "[InfraWeb] The default value should be a pathlib.Path object."
                )
        else: self.default = None

class ForeignKey(__FIELD):
    def __init__(self, to_table, on_delete=CASCADE, allow_null:bool=True, unique:bool=False):
        self.to_table = to_table
        if allow_null in [False, 0]:
            self.allow_null = False
        else:
            self.allow_null = True
        if unique in [False, 0]:
            self.unique = False
        else:
            self.unique = True
        if type(on_delete).__name__[2:] in ['SET', 'STRICT', 'NO_ACTION', 'CASCADE']:
            self.on_delete = on_delete
        else:
            raise ValueError(
            "[InfraWeb] Invalid on_delete value."
        )

class __Application_Database:
    initiated = False
    padding_name = lambda _, num: ("0"*(4-len(num.__str__())))+str(num)
    def Initiate_database(self, database_path):
        self.database_path = database_path
        if not self.initiated:
            self.db = sql.connect(database_path)
            self.initiated = True
    def drop_db(self):
        f = open(self.database_path, 'wb')
        f.write(b''); f.close()
    def load_queries(self):
        dirs = os.listdir(os.path.join(pathlib.Path(self.database_path).parent, 'assets', 'database_schemas'))
        schema_count = 0
        for dir_ in dirs:
            try:
                num = int(dir_.split('_')[-1].split('.')[0])
                if num > schema_count: schema_count = num
            except:pass
        f = open(os.path.join(pathlib.Path(self.database_path).parent, 'assets', 'database_schemas', f'schema_{self.padding_name(schema_count)}.sql'), 'r')
        data = f.read()
        f.close()
        # Slice:
        data = '["""' + data
        data = data.replace("\n\n", '""","""')
        data += '"""]'
        return eval(data)

    def loading_tbls(self):
        try:
            cur = self.db.cursor()
            failures = []; count = 1
            for query in self.load_queries():
                try:
                    cur.execute(query)
                    self.db.commit()
                except Exception as e: failures.append([query, e, count])
                count += 1

            for i in failures:
                print(f"""\n({i[2]}) [{i[1]}]{i[0]}\n""")
            cur.close()
            self.db.close()
        except:
            traceback.print_exc()
            print("[Server][SQL_Database] loading tables error!")

_Model__Application_Database = __Application_Database

def UpdateSchema(database_path):
    ApplicationDatabase = __Application_Database()
    ApplicationDatabase.Initiate_database(database_path)
    ApplicationDatabase.drop_db()
    ApplicationDatabase.loading_tbls()
    print('[InfraWeb] Database Schema updated.')

MODEL_ACTIONS_LOOKUP_TABLE = dict()
FIELDS_NAMES_LIST = [
    'ForeignKey', 'DecimalField','TimeField', 
    'DateTimeField','DateField', 'BoolanField',
    'AutoField', 'IntegerField','CharField',
]

def analize_dictionaries(dict_:dict):
    result = dict()
    for key, val in dict_.items():
        if type(key).__name__ in FIELDS_NAMES_LIST:
            result[key.__fieldname__] = val
        elif type(key).__name__ == 'str': result[key] = val
        else: raise ValueError(
            f"[InfraWeb] Invalid value: {key}"
        )
    return result

def get_class_file_location(obj):
    if hasattr(obj, '__class__'):
        class_obj = obj.__class__
        return inspect.getfile(class_obj)
    else:
        return None

class Model:
    def __init__(self):
        models_path = get_class_file_location(self)
        database_path = os.path.join(pathlib.Path(models_path).parent, 'sqlite3')
        if database_path in DATABASES_IN_USE:
            self.database = DATABASES_IN_USE[database_path]
        else:
            self.database = __Application_Database()
            self.database.Initiate_database(database_path)
            DATABASES_IN_USE[database_path] = self.database
        self.fields = dict()
        self.ExtractFields()

    def ExtractFields(self):
        for obj_name in dir(self):
            obj_value = self.__getattribute__(obj_name)
            if type(obj_value).__name__ in FIELDS_NAMES_LIST:
                self.fields[obj_name] = obj_value
                obj_value.__fieldname__ = obj_name
        self.__modelname__ = type(self).__name__
        self.fields_names = list(self.fields.keys())

    def Update(self, data, where=None):
        data = analize_dictionaries(data)
        table = self.__modelname__
        S = 'SET'; W = ''; params = []
        for key in data:
            val = data[key]; params.append(val)
            S+=f" {key} = ?,"
        if where:
            W = f'WHERE {where.data}'
            for val in where.val:
                params.append(val)
        query = f"""UPDATE {table}\n{S[:-1]}\n{W};"""
        cur = self.database.db.cursor()
        cur.execute(query, tuple(params))
        self.database.db.commit(); cur.close()

    def Insert(self, data):
        data = analize_dictionaries(data)
        table = self.__modelname__
        key = (str(list(data.keys())).replace('"', '')).replace("'", '')
        val = list(data.values())
        cur = self.database.db.cursor()
        cur.execute(f'''INSERT INTO {table} ({key[1:-1]})\nVALUES ({("?,"*len(val))[:-1]});''', tuple(val))
        self.database.db.commit()
        id_ = cur.lastrowid
        cur.close()
        return id_

    def Delete(self, where=None):
        table = self.__modelname__
        cur = self.database.db.cursor()
        if where: cur.execute(f'DELETE FROM {table} WHERE {where.data};', tuple(where.val))
        else: cur.execute(f'TRUNCATE TABLE {table};')
        self.database.db.commit()
        cur.close()

    def Check(self, where=None, fetch=None, columns=None):
        if columns == None:
            columns = self.fields_names
        table = self.__modelname__
        W = ''
        if where: W = f'WHERE {where.data}'
        if isinstance(fetch, int): L = f'LIMIT {fetch}'
        else: L = ''
        cur = self.database.db.cursor()
        if where: cur.execute(f"""SELECT {str(columns)[1:-1].replace('"', '').replace("'", '')} FROM {table}\n{W}\n{L};""", where.val)
        else: cur.execute(f"""SELECT {str(columns)[1:-1].replace('"', '').replace("'", '')} FROM {table}\n{W}\n{L};""")
        self.database.db.commit()
        if fetch: response = cur.fetchall(); cur.close(); return response
        else: response = bool(cur.fetchone()); cur.fetchall(); cur.close(); return response
