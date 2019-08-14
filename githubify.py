import os
from string import Template

EXCLUDE_INDEXES = ('Context', 'ClassDefinitions', 'Ontology')
FILE_REDIRECT_TEMPLATE = Template('''---
redirect_to: "$redirect_to"
---
''')

if __name__ == "__main__": 
    for (root,dirs,files) in os.walk('v1', topdown=True):
        dir_name = os.path.split(root)[-1]
        if dir_name != '' and dir_name not in EXCLUDE_INDEXES:
                 with open(os.path.join(root, 'index.md'), 'w') as f:
                     f.write(FILE_REDIRECT_TEMPLATE.substitute(redirect_to=os.path.join(root, '..', dir_name+'.jsonld')))

        file_names = map(lambda x: os.path.splitext(x)[0], files)
        for fname in file_names:
            if fname not in dirs:
                with open(os.path.join(root, fname+'.md'), 'w') as f:
                    f.write(FILE_REDIRECT_TEMPLATE.substitute(redirect_to=os.path.join(root, fname+'.jsonld')))
