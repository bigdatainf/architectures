FROM python:3.9-slim
WORKDIR /app
COPY users_service.py .
RUN pip install flask requests
EXPOSE 5000
CMD ["python", "users_service.py"]