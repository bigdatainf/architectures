FROM python:3.9-slim
WORKDIR /app
COPY loans_service.py .
RUN pip install flask requests
EXPOSE 5000
CMD ["python", "loans_service.py"]