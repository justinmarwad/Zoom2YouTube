#!/bin/bash          

# DEPENDENCIES:
# 1. Zoom Meeting Downloader: https://github.com/tribloom/Zoom-Meeting-Download
# 2. YouTube  Uploader: https://github.com/porjo/youtubeuploader
# 3. FFMPEG 
# 4. Love and dedication 


## Setup vars ## 
eval $(cat secrets/.env)


INTRO="logo.mp4"
OUTRO="logo.mp4"
OUTPUT_DIR="final"

MY_SCRIPT_VARIABLE="${EMAIL}"


FROM="2022-09-12"
TO="2022-09-12"


# print_usage() {
#   printf "Usage: upload.sh..."
# }

# while getopts 'abf:v' flag; do
#   case "${flag}" in
#     a) a_flag='true' ;;
#     b) b_flag='true' ;;
#     f) files="${OPTARG}" ;;
#     v) verbose='true' ;;
#     *) print_usage
#        exit 1 ;;
#   esac
# done


## Install Dependencies ##
pip3 install jwt

if ! command -v ffmpeg &> /dev/null
then
    echo "[INFO] FFMPEG not installed, installing now..."
    apt install FFMPEG -y 
fi

## Download Latest Lectures From Zoom ##
echo "[INFO] Downloading latest Zoom lectures"
echo "python3 zoom_meeting_download.py -e $EMAIL --from $FROM --to $TO -s secrets/zoom_secrets.json" 
python3 zoom_meeting_download.py -e $EMAIL -f "$FROM" -t "$TO" -s secrets/zoom_secrets.json 

echo "[INFO] Done downloading Zoom lectures!"

## Loop Over All Lectures ##
echo "[INFO] Begin looping"

find recordings/ -type f -name '*.mp4' -print0 | 
while IFS= read -r -d '' FILE; do 
    
    OUTPUT=$OUTPUT_DIR/$(dirname "$FILE")$(basename "$FILE")
    OUTPUT=${OUTPUT// /_}
    
    ## Use FFMPEG To  Upscale And Add Intro/Outro ##
    echo "[INFO] Scaling $FILE to 1080p and appending $INTRO and $OUTRO to $OUTPUT_DIR/$(basename $FILE)"
    echo "[WARNING] Note: This will take some time."

    ffmpeg -i $INTRO -i "$FILE" -i $OUTRO -filter_complex "[0:v]setsar=1,fps=30000/1001,format=yuv420p[intro];[1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1,fps=30000/1001,format=yuv420p[video];[2:v]setsar=1,fps=30000/1001,format=yuv420p[outro];[0:a]aformat=sample_rates=48000:channel_layouts=stereo[introa];[1:a]aformat=sample_rates=48000:channel_layouts=stereo[videoa];[2:a]aformat=sample_rates=48000:channel_layouts=stereo[outroa];[intro][introa][video][videoa][outro][outroa]concat=n=3:v=1:a=1[vid][a]" -map "[vid]" -map "[a]" -movflags +faststart "$OUTPUT" < /dev/null
    
    ## And Upload To YouTube ##
    # echo "[INFO] Uploading $OUTPUT_DIR/$FILE to YouTube"
    # ./youtubeuploader -headlessAuth -filename "$OUTPUT" -title "$OUTPUT" -privacy "unlisted" -metaJSON "secrets/meta.json" -secrets "secrets/client_secrets-test.json" -cache "secrets/request.token"
done




