# Justin Marwad 2022 
import os, subprocess, logging, colorama, pathlib, sys, base64
from multiprocessing import parent_process
import dateutil.parser as dparser
import requests, json
from datetime import datetime, timedelta
from dotenv import load_dotenv

from youtube_upload.client import YoutubeUploader

class Zoom2YouTube:
    def __init__(self, email=None, from_date=None, to_date=None, gpu_encode=False):
        # Load environment variables
        load_dotenv()

        if not from_date: 
            from_date = os.environ.get("FROM_DATE")
        if not to_date:
            to_date = os.environ.get("TO_DATE")
        if not email: 
            email = os.environ.get("EMAIL")
        
        ZOOM_ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID")
        ZOOM_CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID")
        ZOOM_CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET")
        self.ZOOM_MEETING_ID = os.environ.get("ZOOM_MEETING_ID")
        self.YOUTUBE_CLIENT_SECRETS="secrets/client_secrets.json" 

        # if from_date and to_date not set, set them to 7 days ago and today
        if not from_date: 
            one_week_ago = datetime.now() - timedelta(days=7)
            from_date = one_week_ago.strftime('%Y-%m-%d')
        if not to_date: 
            to_date = datetime.now().strftime('%Y-%m-%d')

        # Set variables
        self.email = email 
        self.from_date = from_date 
        self.to_date = to_date

        self.gpu_encode = gpu_encode

        self.ZOOM_ACCESS_TOKEN = self.create_zoom_access_token(ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
        self.save_downloads_location = "recordings"


    ## Utility methods ##
    def run(self, command, powershell=False):
        """ Base method. Runs command as well as prints to screen and logs to result file. """
        self.result(f"[RUN] {command}", colorama.Fore.YELLOW)
        if powershell: 
            return subprocess.run(["powershell", "-Command", command]) #, capture_output=True)
        else: 
            return subprocess.call(command, shell=True) #os.system(command)
    
    def result(self, output, color=colorama.Fore.GREEN): 
        """ Base method. Pretty print out results to terminal. """
        print(f"{color} {output} {colorama.Fore.RESET}")
        logging.info(output) 

    def uniquify(self, path):
        """ Make sure file name is unique. """
        filename, extension = os.path.splitext(path)
        counter = 1

        while os.path.exists(path):
            path = f"{filename}_{str(counter)}{extension}"
            counter += 1

        return path

    def create_zoom_access_token(self, ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET):
        """ Create a Zoom OAuth access token. """

        base64_encoded = base64.b64encode(f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}".encode()).decode()

        response = requests.request("POST", 
            "https://zoom.us/oauth/token", 
            headers={
                'Host': 'zoom.us',
                'Authorization': f'Basic {base64_encoded}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }, 
            data=f'grant_type=account_credentials&account_id={ZOOM_ACCOUNT_ID}'
        )
        
        response.raise_for_status()
        return response.json()['access_token']

    ## Main code ##
    def download_video(self, secrets="secrets/zoom_secrets.json"): 
        """ Download all zoom recordings from a given date range. """
        # self.run(f"python3 zoom_meeting_download.py -e {email} -f {self.from_date} -t {self.to_date} -s {secrets}")


        # Download each recording 
        response = requests.get( 
            url=f'https://api.zoom.us/v2/users/{self.email}/recordings?from={self.from_date}&to={self.to_date}', 
             headers={'Authorization': f'Bearer {self.ZOOM_ACCESS_TOKEN}'}, 
         
        )
        
        response.raise_for_status()
        meetings = response.json()["meetings"]

        # Download the recordings
        for meeting in meetings: 
            for file in meeting["recording_files"]:
                if file["file_type"] == "MP4":
                    download_url = file["download_url"]
                    save_place = f"{self.save_downloads_location}/{file['recording_start']}.mp4"

                    self.result(f"[+] Found recording on {file['recording_start']} to {file['recording_end']} at the location '{download_url}' and saving to '{save_place}'")

                    response = requests.get(download_url)
                    with open(save_place, "wb") as f:
                        f.write(response.content)

    def edit_video(self, intro_video="logo.mp4", outro_video="logo.mp4", final_video=None):
        """ Edit video with intro and outro. """

        for root, dirs, files in os.walk("recordings"):
            for video in files:
                if video.endswith(".mp4"):                   
                    video_path = os.path.join(root, video)
                    date = datetime.strptime(video, "%Y-%m-%dT%H:%M:%SZ.mp4")
                    date = date.strftime("%Y-%m-%dT%H:%M:%SZ")   

                    # if date >= self.from_date and date <= self.to_date:

                    self.result(f"Editing {video}")
                    
                    # if final_video is None: 
                    final_video = f"final/final_{date}.mp4"

                    gpu_encode_flags = ""
                    if self.gpu_encode: 
                        # gpu_encode_flags = "-hwaccel cuda -hwaccel_output_format cuda -c:v h264_nvenc"    
                        gpu_encode_flags = "-hwaccel cuda"    
                        

                    self.run(f"""ffmpeg {gpu_encode_flags} -i {intro_video} -i "{video_path}" -i {outro_video} -filter_complex '[0:v]setsar=1,fps=30000/1001,format=yuv420p[intro];[1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1,fps=30000/1001,format=yuv420p[video];[2:v]setsar=1,fps=30000/1001,format=yuv420p[outro];[0:a]aformat=sample_rates=48000:channel_layouts=stereo[introa];[1:a]aformat=sample_rates=48000:channel_layouts=stereo[videoa];[2:a]aformat=sample_rates=48000:channel_layouts=stereo[outroa];[intro][introa][video][videoa][outro][outroa]concat=n=3:v=1:a=1[vid][a]' -map '[vid]' -map '[a]' -movflags +faststart {final_video} < /dev/null""")

                    self.result(f"Finished editing {video}")
                    self.run(f"rm {video_path}")
                    self.result(f"Removed {video}")

                    # else: 
                    #     self.result("[-] ERROR: No videos with dates that match. Skipping editing.", colorama.Fore.RED)

    def upload_video(self, video, privacy="private"):
        """ Upload video to YouTube. """

        uploader = YoutubeUploader(secrets_file_path=self.YOUTUBE_CLIENT_SECRETS)
        uploader.authenticate()

        # Video options
        options = {
            "title" : f"{video} | Title ", # The video title
            "description" : "Description", # The video description
            # "tags" : ["tag1", "tag2", "tag3"],
            # "categoryId" : "22",
            "privacyStatus" : "private", # "public", "private", or "unlisted"
            "kids" : False, # Specifies if the Video if for kids or not. Defaults to False.
            # "thumbnailLink" : "https://awebsite/animage.jpg" # Optional. Specifies video thumbnail.
        }

        # upload video
        uploader.upload(video, options) 



if __name__ == "__main__":

    print("[INFO] Zoom2YouTube. Download, edit, and upload Zoom recordings to YouTube.") 
    z2y = Zoom2YouTube(gpu_encode=False)
    
    # print("[INFO] Downloading recordings from Zoom.")
    z2y.download_video()
    
    # print("[INFO] Editing recordings.")
    z2y.edit_video()

    # print("[INFO] Uploading recordings.")
    # z2y.upload_video()
