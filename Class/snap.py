import subprocess, requests, shutil, sys, os

class SNAP():

    def __init__(self,path):
        self.path = path
        with open(f'{self.path}/configs/config.json') as f: self.config = json.load(f)

    def update(self):
        subprocess.run("cd; git pull",shell=True)

    def reqFileID(self,ttl=None):
        try:
            reqUrl = f"https://{self.config['endpoint']}/dir/assign"
            if ttl: reqUrl += f"?ttl={ttl}"
            req = requests.get(reqUrl, timeout=(5,5))
            if req.status_code == 200: return r.json()
        except Exception as ex:
            print(f"Error {ex}")
            return {}

    def uploadFile(self,file,fid):
        try:
            with open(file, 'rb') as f:
                req = requests.post(f"https://{self.config['endpoint']}/{fid}", data=f)
            if req.status_code == 200: return True
        except Exception as ex:
            print(f"Error {ex}")

    def downloadFile(self,fid):
        try:
            with requests.get(f"https://{self.config['endpoint']}/{fid}", stream=True) as r:
                with open(fid, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
        except Exception as ex:
            print(f"Error {ex}")

    def deleteFile(self,fid):
        try:
            req = requests.delete(f"https://{self.config['endpoint']}/{fid}", timeout=(5,5))
            if req.status_code == 200: return True
        except Exception as ex:
            print(f"Error {ex}")

    def snapShot(self,container):
        result = subprocess.run(f"incus snapshot {container} backup", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"incus publish {container}/backup --alias {container}Backup", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"incus image export {container}Backup .", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"incus image delete {container}Backup", shell=True)
        if result.returncode != 0: return False
        return True

    def snapRestore(self,container,backupFile):
        result = subprocess.run(f"incus image import {backupFile} --alias {container}Backup", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"incus launch {container}Backup {container}", shell=True)
        if result.returncode != 0: return False
        result = subprocess.run(f"incus image delete {container}Backup", shell=True)
        if result.returncode != 0: return False
        return True