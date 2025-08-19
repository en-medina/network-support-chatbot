FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y \
    iputils \
    && dnf clean all \
    && rm -rf /var/cache/dnf

COPY requirements.txt .
RUN pip install --no-cache-dir \
    -r requirements.txt

COPY . .

CMD ["app.lambda_handler"]