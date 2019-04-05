import ast
import os
import yaml


def stub_out(func, file):
    """This function creates the default function stubs"""
    with open(file, "a") as myfile:
        text = """
def %s(event, context):
    response = dict(statusCode=501, body="")
    return response

""" % (func)
        myfile.write(text)


# Read in the serverless.yml file and find all the functions and files that should exist
f = ""
with open("serverless.yml", 'r') as stream:
    f = yaml.full_load(stream)

function_handlers = [f['functions'][x]['handler'] for x in f['functions']]

# Construct the file names we're looking for
filenames = []
for file in function_handlers:
    filenames.append((file.split('.')[1], os.path.join(os.getcwd() + "/" +
                                                       file.split('.')[0] +
                                                       '.py')))

# Make sure the files we need exist, and create them if they are missing
for tup in filenames:
    os.makedirs(os.path.dirname(tup[1]), exist_ok=True)
    if not os.path.exists(tup[1]):
        print("Creating "+ os.path.relpath(tup[1], os.getcwd()))
        with open(tup[1], 'w'): pass

# Make sure the functions exist in the files
for tup in filenames:
    with open(tup[1]) as fd:
        file_contents = fd.read()
    module = ast.parse(file_contents)
    function_definitions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    if tup[0] in [f.name for f in function_definitions]:
        print("Found " + tup[0] + " in " + os.path.relpath(tup[1], os.getcwd()))
    else:
        print("Did not find " + tup[0] + " in " + os.path.relpath(tup[1], os.getcwd()) + ", stubbing out")
        stub_out(tup[0], tup[1])
        print("Stubbed out " + tup[0] + " in " + os.path.relpath(tup[1], os.getcwd()))

# Check for extra files
files_should_exisit = [tup[1] for tup in filenames]
files_that_exist = []
exclude_dirs = set([".serverless", "__pycache__", "lib"])
exclude_files = set(["serverless.yml", "requirements.txt", "package.json", "__init__.py"])
for root, dirs, files in os.walk(os.getcwd(), topdown=True):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    files[:] = [f for f in files if f not in exclude_files]
    for file in files:
        files_that_exist.append((os.path.join(root, file)))

for x in [x for x in files_that_exist if x not in files_should_exisit]:
    print("File " + os.path.relpath(x, os.getcwd()) + " may be unnecessary")
