import datetime,os,jwt
from flask import Flask,request
from flask_myslqdb import MySQL


server = Flask(__name__)
mysql = MySQL(server)



server.config["MySQL_HOST"]=os.environ.get("MYSQL_HOST")
server.config["MySQL_USER"]=os.environ.get("MYSQL_USER")
server.config["MySQL_PASSWORD"]=os.environ.get("MYSQL_PASSWORD")
server.config["MySQL_DB"]=os.environ.get("MYSQL_DB")
server.config["MySQL_HOST"]=os.environ.get("MYSQL_PORT")


@server.route("/login",methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials",401
    
    # check DB for user,pass
    cur = mysql.connection.cursur() 

    res=cur.execute(
        "SELECT email,password FROM user WHERE email=%s",(auth.username,)
    )
    if res > 0 :
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]
        
        if auth.username != email or auth.password != password:
                return "invalid credentials",401
        else:
            return createJWT(auth.username,os.environ.get("JWT_SECRET"),True)
    else:
        return "invalid credentials",401
    
server.route("/validate",methods=["POST"])
def validate():
    encode_jwt =request.headers["Authorization" ]
    if not encode_jwt:
        return "missinf credentials",401
    
    encode_jwt= encode_jwt.split(" ")[1]
    
    try:
        decode= jwt.decode(encode_jwt,os.environ.get("JWT_SECRET"),algorithms="HS256")
    except:
        return "not authorized",403
    
    return decode,200
    
    
def createJWT(username,secret,authz):
    return jwt.encode(
        {
            "username":username,
            "exp":datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat":datetime.datetime.utc(),
            "admin":authz,
        },
        secret,
        algorithm="HS256"
    )
    
if __name__ == "__main__":
    server.run("0.0.0.0",port=5000)