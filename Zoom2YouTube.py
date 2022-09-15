# Justin Marwad 2022 
import os, subprocess, logging, colorama  

class Zoom2YouTube:
    def __init__(self, email): 
        self.email = email 


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
            path = filename + " (" + str(counter) + ")" + extension
            counter += 1

        return path

    ## Main code ##
    def download_video(self, from_date, to_date, secrets="secrets/zoom_secrets.json"): 
        """ Download all zoom recordings from a given date range. """
        self.run(f"python3 zoom_meeting_download.py -e {email} -f {from_date} -t {to_date} -s {secrets}")

    def edit_video(self, intro_video="logo.mp4", outro_video="logo.mp4", final_video=None):
        """ Edit video with intro and outro. """
        if final_video is None: 
            final_video = self.uniquify("final/final.mp4")


        for root, dirs, files in os.walk("recordings"):
            for video in files:
                if video.endswith(".mp4"):
                    self.result(f"Editing {video}")
                    video_path = os.path.join(root, video) 
                    self.run(f"""ffmpeg -i {intro_video} -i "{video_path}" -i {outro_video} -filter_complex '[0:v]setsar=1,fps=30000/1001,format=yuv420p[intro];[1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1,fps=30000/1001,format=yuv420p[video];[2:v]setsar=1,fps=30000/1001,format=yuv420p[outro];[0:a]aformat=sample_rates=48000:channel_layouts=stereo[introa];[1:a]aformat=sample_rates=48000:channel_layouts=stereo[videoa];[2:a]aformat=sample_rates=48000:channel_layouts=stereo[outroa];[intro][introa][video][videoa][outro][outroa]concat=n=3:v=1:a=1[vid][a]' -map '[vid]' -map '[a]' -movflags +faststart {final_video} < /dev/null""")

                    self.result(f"Finished editing {video}")
                    # self.run(f"rm {video}")
                    # self.result(f"Removed {video}")

    def upload_video(self, video, privacy="unlisted", meta_token="secrets/meta.json", client_secrets="secrets/client_secrets.json", request_token="secrets/request_token.json"):
        """ Upload video to YouTube. """
        self.run(f"./youtubeuploader -headlessAuth -filename '{video}' -title '{video}' -privacy '{privacy}' -metaJSON '{meta_token}' -secrets '{client_secrets}' -cache '{request_token}'")


if __name__ == "__main__":
    if os.environ["EMAIL"]:
        email = os.environ["EMAIL"] 

    print("[INFO] Zoom2YouTube. Download, edit, and upload Zoom recordings to YouTube.") 
    z2y = Zoom2YouTube(email)
    
    print("[INFO] Downloading recordings from Zoom.")
    z2y.download_video("2022-09-12", "2022-09-12")
    
    print("[INFO] Editing recordings.")
    z2y.edit_video()

    # print("[INFO] Uploading recordings.")
    # z2y.upload_video()
