FROM ubuntu:20.04

LABEL maintainer="aolney@memphis.edu"

ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

# We copy just the requirements.txt first to leverage Docker cache
COPY ./environment.yml /app/environment.yml

WORKDIR /app

#set up the conda env, discovering its name from environment.yml
RUN conda env create -f /app/environment.yml
RUN echo "conda activate $(head -1 /app/environment.yml | cut -d' ' -f2)" >> ~/.bashrc
ENV CONDA_DEFAULT_ENV="$(head -1 /app/environment.yml | cut -d' ' -f2)"
ENV ENV_TORCH_HOME=/app/models
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

COPY . /app

EXPOSE 8000

#explicitly calling with bash so that conda env is set up for gunicorn; a bit convoluted to be generic with the env name
CMD ["/bin/bash", "-c","conda run -n $(head -1 /app/environment.yml | cut -d' ' -f2) gunicorn -w 4 -b 0.0.0.0:8000 app:app"]
