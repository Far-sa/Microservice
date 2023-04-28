import os,pika,sys,time
from pymongo import MongoClient
import gridfs

import convert from to_mp3


def main():
    client = MongoClient("host.minikube.internal",27017)
    db_video = client.videos
    db_mp3s = client.mp3s
    
    #* Gridfs
    fs_mp3s = gridfs.Gridfs(db_mp3s)
    fs_videos = gridfs.Gridfs(db_video)

    #* RabbitMQ connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    
    def callback(ch,method,body,properties):
        err = to_mp3.start(body,fs_videos,fs_mp3s,ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
    
    channel.basic_consume(
        queue = os.environ.get("VIDEO_QUEUE"),on_message_callback=callback
    )
    print("waiting for messages. To exist press CTRL+C")
    
    channel.start_consuming()
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)