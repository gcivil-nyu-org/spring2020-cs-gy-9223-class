FROM nyumotorsportstelemetryorg/mercury

# RUN mkdir /hardware

# WORKDIR /hardware
# install required python packages
COPY ./pi_requirements.txt .
RUN sudo python3 -m pip install pip --upgrade --force
RUN sudo pip3 install -r pi_requirements.txt

COPY . hardware/

# might want to create a hardware-specific requirements.txt for stuff we need to run that

CMD ["python3", "-m", "hardware.main"]