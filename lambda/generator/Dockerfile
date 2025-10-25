FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y \
    iputils \
    && dnf clean all \
    && rm -rf /var/cache/dnf

COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv \
    && pipenv install --deploy --system --ignore-pipfile \
    && rm -rf /root/.cache/pip /root/.cache/pipenv

COPY . .

CMD ["app.lambda_handler"]