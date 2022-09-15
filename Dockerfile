FROM ubuntu:22.04 

COPY . /code 
WORKDIR /code

RUN apt update

# Install Python and dependencies
RUN apt install ffmpeg python3 python3-pip -y 
RUN pip3 install --no-cache-dir -r requirements.txt

# Weird fix for PYJWT encode error 
RUN pip uninstall PyJWT
RUN pip install --upgrade PyJWT==1.7.1

CMD [ "python3", "Zoom2YouTube.py"]