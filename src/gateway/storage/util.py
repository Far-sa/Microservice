import os,pika,json

def upload(f,fs,access,channel):
    try:
        fid = fs.put(f)
    except Exception as err:
        return "internal server error",500
    
    message = {
        "video_fid": str(fid),
        "mp3_fid":None,
        "username": access["username"],
    }
    
    try:
        channel.basic_publish(
            exchange= "",
            routing_key="video",
            body=json.dumps(message),
            properties= pika.BasicProperties(
                delivery_mode=pika.__spec__.PERSISTAENT_DELIVEY_MODE
            ),
        )
    except:
        fs.delete(fid)
        return "internal server error",500