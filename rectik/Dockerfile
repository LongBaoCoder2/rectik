FROM nvcr.io/nvidia/merlin/merlin-tensorflow:nightly


COPY . /rectik/

# Set environment variables
ENV NVIDIA_VISIBLE_DEVICES=""
ENV NVIDIA_DRIVER_CAPABILITIES=""
ENV NUMBA_DISABLE_JIT=1
ENV NUMBA_DISABLE_CUDA=1
ENV METAFLOW_HOME=/metaflow
ENV PYTHONUNBUFFERED=1
ENV METAFLOW_USER=user

WORKDIR /rectik

# Install dependencies
RUN pip install --upgrade pip 

RUN pip install -r /rectik/requirements.txt

# The dependency tailored for aligning with my working device.
RUN pip uninstall cudf -y && \
    pip install -U pandas && \
    pip install -U numba dask && \
    pip uninstall dask -y && \
    pip install "dask==2023.6.0"

# Set working directory
CMD [ "python", "data_flow.py", "run" ]
