FROM nyumotorsportstelemetryorg/mercury

# RUN mkdir /hardware
RUN sudo apt-get update && apt --fix-broken install -y
# install common build dependencies and clean up afterwards
RUN sudo apt-get install -y --no-install-recommends \ 
 # RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends \
 # RUN sudo apt-get update && sudo apt-get install -y \
#     sense-hat \
    # python3-numpy \
    # python3-pil \
    # python3-pkg-resources \
    # dconf-gsettings-backend \
    # python3-gi \
    # python3-gi-cairo \
    # idle3 \
    python3-sense-emu \
    sense-emu-tools \
    # aptitude \
    && rm -rf /var/lib/apt/lists/*
    # && sudo aptitude install python3-sense-emu \
    # sense-emu-tools

# WORKDIR /hardware
# install required python packages
COPY ./pi_requirements.txt .
RUN sudo python3 -m pip install pip --upgrade --force
RUN sudo pip3 install -r pi_requirements.txt

COPY . hardware/

# might want to create a hardware-specific requirements.txt for stuff we need to run that

CMD ["python3", "-m", "hardware.main"]