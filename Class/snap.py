import subprocess, requests, shutil, json, time, sys, os

class SNAP():

    def __init__(self,path):
        self.path = path
        with open(f'{self.path}/configs/config.json') as f: self.config = json.load(f)
        if not os.path.isfile(f'{self.path}/configs/backups.json'): 
            with open(f'{self.path}/configs/backups.json', 'w') as f: json.dump({}, f)
        with open(f'{self.path}/configs/backups.json') as f: self.backups = json.load(f)
        self.headers = {"Basic":self.config['auth']}

    def update(self):
        subprocess.run("cd; git pull",shell=True)

    def reqFileID(self,ttl=None):
        try:
            reqUrl = f"https://{self.config['endpoint']}/dir/assign"
            if ttl: reqUrl += f"?ttl={ttl}"
            req = requests.get(reqUrl, timeout=(5,5), headers=self.headers)
            if req.status_code == 200: return r.json()
            print(f"Error got {req.status_code}")
        except Exception as ex:
            print(f"Error {ex}")
            return {}

    def uploadFile(self,file,fid):
        try:
            with open(file, 'rb') as f:
                req = requests.post(f"https://{self.config['endpoint']}/{fid}", data=f, headers=self.headers)
            if req.status_code == 200: return True
            print(f"Error got {req.status_code}")
        except Exception as ex:
            print(f"Error {ex}")

    def downloadFile(self,fid):
        try:
            with requests.get(f"https://{self.config['endpoint']}/{fid}", stream=True, headers=self.headers) as r:
                with open(fid, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            print(f"Error got {req.status_code}")
        except Exception as ex:
            print(f"Error {ex}")

    def deleteFile(self,fid):
        try:
            req = requests.delete(f"https://{self.config['endpoint']}/{fid}", timeout=(5,5), headers=self.headers)
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
                return       
        fileID = self.reqFileID(ttl)
        print(f"Uploading file as {fileID}")
        result = self.uploadFile(f'{self.path}/tmp/{container}Backup.tar.gz',fileID)
        if not result: return
        os.remove(f'{self.path}/tmp/{container}Backup.tar.gz')
        if not container in self.backups: self.backups[container] = []
        self.backups[container].append({"created":int(time.time()),"fileID":fileID})
        with open(f'{self.path}/configs/backups.json', 'w') as f: json.dump(self.backups, f)

    def restore(self,container):
        print(f"Restoring {container}")
        self.snapRestore(container,"")

    def setConfig(self,params):
        key, value = params[0],params[1]
        self.config[key] = value
        with open(f'{self.path}/configs/config.json', 'w') as f: json.dump(self.config,f,indent=4)