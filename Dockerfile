#https://pdm-project.org/latest/usage/advanced/#use-pdm-in-a-multi-stage-dockerfile

ARG PYTHON_BASE=3.12-slim
# build stage
FROM python:$PYTHON_BASE AS builder
ARG STAGE

# install PDM
RUN pip install -U pdm
# disable update check
ENV PDM_CHECK_UPDATE=false
# copy files
COPY pyproject.toml pdm.lock /project/
COPY . /project/src

# install dependencies and project into the local packages directory
WORKDIR /project

RUN apt-get clean && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

#install all dependencies
RUN pip install uv
RUN pdm config use_uv true  
RUN pdm install

# run stage
FROM python:$PYTHON_BASE
ARG STAGE
# retrieve packages from build stage
COPY --from=builder /project/.venv/ /project/.venv
ENV PATH="/project/.venv/bin:$PATH"
ENV PYTHONPATH="/project/.venv/lib/python3.12/site-packages:/project/src:$PYTHONPATH"
EXPOSE 6969
ENV STREAMLIT_SERVER_PORT=6969
# set command/entrypoint, adapt to fit your needs
COPY . /project/src
COPY .streamlit/config.toml ./.streamlit/
CMD [ "streamlit", "run", "/project/src/app.py", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false" ]