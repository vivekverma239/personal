FROM ubuntu:18.04

EXPOSE 80

WORKDIR /home/dashboard/
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        git \
        python3 \
        python3-dev \
        python3-setuptools \
        python3-pip 

        
RUN apt-get update \
    && apt-get upgrade -y \
    && pip3 install uwsgi \
    && pip3 install nltk \
    && python3 -c "import nltk; nltk.download('punkt')" \
    && python3 -c "import nltk; nltk.download('averaged_perceptron_tagger')" \
    && mkdir -p logs \
    && apt-get install netcat -y

# Only for certain ubuntu distribution type like in EXL
#RUN pip3 install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.5.0-cp35-cp35m-linux_x86_64.whl
RUN python3 -c "import nltk; nltk.download('stopwords')"

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

RUN python3 -m spacy download en_core_web_sm


# ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates locales \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/* 


ENV JAVA_HOME=/opt/java/openjdk \
    PATH="/opt/java/openjdk/bin:$PATH"

COPY . .

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /dev/stdout \
	&& ln -sf /dev/stderr /dev/stdout

ENV C_FORCE_ROOT='true'
# ENV LANG C.UTF-8
# ENV LC_ALL C.UTF-8

# ENTRYPOINT ["./entrypoint.sh"]
