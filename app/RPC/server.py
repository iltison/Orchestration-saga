import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='availability')

def fib(n):
    if n == 'Availability':
        return True
    return False

def on_request(ch, method, props, body):
    n = str(body, 'utf-8')
    print(" [.] fib(%s)" % n)
    response = fib(n)
    print(" [.] %s" % response)
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='availability', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()