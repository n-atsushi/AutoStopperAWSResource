FROM public.ecr.aws/lambda/python:3.12-arm64

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY app/lambda_function.py ${LAMBDA_TASK_ROOT}

CMD [ "lambda_function.handler" ]
