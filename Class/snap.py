import subprocess, requests, shutil, sys, os

class SNAP():

    def __init__(self,path):
        self.path = path
        with open(f'{self.path}/configs/config.json') as f: self.config = json.load(f)

    def update(self):
        subprocess.run("cd; git pull",shell=True)

    def reqFileID(self):
        try:
            req = requests.get(f"https://{self.config['endpoint']}/dir/assign", timeout=(5,5))
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