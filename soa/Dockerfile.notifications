FROM python:3.9-slim
WORKDIR /app
COPY notifications_service.py .
RUN pip install flask requests
EXPOSE 5000
CMD ["python", "notifications_service.py"]