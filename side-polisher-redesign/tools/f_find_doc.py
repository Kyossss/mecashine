import adsk.core
def run(_c):
    app = adsk.core.Application.get()
    for p in app.data.dataProjects:
        def walk(folder, path, depth):
            for f in folder.dataFiles:
                if 'conveyor' in f.name.lower() or 'asps' in f.name.lower() or 'mecashine' in f.name.lower():
                    print(p.name, '|', path + f.name, '| v', f.versionNumber, '| id', f.id)
            if depth < 3:
                for sf in folder.dataFolders: walk(sf, path + sf.name + '/', depth + 1)
        try: walk(p.rootFolder, '', 0)
        except Exception as e: print('skip', p.name, e)
