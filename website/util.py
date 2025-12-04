import smtplib
import ssl
import os
from configparser import ConfigParser
from . import database
from .dbModels import User, Sample

def cMS(milliseconds):

    if (milliseconds == None) :
        milliseconds = 0

    seconds=int((milliseconds/1000)%60)
    minutes=int((milliseconds/(1000*60))%60)
    hours=int((milliseconds/(1000*60*60))%24)
    result=str(str(hours).zfill(2) + ":" + str(minutes).zfill(2) + ":" + str(seconds).zfill(2))
    return result

def cHMS(time_str, fallbackvalue=0):
    try:
        h, m, s = time_str.split(':')
        return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000
    except Exception as e:
        print(e)
        return fallbackvalue

def convBool(vhod):
    if (vhod == "on"):
        return True
    else:
        return False

def convChecked(vhod):
    vhod=str(vhod)
    if (vhod == "True"):
        return "checked"
    elif (vhod == "False"):
        return ""
    else:
        return vhod

def convTF(vhod):
    vhod=str(vhod)
    if (vhod == "True"):
        return "DA"
    elif (vhod == "False"):
        return "NE"
    else:
        return vhod

def convMail(vhod):
    vhod=str(vhod)
    return "<a href=\"mailto:" + vhod + "\">" + vhod + "</a>"

def updateUsersRecordingLengts():
    
    allSamples = database.session.query(Sample).all()
    allUsers   = database.session.query(User).all()

    for user in allUsers:
        total = 0
        aprooved = 0
        for sample in allSamples:
            if sample.userID == user.id:
                total += sample.metaTechLengthMilisec
                if sample.metaEditingChecked == True:
                    aprooved += sample.metaEditingLengthAprv
        
        user.totalRecoringsLengtMilisec = total
        user.approvedRecoringsLengtMilisec = aprooved
        database.session.commit()

    return 0

def sendMail(message):

    try:

        cfgParse = ConfigParser()
        cfgParse.read(os.getcwd() + "/mail-config.ini")

        smtp_sender    = cfgParse.get("smtp","sender")
        smtp_password  = cfgParse.get("smtp","password")
        smtp_server    = cfgParse.get("smtp","server")
        smtp_port      = cfgParse.getint("smtp","port")

        email_receiver = cfgParse.get("mail","receiverlist").split(",")
        email_Subject  = "Subject: " + cfgParse.get("mail","subject")
        email_From     = "From: " + cfgParse.get("mail","from") + "<" + smtp_sender + ">"
        email_To       = "To: " + ", ".join(email_receiver)
        email_Content  = "Content-Type: text/plain; charset=\"utf-8\""

        email = ""
        email = email + email_Subject + "\n"
        email = email + email_From + "\n"
        email = email + email_To + "\n"
        email = email + email_Content + "\n"
        email = email + "\n"
        email = email + message
        email = email + "\n\nTo je avtomatizirano sporočilo s portala <<ime portala>>"
        email = email.encode('utf-8')

        server = smtplib.SMTP(smtp_server,smtp_port)
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.set_default_verify_paths()
        context.verify_mode = ssl.CERT_REQUIRED
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(smtp_sender, smtp_password)
        server.sendmail(smtp_sender, email_receiver, email)

    except Exception as e:
        print(e)
    return
    
def notifyNewUser(name, username, email):
    message = "Na portalu je registriran nov uporabnik z uporabniskim imenom " 
    message += username + ", s podatki: " + name + "(" + email + ")"
    sendMail(message)

def notifyNewRecording(username, id):
    message = "Na portalu je uporabnik z uporabniskim imenom " 
    message += username + " oddal now posnetek, ki je dobil zaporedne številko ID=" + str(id) + "."
    sendMail(message)
    
def notifyOfEdit(username, type, id):
    message = "Na portalu je uporabnik z uporabnikškim imenom "
    message += username + " urejal " + type + " z zaporedno številko ID=" + str(id) + "."
    sendMail(message)
