FROM quay.io/iamplus/nlu:master
#FROM nlu-test

WORKDIR /nlu
# give the celery logs a place to live
RUN mkdir -p /var/log/celery && mkdir -p /var/log/nlu

COPY . ./nlu_applications/home

RUN pip3 install -I --force-reinstall -r ./nlu_applications/home/requirements.txt

# configure and install NLU application.
RUN make config app=home && make clean && make update-config && make update-modules && make install
