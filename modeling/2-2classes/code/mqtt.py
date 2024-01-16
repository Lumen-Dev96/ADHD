import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, message):
    print("Received message on topic %s: %s" % (message.topic, message.payload.decode()))

# 连接MQTT代理
broker_address = "broker.emqx.io"
port = 1883
username = "test"
password = "123456"

client = mqtt.Client()
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message


client.connect(broker_address, port)


# 订阅消息
topic = "Lumen"
client.subscribe(topic)

client.loop_forever()

