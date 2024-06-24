import subprocess, requests, shutil, json, time, sys, os

class SNAP():

    def __init__(self,path):
        self.path = path
        with open(f'{self.path}/configs/config.json') as f: self.config = json.load(f)
        if not os.path.isfile(f'{self.path}/configs/backups.json'): 
            with open(f'{self.path}/configs/backups.json', 'w') as f: json.dump({}, f)
        with open(f'{self.path}/configs/backups.json') as f: self.backups = json.load(f)

    def update(self):
        subprocess.run("cd; git pull",shell=True)

    def reqFileID(self,ttl=None):
        try:
            reqUrl = f"https://{self.config['master']}/dir/assign"
            if ttl: reqUrl += f"?ttl={ttl}"
            req = requests.get(reqUrl, timeout=(5,5), auth=(self.config['username'], self.config['password']))
            if req.status_code == 200: return req.json()
            print(f"Error got {req.status_code}")
        except Exception as ex:
            print(f"Error {ex}")
            return {}

    def uploadFile(self,file,fid):
        try:
            with open(file, 'rb') as f:
                req = requests.post(f"https://{self.config['filer']}/{fid}", data=f, auth=(self.config['username'], self.config['password']))
            if req.status_code == 200: return True
            print(f"Error got {req.status_code}")
        except Exception as ex:
            print(f"Error {ex}")

    def downloadFile(self,fid):
        try:
            with requests.get(f"https://{self.config['filer']}/{fid}", stream=True, auth=(self.config['username'], self.config['password'])) as r:
                with open(fid, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            print(f"Error got {req.status_code}")
        except Exception as ex:
            print(f"Error {ex}")

    def deleteFile(self,fid):
        try:
            req = requests.delete(f"https://{self.config['filer']}/{fid}", timeout=(5,5), auth=(self.config['username'], self.config['password']))
            if req.status_code == 200: return True
            print(f"Error got {req.status_code}")
        except Exception as ex:
            print(f"Error {ex}")

    def snapShot(self,container):
        result = subprocess.run(f"{self.config['type']} snapshot create {container} {container}Backup", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"{self.config['type']} publish {container}/{container}Backup --alias {container}Backup", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"{self.config['type']} image export {container}Backup /opt/lxcSnap/tmp/{container}Backup", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"{self.config['type']} image delete {container}Backup", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"{self.config['type']} snapshot delete {container} {container}Backup", shell=True)
        if result.returncode != 0: return False
        return True

    def snapRestore(self,container,backupFile):
        result = subprocess.run(f"{self.config['type']} image import {backupFile} --alias {container}Backup", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"{self.config['type']} launch {container}Backup {container}", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"{self.config['type']} image delete {container}Backup", shell=True)
        if result.returncode != 0: return False
        return True

    def create(self,params):
        if len(params) == 0: return False
        container, ttl = params[0], None
        if len(params) > 1: ttl = params[1]
        if os.path.isfile(f'{self.path}/tmp/{container}Backup.tar.gz'):
            print(f"Found existing Backup for {container}")
        else: 
            print(f"Creating Backup for {container}")
            result = self.snapShot(container)
            if not result: 
                print(f"Failed to create Backup for {container}")
                return False       
        response = self.reqFileID(ttl)
        if not response:
            print(f"Failed to get fileID for {container}")
            return False
        print(f"Uploading file as {response['fid']}")
        result = self.uploadFile(f'{self.path}/tmp/{container}Backup.tar.gz',response['fid'])
        if not result: return
        print(f"Cleaning up")
        os.remove(f'{self.path}/tmp/{container}Backup.tar.gz')
        if not container in self.backups: self.backups[container] = []
        self.backups[container].append({"created":int(time.time()),"fileID":response['fid']})
        with open(f'{self.path}/configs/backups.json', 'w') as f: json.dump(self.backups, f)
        print(f"Done")

    def restore(self,container):
        print(f"Restoring {container}")
        self.snapRestore(container,"")

    def setConfig(self,params):
        key, value = params[0],params[1:]
        if key == "auth":
            self.config["username"] = value[0]
            self.config["password"] = value[1]
        elif key == "endpoint":
            if len(value) > 1:
                self.config['master'] = value[0]
                self.config['filer'] = value[1]
            else:
                self.config['master'] = value[0]
                self.config['filer'] = value[0]
        else:
            self.config[key] = value[0]
        with open(f'{self.path}/configs/config.json', 'w') as f: json.dump(self.config,f,indent=4)