import subprocess, requests, shutil, json, time, datetime, sys, os

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
            return req.status_code,req.json()
        except Exception as ex:
            return 0,ex
        return 0,""

    def uploadFile(self,file,fid):
        try:
            with open(file, 'rb') as f:
                req = requests.post(f"https://{self.config['filer']}/{fid}", data=f, headers={'Content-Type': 'form/multipart'}, auth=(self.config['username'], self.config['password']))
            return req.status_code,""
        except Exception as ex:
            return 0,ex
        return 0,"Failed to upload file"

    def downloadFile(self,fileID):
        try:
            with requests.get(f"https://{self.config['filer']}/{fileID}", stream=True, auth=(self.config['username'], self.config['password'])) as r:
                with open(f'{self.path}/tmp/{fileID}.tar.gz', 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        f.write(chunk)
            return r.status_code,""
        except Exception as ex:
            return 0,ex
        return 0,"Failed to download file"

    def deleteFile(self,fileID):
        try:
            req = requests.delete(f"https://{self.config['filer']}/{fileID}", timeout=(5,5), auth=(self.config['username'], self.config['password']))
            if req.status_code == 200: return True
            return req.status_code,""
        except Exception as ex:
            return 0,ex
        return 0,"Failed to delete file"

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

    def snapRestore(self,container,backupFile,containerName):
        result = subprocess.run(f"{self.config['type']} image import {backupFile} --alias {container}Backup", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"{self.config['type']} launch {container}Backup {containerName}", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"{self.config['type']} image delete {container}Backup", shell=True)
        if result.returncode != 0: return False
        return True

    def create(self,params):
        if len(params) == 0: return False
        container, ttl = params[0], None
        if len(params) > 1: ttl = params[1]
        if not self.containerExists(container):
            print(f"{container} does not exists, unable to backup")
            return False
        if os.path.isfile(f'{self.path}/tmp/{container}Backup.tar.gz'):
            print(f"Found existing Backup for {container}")
        else: 
            print(f"Creating Backup for {container}")
            result = self.snapShot(container)
            if not result: 
                print(f"Failed to create Backup for {container}")
                return False       
        statusCode,message = self.reqFileID(ttl)
        assign = message
        if statusCode != 200:
            print(f"Error at requesting fileID {message}")
            return False
        print(f"Uploading file as {assign['fid']}")
        statusCode,message = self.uploadFile(f'{self.path}/tmp/{container}Backup.tar.gz',assign['fid'])
        if statusCode != 201:
            print(f"Error at uploading file {message}")
            return False
        print(f"Cleaning up")
        os.remove(f'{self.path}/tmp/{container}Backup.tar.gz')
        if not container in self.backups: self.backups[container] = []
        self.backups[container].append({"created":int(time.time()),"fileID":assign['fid']})
        with open(f'{self.path}/configs/backups.json', 'w') as f: json.dump(self.backups, f)
        print(f"Done")

    def backupsList(self,container):
        if container in self.backups:
            backups = self.backups[container]
            for backup in backups:
                print(datetime.datetime.fromtimestamp(backup['created']).strftime('%c'),backup['fileID'])
        else:
            print(f"Could not find {container} in backups")

    def download(self,fileID):
        if os.path.isfile(f'{self.path}/tmp/{fileID}.tar.gz'):
            print(f"{fileID} is already downloaded as {self.path}/tmp/{fileID}.tar.gz")
            return True
        print(f"Downloading file {fileID}")
        statusCode, message = self.downloadFile(fileID)
        if statusCode != 200:
            print(f"Error at downloading file {message}")
            return False
        print(f"File downloaded as {self.path}/tmp/{fileID}.tar.gz")
        return True

    def delete(self,fileID):
        print(f"Deleting file {fileID}")
        statusCode, message = self.deleteFile(fileID)
        if statusCode != 200:
            print(f"Error at deleting file {message}")
            return False
        print(f"{fileID} deleted")

    def containerExists(self,targetContainer):
        try:
            containersRaw = subprocess.check_output(f"{self.config['type']} list --format=json", shell=True).decode("utf-8")
        except Exception as ex:
            exit(f"Either incus is not installed or incorrect permissions.")
        containers = json.loads(containersRaw)
        for container in containers:
            if container['name'] == targetContainer: return True
        return False

    def restore(self,container,source="",target=""):
        targetContainer = target if target else container
        if self.containerExists(targetContainer):
            print(f"{targetContainer} exists, unable to restore")
            return False
        if source:
            print(f"Downloading {source}")
            response = self.download(source)
            latestBackup = {}
            latestBackup['fileID'] = source
        else:
            print(f"Downloading last backup for {container}")
            latestBackup = self.backups[container][len(self.backups[container]) -1]
            response = self.download(latestBackup['fileID'])
        if not response: return False
        print(f"Restoring {targetContainer}")
        response = self.snapRestore(container,f"{self.path}/tmp/{latestBackup['fileID']}.tar.gz",targetContainer)
        if not response:
            print(f"Failed to restore {targetContainer}")
            return False
        os.remove(f"{self.path}/tmp/{latestBackup['fileID']}.tar.gz")
        print(f"Restored {targetContainer}")

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
        with open(f'{self.path}/configs/config.json', 'w') as f: json.dump(self.config, f, indent=4)