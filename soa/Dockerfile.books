FROM python:3.9-slim
WORKDIR /app
COPY books_service.py .
RUN pip install flask requests
EXPOSE 5000
CMD ["python", "books_service.py"]