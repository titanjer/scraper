import os
import re
from collections import OrderedDict


def read_env(**variables):
    """ Reads local default environment variables from a .env file
    located in the project root directory.

    """
    try:
        with open('.env') as f:
            content = f.read()
    except IOError:
        content = ''

    env_dict = OrderedDict()

    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)
            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)
            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))
            os.environ.setdefault(key, val)
            env_dict[key] = val

    env_dict.update(variables)

    return env_dict


def read_variable(var, error_string=None, default=None, auto_convert=True):
    """ Safe way to read env. variables
        auto_convert option trying to convert variable into
        integer or boolean or string
    """
    env_variable = os.environ.get(var)
    if env_variable is None:
        if default is not None:
            return default
        else:
            if error_string is None:
                raise Exception("{} not defined".format(env_variable))
            else:
                raise Exception(error_string)

    def convert(variable):
        convert_var = None
        # try to integer
        try:
            convert_var = int(variable)
        except ValueError:
            pass
        else:
            return convert_var
        # try to boolean
        if variable in ['True', 'true', 'False', 'false']:
            if variable in ['True', 'true']:
                return True
            else:
                return False
        # or return string
        return str(variable)

    if auto_convert is True:
        return convert(env_variable)
    else:
        return env_variable


def load_env_variables():
    env_vars = read_env()
    for key, val in env_vars.items():
        env_vars[key] = read_variable(key, default=val)
    return env_vars
