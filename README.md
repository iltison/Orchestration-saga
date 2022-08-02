Run 

Docker:  
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.10-management


service:  
python -m microservices.available_order

saga:  
python -m app.saga.saga
