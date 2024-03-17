FROM nvidia/cuda:11.7.1-base-ubuntu22.04
WORKDIR /server
COPY requirements.txt .


RUN apt-get update
RUN apt-get -y install python3-pip
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000

RUN unset LD LD_LIBRARY_PATH

CMD ["python3", "det.py"]
CMD ["python3", "server.py"]
