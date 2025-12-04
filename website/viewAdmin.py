import xlsxwriter
import datetime
import os
import html
import subprocess
import shlex

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from . import database
from .dbModels import User, Sample, Transcript, Speaker
from .util import *
from .utilFormat import *

viewAdmin = Blueprint('viewAdmin', __name__)

@viewAdmin.route('/admin')
@login_required
def admin():
    if(current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    else:
        return render_template("admin.html", user=current_user, username=current_user.username, wide=True)


@viewAdmin.route('/admin-users', methods=['GET', 'POST'])
@login_required
def admin_users():

    if(current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    
    else: 

        maxID = database.session.query(User).count()
        dropdownOptions=""
        for i in range (1,maxID+1):
            dropdownOptions += "<option value=" + str(i) + ">" + str(i) + " - "
            dropdownOptions += html.escape(str(User.query.get(i).nameSurname))
            dropdownOptions += "</option>\n"

        if request.method == 'GET':
            return render_template("admin-users.html",
                user=current_user, 
                username=current_user.username, 
                dropdownOptions=dropdownOptions,
                hiddenDiv="hidden",
                showID="0",
                wide=True)
        
        elif ("changeData" in request.form):

            showID = int(request.form.get('currentID'))

            newNameLastname  = str(request.form.get('nameSurname'))
            newEmail         = str(request.form.get('email'))
            newIsAdmin       = str(request.form.get('isAdmin'))
            newIsTranscriber = str(request.form.get('isTranscriber'))
            newPrizeSelect   = str(request.form.get('prizeSelect'))
            newPrizeSend     = str(request.form.get('prizeSend'))
            if (showID == 1):
                newIsAdmin = "on"

            user = User.query.filter_by(id=showID).first()

            now = datetime.datetime.now()
            now = now.strftime("%Y-%m-%d %H-%M-%S")
            output  = "Changin user data at: " + now + "\n"
            output += "Changes done by: " + current_user.username  + "\n"
            output += "OLD DATA:\n\n"
            for c in user.__table__.columns:
                output += '{}: {}\n'.format(c.name, getattr(user, c.name))
            output += "\n"
            
            user.nameSurname = newNameLastname
            user.email = newEmail
            user.isAdmin = convBool(newIsAdmin)
            user.isEditor = convBool(newIsAdmin)
            user.isTranscriber = convBool(newIsTranscriber)
            user.prizeSelect = newPrizeSelect
            user.prizeSend = convBool(newPrizeSend)
            database.session.commit()

            notifyOfEdit(current_user.username,"uporabnika",showID)

            output += "NEW DATA:\n\n"
            for c in user.__table__.columns:
                output += '{}: {}\n'.format(c.name, getattr(user, c.name))
            
            rootFolder = os.getcwd()
            filename= rootFolder + "/instance/changelog-user-" + now + ".txt"
            with open(filename, "wb") as fM:
                fM.write(str.encode(output))

        elif ("showUser" in request.form):
            showID = int(request.form.get('idSelect'))
            if (showID == 0):
                flash("Izberite uporabnika", category='error')
                return render_template("admin-users.html",
                    user=current_user, 
                    username=current_user.username, 
                    dropdownOptions=dropdownOptions,
                    hiddenDiv="hidden",
                    showID="0",
                    wide=True)
            
        elif ("showNext" in request.form):
            showID = int(request.form.get('currentID'))+1
            if (showID > maxID):
                showID = 1
            
        elif ("showPrev" in request.form):
            showID = int(request.form.get('currentID'))-1
            if (showID < 1):
                showID = maxID
        
        dataBaseContent, dataNS, dataEM, dataADM, dataTRS, dataPSel, dataPSnd = formatDataBaseContentUser(showID)
        dataADMc=convChecked(dataADM)
        dataTRSc=convChecked(dataTRS)
        dataPSndc=convChecked(dataPSnd)

        return render_template("admin-users.html",
            user=current_user, 
            username=current_user.username, 
            dropdownOptions=dropdownOptions,
            hiddenDiv="",
            showID=showID,
            dataBaseContent=dataBaseContent,
            dataNS=dataNS,
            dataEM=dataEM,
            dataADM=dataADMc,
            dataTRS=dataTRSc,
            dataPSel=dataPSel,
            dataPSnd=dataPSndc,
            wide=True)

@viewAdmin.route('/admin-recordings', methods=['GET', 'POST'])
@login_required
def admin_recordings():

    if(current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    
    else: 
        
        maxID = database.session.query(Sample).count()
        dropdownOptions=""
        for i in range (1,maxID+1):
            dropdownOptions += "<option value=" + str(i) + ">" + str(i)
            dropdownOptions += "</option>\n"

        if request.method == 'GET':
            return render_template("admin-recordings.html",
                user=current_user, 
                username=current_user.username, 
                dropdownOptions=dropdownOptions,
                hiddenDiv="hidden",
                showID="0",
                wide=True)
        
        elif ("dwnlAll" in request.form):
            filename = os.getcwd() + "/database/AllAudio-" + str(maxID) + ".zip"
            all = []
            all.append("zip")
            all.append("-u")
            all.append(filename)
            for i in range (1,maxID+1):
                all.append("database/" + Sample.query.get(i).metaTechFilenameWave)
            subprocess.run(all)
            return send_file(filename, as_attachment=True)
            
        elif ("dwnlFile" in request.form):
            showID = int(request.form.get('currentID'))
            dataFolder = os.getcwd() + "/database/"
            fileAudio = dataFolder + Sample.query.get(showID).metaTechFilenameWave
            return send_file(fileAudio, as_attachment=True)
        
        elif ("showSample" in request.form):
            showID = int(request.form.get('idSelect'))
            if (showID == 0):
                flash("Izberite posnetek", category='error')
                return render_template("admin-recordings.html",
                    user=current_user, 
                    username=current_user.username, 
                    dropdownOptions=dropdownOptions,
                    hiddenDiv="hidden",
                    showID="0",
                    wide=True)
            
        elif ("showNext" in request.form):
            showID = int(request.form.get('currentID'))+1
            if (showID > maxID):
                showID = 1
        
        elif ("showPrev" in request.form):
            showID = int(request.form.get('currentID'))-1
            if (showID < 1):
                showID = maxID

        elif ("changeFile" in request.form):
            showID = int(request.form.get('currentID'))
            
            now = datetime.datetime.now()
            now = now.strftime("%Y-%m-%d %H-%M-%S")
            old_name = os.getcwd() + "/database/" + Sample.query.get(showID).metaTechFilenameWave
            bu_name = os.getcwd() + "/database/bu/" + Sample.query.get(showID).metaTechFilenameWave + ".bu-" + now
            try:
                fileNew = request.files['formAF_FILE']
                if (fileNew.filename != ""):
                    os.rename(old_name, bu_name)
                    fileNew.save(old_name)
            except:
                print("napaka pri shranjeanju nove audio datoteke")
                pass

        try:
            soxContent = formatWaveFileData(showID)
        except:
            soxContent  = "Datoteka = " + os.getcwd() + "/database/" + Sample.query.get(showID).metaTechFilenameWave
            soxContent += "\nNapaka pri samodejnem pridobivanju podatkov o datoteki. "
            soxContent += "\nPoskusite ročno pregledati datoteko. "
        
        return render_template("admin-recordings.html", 
            user=current_user, 
            username=current_user.username, 
            dropdownOptions=dropdownOptions,
            hiddenDiv="",
            showID=showID,
            soxContent=soxContent,
            wide=True)


@viewAdmin.route('/admin-samples', methods=['GET', 'POST'])
@login_required
def admin_samples():
    if(current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    else: 

        maxID = database.session.query(Sample).count()
        dropdownOptions=""
        for i in range (1,maxID+1):
            dropdownOptions += "<option value=" + str(i) + ">" + str(i)
            dropdownOptions += "</option>\n"

        if request.method == 'GET':
            return render_template("admin-samples.html",
                user=current_user, 
                username=current_user.username, 
                dropdownOptions=dropdownOptions,
                hiddenDiv="hidden",
                showID="0",
                wide=True)
        
        elif ("dwnlFiles" in request.form):
            showID = int(request.form.get('currentID'))
            dataFolder = os.getcwd() + "/database/"
            fileAudio = dataFolder + Sample.query.get(showID).metaTechFilenameWave
            return send_file(fileAudio, as_attachment=True)
        elif ("dwnlFilesA" in request.form):
            showID = int(request.form.get('currentID'))
            dataFolder = os.getcwd() + "/database/"
            fileAudio = dataFolder + Sample.query.get(showID).metaTechFilenameFrmA
            return send_file(fileAudio, as_attachment=True)
        elif ("dwnlFilesB" in request.form):
            showID = int(request.form.get('currentID'))
            dataFolder = os.getcwd() + "/database/"
            fileAudio = dataFolder + Sample.query.get(showID).metaTechFilenameFrmB
            return send_file(fileAudio, as_attachment=True)
        elif ("dwnlFilesC" in request.form):
            showID = int(request.form.get('currentID'))
            dataFolder = os.getcwd() + "/database/"
            fileAudio = dataFolder + Sample.query.get(showID).metaTechFilenameFrmC
            return send_file(fileAudio, as_attachment=True)
        
        elif ("showSample" in request.form):
            showID = int(request.form.get('idSelect'))
            if (showID == 0):
                flash("Izberite posnetek", category='error')
                return render_template("admin-samples.html",
                    user=current_user, 
                    username=current_user.username, 
                    dropdownOptions=dropdownOptions,
                    hiddenDiv="hidden",
                    showID="0",
                    wide=True)
            
        elif ("showNext" in request.form):
            showID = int(request.form.get('currentID'))+1
            if (showID > maxID):
                showID = 1
        
        elif ("showPrev" in request.form):
            showID = int(request.form.get('currentID'))-1
            if (showID < 1):
                showID = maxID

        elif ("changeData" in request.form):
            showID = int(request.form.get('currentID'))

            newTextID         = str(request.form.get('dataTextID'))
            newSourceID       = str(request.form.get('dataSourceID'))
            newRecordingID    = str(request.form.get('dataRecordingID'))
            newSubcorpus      = str(request.form.get('dataSubcorpus'))
            newDesciption     = str(request.form.get('dataDesciption'))
            newDate           = str(request.form.get('dataDate'))
            newSource         = str(request.form.get('dataSource'))
            newLocation       = str(request.form.get('dataLocation'))
            newSpeechDomain   = str(request.form.get('dataSpeechDomain'))
            newSpeechType     = str(request.form.get('dataSpeechType'))
            newChannel        = str(request.form.get('dataChannel'))
            newKeywords       = str(request.form.get('dataKeywords'))
            newDevice         = str(request.form.get('dataDevice'))
            newRooms          = str(request.form.get('dataRooms'))
            newQuality        = str(request.form.get('dataQuality'))
            newURL            = str(request.form.get('dataURL'))
            newLenAprv        = str(request.form.get('dataLenAprv'))
            newChecked        = convBool(str(request.form.get('dataChecked')))
            newApprovedQ      = convBool(str(request.form.get('dataApprovedQ')))
            newApprovedForT   = convBool(str(request.form.get('dataApprovedForT')))
            newCommentForT    = str(request.form.get('dataCommentForT'))
            newStartedT       = convBool(str(request.form.get('dataStartedT')))
            newApprovedT      = convBool(str(request.form.get('dataApprovedT')))
            newEditorComment  = str(request.form.get('dataEditorComment'))

            now = datetime.datetime.now()
            now = now.strftime("%Y-%m-%d %H-%M-%S")
            sample = Sample.query.filter_by(id=showID).first()

            output  = "Changin sample data at: " + now + "\n"
            output += "Changes done by: " + current_user.username  + "\n"
            output += "OLD DATA:\n\n"

            for c in sample.__table__.columns:
                output += '{}: {}\n'.format(c.name, getattr(sample, c.name))
            output += "\n"

            sample.metaEditingTextID        = newTextID       
            sample.metaEditingSourceID      = newSourceID     
            sample.metaEditingRecodingID    = newRecordingID  
            sample.metaEditingSubcorpus     = newSubcorpus    
            sample.metaEditingDescription   = newDesciption   
            sample.metaEditingDate          = newDate         
            sample.metaEditingSource        = newSource       
            sample.metaEditingLocation      = newLocation     
            sample.metaEditingSpeechDomain  = newSpeechDomain 
            sample.metaEditingSpeechType    = newSpeechType   
            sample.metaEditingChannel       = newChannel      
            sample.metaEditingKeywords      = newKeywords     
            sample.metaEditingDevice        = newDevice       
            sample.metaEditingRooms         = newRooms        
            sample.metaEditingQuality       = newQuality      
            sample.metaEditingURL           = newURL          
            sample.metaEditingLengthAprv    = int(cHMS(newLenAprv,fallbackvalue=sample.metaTechLengthMilisec))
            sample.metaEditingChecked       = newChecked      
            sample.metaEditingApprovedQ     = newApprovedQ    
            sample.metaEditingApprovedForT  = newApprovedForT 
            sample.metaEditingCommentForT   = newCommentForT
            sample.metaEditingStartedT      = newStartedT     
            sample.metaEditingApprovedTRS   = newApprovedT    
            sample.metaEditingEditorComment = newEditorComment

            sample.metaEditingNameOfEditor  = current_user.nameSurname + " (" + current_user.username + ")"
            sample.metaEditingLastEditTime  = now

            database.session.commit()

            output += "NEW DATA:\n\n"
            for c in sample.__table__.columns:
                output += '{}: {}\n'.format(c.name, getattr(sample, c.name))
            
            rootFolder = os.getcwd()
            filename= rootFolder + "/instance/changelog-sample-" + now + ".txt"
            with open(filename, "ab") as fM:
                fM.write(str.encode(output))

        dataBaseContent = ""
        dataBaseContent = formatDataBaseContentSample(showID)
        
        hideBtnSpkB = ""
        hideBtnSpkC = ""
        if (Sample.query.get(showID).metaUploadNoSpeakers < 2):
            hideBtnSpkB = "hidden"
        if (Sample.query.get(showID).metaUploadNoSpeakers < 3):
            hideBtnSpkC = "hidden"

        SpeakerIDA = 0
        SpeakerIDB = 0
        SpeakerIDC = 0
        AllSpeakers = database.session.query(Speaker).all()
        for ThisSpeaker in AllSpeakers:
            if ThisSpeaker.recordingID == showID:
                if (ThisSpeaker.recordingOrder == 1):
                    SpeakerIDA = ThisSpeaker.id
                if (ThisSpeaker.recordingOrder == 2):
                    SpeakerIDB = ThisSpeaker.id
                if (ThisSpeaker.recordingOrder == 3):
                    SpeakerIDC = ThisSpeaker.id

        linkSpeakerA = "<a href=\"/admin-speakers?id="+str(SpeakerIDA)+"\" target=\"_blank\">Prikaži govorca 1</a>"
        if (Sample.query.get(showID).metaUploadNoSpeakers >= 2):
            linkSpeakerB = "<a href=\"/admin-speakers?id="+str(SpeakerIDB)+"\" target=\"_blank\">Prikaži govorca 2</a>"
        else:
            linkSpeakerB = ""
        if (Sample.query.get(showID).metaUploadNoSpeakers >= 3):
            linkSpeakerC = "<a href=\"/admin-speakers?id="+str(SpeakerIDC)+"\" target=\"_blank\">Prikaži govorca 3</a>"
        else:
            linkSpeakerC = ""
        
        return render_template("admin-samples.html", 
            user=current_user, 
            username=current_user.username, 
            dropdownOptions=dropdownOptions,
            hiddenDiv="",
            showID=showID,
            dataBaseContent=dataBaseContent,
            linkSpeakerA=linkSpeakerA,
            linkSpeakerB=linkSpeakerB,
            linkSpeakerC=linkSpeakerC,

            dataTextID = str(Sample.query.get(showID).metaEditingTextID),
            dataSourceID = str(Sample.query.get(showID).metaEditingSourceID),
            dataRecordingID = str(Sample.query.get(showID).metaEditingRecodingID),
            dataSubcorpus = str(Sample.query.get(showID).metaEditingSubcorpus),
            dataDesciption = str(Sample.query.get(showID).metaEditingDescription),
            dataDate = str(Sample.query.get(showID).metaEditingDate),
            dataSource = str(Sample.query.get(showID).metaEditingSource),
            dataLocation = str(Sample.query.get(showID).metaEditingLocation),
            dataSpeechDomain = str(Sample.query.get(showID).metaEditingSpeechDomain),
            dataSpeechType = str(Sample.query.get(showID).metaEditingSpeechType),
            dataChannel = str(Sample.query.get(showID).metaEditingChannel),
            dataKeywords = str(Sample.query.get(showID).metaEditingKeywords),
            dataDevice = str(Sample.query.get(showID).metaEditingDevice),
            dataRooms = str(Sample.query.get(showID).metaEditingRooms),
            dataQuality = str(Sample.query.get(showID).metaEditingQuality),
            dataURL = str(Sample.query.get(showID).metaEditingURL),
            dataLenAprv = cMS(Sample.query.get(showID).metaEditingLengthAprv),
            dataChecked = convChecked(Sample.query.get(showID).metaEditingChecked),
            dataApprovedQ = convChecked(Sample.query.get(showID).metaEditingApprovedQ),
            dataApprovedForT = convChecked(Sample.query.get(showID).metaEditingApprovedForT),
            dataCommentForT = str(Sample.query.get(showID).metaEditingCommentForT),
            dataStartedT = convChecked(Sample.query.get(showID).metaEditingStartedT),
            dataApprovedT = convChecked(Sample.query.get(showID).metaEditingApprovedTRS),
            dataEditorComment = str(Sample.query.get(showID).metaEditingEditorComment),
            wide=True)


@viewAdmin.route('/serve-img', methods=['GET'])
def serve_img():
    if(current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    ParamID = request.args.get('id')
    recordingID = Speaker.query.get(ParamID).recordingID
    recordingOrder = Speaker.query.get(ParamID).recordingOrder
    if (recordingOrder == 1):
        fileDWLD = Sample.query.get(recordingID).metaTechFilenameFrmA
    elif (recordingOrder == 2):
        fileDWLD = Sample.query.get(recordingID).metaTechFilenameFrmB
    elif (recordingOrder == 3):
        fileDWLD = Sample.query.get(recordingID).metaTechFilenameFrmC
    dataFolder = os.getcwd() + "/database/"
    fileDWLD = dataFolder + fileDWLD
    return send_file(fileDWLD)


@viewAdmin.route('/admin-speakers', methods=['GET', 'POST'])
@login_required
def admin_speakers():

    ParamID = request.args.get('id')

    if(current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    
    else: 

        maxID = database.session.query(Speaker).count()
        dropdownOptions=""
        for i in range (1,maxID+1):
            dropdownOptions += "<option value=" + str(i) + ">" + str(i)
            dropdownOptions += "</option>\n"

        if (request.method == 'GET') and (ParamID is not None):
            showID = int(ParamID)

        elif request.method == 'GET':
            return render_template("admin-speakers.html",
                user=current_user,
                username=current_user.username, 
                dropdownOptions=dropdownOptions,
                hiddenDiv="hidden",
                showID="0",
                wide=True)
        
        elif ("dwnlFile" in request.form):
            showID = int(request.form.get('currentID'))
            dataFolder = os.getcwd() + "/database/"
            recordingID = Speaker.query.get(showID).recordingID
            recordingOrder = Speaker.query.get(showID).recordingOrder

            if (recordingOrder == 1):
                fileDWLD = Sample.query.get(recordingID).metaTechFilenameFrmA
            elif (recordingOrder == 2):
                fileDWLD = Sample.query.get(recordingID).metaTechFilenameFrmB
            elif (recordingOrder == 3):
                fileDWLD = Sample.query.get(recordingID).metaTechFilenameFrmC

            fileDWLD = dataFolder + fileDWLD
            return send_file(fileDWLD, as_attachment=True)
        
        elif ("showSpeaker" in request.form):
            showID = int(request.form.get('idSelect'))
            if (showID == 0):
                flash("Izberite govorca", category='error')
                return render_template("admin-speakers.html",
                    user=current_user,
                    username=current_user.username, 
                    dropdownOptions=dropdownOptions,
                    hiddenDiv="hidden",
                    showID="0",
                    wide=True)
            
        elif ("showNext" in request.form):
            showID = int(request.form.get('currentID'))+1
            if (showID > maxID):
                showID = 1

        elif ("showPrev" in request.form):
            showID = int(request.form.get('currentID'))-1
            if (showID < 1):
                showID = maxID
        
        elif ("changeData" in request.form):
            showID = int(request.form.get('currentID'))

            newdataTextID              = str(request.form.get('dataTextID'))
            newdataSourceID            = str(request.form.get('dataSourceID'))
            newdataRecordingID         = str(request.form.get('dataRecordingID'))
            newdataSubcorpus           = str(request.form.get('dataSubcorpus'))
            newdataPRSID               = str(request.form.get('dataPRSID'))
            newdataGender              = str(request.form.get('dataGender'))
            newdataAge                 = str(request.form.get('dataAge'))
            newdataLanguageA           = str(request.form.get('dataLanguageA'))
            newdataDialectType         = str(request.form.get('dataDialectType'))
            newdataDialectGRP          = str(request.form.get('dataDialectGRP'))
            newdataDialect             = str(request.form.get('dataDialect'))
            newdataEducation           = str(request.form.get('dataEducation'))
            newdataLocationA           = str(request.form.get('dataLocationA'))
            newdataLocARegion          = str(request.form.get('dataLocARegion'))
            newdataLocACountry         = str(request.form.get('dataLocACountry'))
            newdataLocationB           = str(request.form.get('dataLocationB'))
            newdataLocBRegion          = str(request.form.get('dataLocBRegion'))
            newdataLocBCountry         = str(request.form.get('dataLocBCountry'))
            newdataLocationC           = str(request.form.get('dataLocationC'))
            newdataLocCRegion          = str(request.form.get('dataLocCRegion'))
            newdataLocCCountry         = str(request.form.get('dataLocCCountry'))
            newdataBilingual           = str(request.form.get('dataBilingual'))
            newdataLanguageB           = str(request.form.get('dataLanguageB'))

            now = datetime.datetime.now()
            now = now.strftime("%Y-%m-%d %H-%M-%S")
            speaker = Speaker.query.filter_by(id=showID).first()

            output  = "Changin sample data at: " + now + "\n"
            output += "Changes done by: " + current_user.username  + "\n"
            output += "OLD DATA:\n\n"

            for c in speaker.__table__.columns:
                output += '{}: {}\n'.format(c.name, getattr(speaker, c.name))
            output += "\n"

            speaker.metaEditingTextID             = newdataTextID          
            speaker.metaEditingSourceID           = newdataSourceID        
            speaker.metaEditingRecordingID        = newdataRecordingID     
            speaker.metaEditingSubcorpus          = newdataSubcorpus       
            speaker.metaEditingPRSID              = newdataPRSID           
            speaker.metaEditingGender             = newdataGender          
            speaker.metaEditingAge                = newdataAge             
            speaker.metaEditingLanguageA          = newdataLanguageA       
            speaker.metaEditingDialectType        = newdataDialectType     
            speaker.metaEditingDialectGRP         = newdataDialectGRP      
            speaker.metaEditingDialect            = newdataDialect         
            speaker.metaEditingEducation          = newdataEducation       
            speaker.metaEditingLocationA          = newdataLocationA       
            speaker.metaEditingLocARegion         = newdataLocARegion      
            speaker.metaEditingLocACountry        = newdataLocACountry     
            speaker.metaEditingLocationB          = newdataLocationB       
            speaker.metaEditingLocBRegion         = newdataLocBRegion      
            speaker.metaEditingLocBCountry        = newdataLocBCountry     
            speaker.metaEditingLocationC          = newdataLocationC       
            speaker.metaEditingLocCRegion         = newdataLocCRegion      
            speaker.metaEditingLocCCountry        = newdataLocCCountry     
            speaker.metaEditingBilingual          = newdataBilingual       
            speaker.metaEditingLanguageB          = newdataLanguageB      

            speaker.metaEditingNameOfEditor  = current_user.nameSurname + " (" + current_user.username + ")"
            speaker.metaEditingLastEditTime  = now 

            database.session.commit()

            output += "NEW DATA:\n\n"
            for c in speaker.__table__.columns:
                output += '{}: {}\n'.format(c.name, getattr(speaker, c.name))

            rootFolder = os.getcwd()
            filename= rootFolder + "/instance/changelog-speaker-" + now + ".txt"
            with open(filename, "ab") as fM:
                fM.write(str.encode(output))

        dataBaseContent = ""
        dataBaseContent = formatDataBaseContentSpeaker(showID)

        dataFolder = os.getcwd() + "/database/"
        recordingID = Speaker.query.get(showID).recordingID
        recordingOrder = Speaker.query.get(showID).recordingOrder
        if (recordingOrder == 1):
            fileDWLD = Sample.query.get(recordingID).metaTechFilenameFrmA
        elif (recordingOrder == 2):
            fileDWLD = Sample.query.get(recordingID).metaTechFilenameFrmB
        elif (recordingOrder == 3):
            fileDWLD = Sample.query.get(recordingID).metaTechFilenameFrmC
        fileDWLD = "static/database/" + fileDWLD

        print(fileDWLD)
        filename, file_extension = os.path.splitext(fileDWLD)
        file_extension = file_extension.lower()
        addition = ""
        
        if (file_extension == ".pdf"):
            addition  = "<embed src=\""
            addition += "/serve-img?id="
            addition += str(showID)
            addition += "\" "
            addition += "type=\"application/pdf\" width=\"100%\" height=\"600px\">"
            addition += "</embed>"
        else:
            addition = "<img src=\""
            addition += "/serve-img?id="
            addition += str(showID)
            addition += "\" "
            addition += "style='border:1px solid #000000' width=\"100%\"></img>"

        dataBaseContent = dataBaseContent + "\n<br />\n" + addition
        
        return render_template("admin-speakers.html",
            user=current_user, 
            username=current_user.username, 
            dropdownOptions=dropdownOptions,
            hiddenDiv="",
            showID=showID,
            dataBaseContent=dataBaseContent,
            dataTextID       = str (Speaker.query.get(showID).metaEditingTextID),
            dataSourceID     = str (Speaker.query.get(showID).metaEditingSourceID),
            dataRecordingID  = str (Speaker.query.get(showID).metaEditingRecordingID),
            dataSubcorpus    = str (Speaker.query.get(showID).metaEditingSubcorpus),
            dataPRSID        = str (Speaker.query.get(showID).metaEditingPRSID),
            dataGender       = str (Speaker.query.get(showID).metaEditingGender),
            dataAge          = str (Speaker.query.get(showID).metaEditingAge),
            dataLanguageA    = str (Speaker.query.get(showID).metaEditingLanguageA),
            dataDialectType  = str (Speaker.query.get(showID).metaEditingDialectType),
            dataDialectGRP   = str (Speaker.query.get(showID).metaEditingDialectGRP),
            dataDialect      = str (Speaker.query.get(showID).metaEditingDialect),
            dataEducation    = str (Speaker.query.get(showID).metaEditingEducation),
            dataLocationA    = str (Speaker.query.get(showID).metaEditingLocationA),
            dataLocARegion   = str (Speaker.query.get(showID).metaEditingLocARegion),
            dataLocACountry  = str (Speaker.query.get(showID).metaEditingLocACountry),
            dataLocationB    = str (Speaker.query.get(showID).metaEditingLocationB),
            dataLocBRegion   = str (Speaker.query.get(showID).metaEditingLocBRegion),
            dataLocBCountry  = str (Speaker.query.get(showID).metaEditingLocBCountry),
            dataLocationC    = str (Speaker.query.get(showID).metaEditingLocationC),
            dataLocCRegion   = str (Speaker.query.get(showID).metaEditingLocCRegion),
            dataLocCCountry  = str (Speaker.query.get(showID).metaEditingLocCCountry),
            dataBilingual    = str (Speaker.query.get(showID).metaEditingBilingual),
            dataLanguageB    = str (Speaker.query.get(showID).metaEditingLanguageB),
            wide = True)

@viewAdmin.route('/admin-transcripts', methods=['GET', 'POST'])
@login_required
def admin_transcripts():
    if(current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    
    else:

        maxID = database.session.query(Sample).count()
        dropdownOptionsRec=""
        for i in range (1,maxID+1):
            dropdownOptionsRec += "<option value=" + str(i) + ">" + str(i)
            dropdownOptionsRec += "</option>\n"

        if request.method == 'GET':
            return render_template("admin-transcripts.html", 
                user=current_user, 
                username=current_user.username, 
                dropdownOptionsRec=dropdownOptionsRec,
                hiddenSel="hidden",
                dropdownOptionsTrs="",
                hiddenEdt="hidden",
                dataBaseContent="",
                SelPog="",
                SelStd="",
                trsApproved="",
                showID="0",
                wide=True)
        
        recID = int(request.form.get('recID'))
        trsID = int(request.form.get('trsID'))
        maxID = database.session.query(Transcript).count()
        
        dropdownOptionsTrs=""
        for i in range (1,maxID+1):
            if Transcript.query.get(i).recordingID == recID:
                version=str(Transcript.query.get(i).version)                    
                approved=str(Transcript.query.get(i).approved)
                if approved == "False":
                    approved = "Neodobrena"
                else:
                    approved = "Odobrena"
                tip=str(Transcript.query.get(i).trsType)
                if tip=="1":
                    tip = "pogovorna"
                else:
                    tip = "standardizirana"
                dropdownOptionsTrs += "<option value=" + version + ">" + version + ": " + str(approved) + " " + tip
                dropdownOptionsTrs += "</option>\n"

        thisTRS = ""
        for i in range (1,maxID+1):
            if Transcript.query.get(i).recordingID == recID:
                if Transcript.query.get(i).version == trsID:
                    thisTRS = Transcript.query.get(i)
                    totalID = thisTRS.id
        
        dataBaseContent = ""
        if (thisTRS):

            if thisTRS.trsType == 1:
                thisType = "pogovorna"
                SelPog="selected"
                SelStd=""
            else:
                thisType = "standardizirana"
                SelPog=""
                SelStd="selected"
            
            if thisTRS.approved == True:
                trsApproved = "checked"
            else:
                trsApproved = ""

            dataBaseContent += "ID posnetka: " + str(recID) + "<br/>"
            dataBaseContent += "Verzija transkripcije: " + str(trsID) + "<br/>"
            dataBaseContent += "Tip transkripcije: " + thisType + "<br/>"
            dataBaseContent += "Transkriptor: " + str(thisTRS.transcriber) + "<br/>"
            dataBaseContent += "Odobreno: " + str(thisTRS.approved) + "<br/>"
            dataBaseContent += "Odobril: " + thisTRS.approvedBy + "(" + thisTRS.approvedDate + ")<br/>"

            dataFolder = os.getcwd() + "/database/"
            fileTRS = dataFolder + thisTRS.fileName
        
        if ("showRec" in request.form):
            return render_template("admin-transcripts.html", 
                user=current_user, 
                username=current_user.username, 
                dropdownOptionsRec=dropdownOptionsRec,
                hiddenSel="",
                dropdownOptionsTrs=dropdownOptionsTrs,
                hiddenEdt="hidden",
                dataBaseContent="",
                SelPog="",
                SelStd="",
                trsApproved="",
                recID=recID,
                wide=True)
        
        elif ("showTrs" in request.form):
            return render_template("admin-transcripts.html", 
                user=current_user, 
                username=current_user.username, 
                dropdownOptionsRec=dropdownOptionsRec,
                hiddenSel="",
                dropdownOptionsTrs=dropdownOptionsTrs,
                hiddenEdt="",
                dataBaseContent=dataBaseContent,
                SelPog=SelPog,
                SelStd=SelStd,
                trsApproved=trsApproved,
                recID=recID,
                trsID=str(trsID),
                wide=True)
        
        elif("dwnlFiles" in request.form):
            return send_file(fileTRS, as_attachment=True)
        
        elif("changeData" in request.form):

            newApproved = request.form.get('aproove')
            newApproved = convBool(newApproved)
            newType = request.form.get('typeSel')
            now = datetime.datetime.now()
            now = now.strftime("%Y-%m-%d %H-%M-%S")

            transcript = Transcript.query.filter_by(id=totalID).first()
            
            if (transcript.approved != newApproved):
                transcript.approved = newApproved
                if (transcript.approved == True):
                    transcript.approvedBy = current_user.nameSurname + " (" + current_user.username + ")"
                    transcript.approvedDate = now
                else:
                    transcript.approvedBy = ""
                    transcript.approvedDate = ""
            if (newType == "Pogovorna"):
                transcript.trsType = 1
            else:
                transcript.trsType = 2
            database.session.commit()
            notifyOfEdit(current_user.username,"transkripcijo",totalID)

            dropdownOptionsTrs=""
            for i in range (1,maxID+1):
                if Transcript.query.get(i).recordingID == recID:
                    version=str(Transcript.query.get(i).version)                    
                    approved=str(Transcript.query.get(i).approved)
                    if approved == "False":
                        approved = "Neodobrena"
                    else:
                        approved = "Odobrena"
                    tip=str(Transcript.query.get(i).trsType)
                    if tip=="1":
                        tip = "pogovorna"
                    else:
                        tip = "standardizirana"
                    dropdownOptionsTrs += "<option value=" + version + ">" + version + ": " + str(approved) + " " + tip
                    dropdownOptionsTrs += "</option>\n"

            if transcript.trsType == 1:
                thisType = "pogovorna"
                SelPog="selected"
                SelStd=""
            else:
                thisType = "standardizirana"
                SelPog=""
                SelStd="selected"
            
            if transcript.approved == True:
                trsApproved = "checked"
            else:
                trsApproved = ""

            dataBaseContent = ""
            dataBaseContent += "ID posnetka: " + str(recID) + "<br/>"
            dataBaseContent += "Verzija transkripcije: " + str(trsID) + "<br/>"
            dataBaseContent += "Tip transkripcije: " + thisType + "<br/>"
            dataBaseContent += "Transkriptor: " + str(thisTRS.transcriber) + "<br/>"
            dataBaseContent += "Odobreno: " + str(thisTRS.approved) + "<br/>"
            dataBaseContent += "Odobril: " + thisTRS.approvedBy + "(" + thisTRS.approvedDate + ")<br/>"
            
            return render_template("admin-transcripts.html", 
                user=current_user, 
                username=current_user.username, 
                dropdownOptionsRec=dropdownOptionsRec,
                hiddenSel="",
                dropdownOptionsTrs=dropdownOptionsTrs,
                hiddenEdt="",
                dataBaseContent=dataBaseContent,
                SelPog=SelPog,
                SelStd=SelStd,
                trsApproved=trsApproved,
                recID=recID,
                trsID=str(trsID),
                wide=True)

@viewAdmin.route('/admin-export-users')
@login_required
def admin_export_users():
    
    if (current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    
    else:

        updateUsersRecordingLengts()
        
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H-%M-%S")
        rootFolder = os.getcwd()
        xlsfilename = rootFolder + "/instance/users-export " + now + ".xlsx"
        workbook = xlsxwriter.Workbook(xlsfilename)
        sheet = workbook.add_worksheet()
        sheet.write(0,0,"Portal TODO")
        sheet.write(1,0,"Izpis registriranih uporabnikov")
        sheet.write(2,0,str(now))

        Allusers = database.session.query(User).all()
        format1 = workbook.add_format({'bold':True, 'bg_color':'#C6E0B4'})

        sheet.write(4,0,"ID",format1)
        sheet.write(4,1,"Admin",format1)
        sheet.write(4,2,"Ime in priimek",format1)
        sheet.write(4,3,"Uporabniško ime",format1)
        sheet.write(4,4,"Elektronski naslov",format1)
        sheet.write(4,5,"Število posnetkov",format1)
        sheet.write(4,6,"Skupna dolžina",format1)
        sheet.write(4,7,"Odobrena dolžina",format1)
        
        sheet.set_column(2,7,25)

        row = 4
        for ThisUser in Allusers:
            row = row + 1
            sheet.write(row,0,ThisUser.id)
            sheet.write(row,1,ThisUser.isAdmin)
            sheet.write(row,2,ThisUser.nameSurname)
            sheet.write(row,3,ThisUser.username)
            sheet.write(row,4,ThisUser.email)
            sheet.write(row,5,len(ThisUser.samples))
            sheet.write(row,6,cMS(ThisUser.totalRecoringsLengtMilisec))
            sheet.write(row,7,cMS(ThisUser.approvedRecoringsLengtMilisec))

        sheet.autofilter('A5:H5')

        workbook.close()
        return send_file(xlsfilename, as_attachment=True, download_name="GS - users - " + now + ".xlsx")


@viewAdmin.route('/admin-export-samples')
@login_required
def admin_export_samples():
    if (current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    else:

        AllSamples = database.session.query(Sample).all()
        AllSpeakers = database.session.query(Speaker).all()
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H-%M-%S")
        
        rootFolder = os.getcwd()
        xlsfilename = rootFolder + "/instance/samples-export " + now + ".xlsx"
        workbook = xlsxwriter.Workbook(xlsfilename)
        sheet = workbook.add_worksheet()
        sheet.write(0,0,"Portal TODO")
        sheet.write(1,0,"Izpis naloženih posnetkov")
        sheet.write(2,0,str(now))

        formatPlain = workbook.add_format()  
        formatHead = workbook.add_format({'bold':True, 'bg_color':'#C6E0B4'})
        formatLength = workbook.add_format({'num_format': 'HH:MM:SS'})
        formatDateTime = workbook.add_format({'num_format': 'YYYY-MM-DD HH:MM:SS'})

        xls_structure = [
            ["TEXT-ID","metaEditingTextID","30","formatPlain"],
            ["SOURCE-ID","metaEditingSourceID","30","formatPlain"],
            ["RECORDING-ID","metaEditingRecodingID","30","formatPlain"],
            ["SUBCORPUS","metaEditingSubcorpus","15","formatPlain"],
            ["LANGUAGE","<empty>","15","formatPlain"],
            ["MODALITY","<empty>","15","formatPlain"],
            ["TITLE","metaEditingDescription","50","formatPlain"],
            ["DATE","metaEditingDate","15","formatPlain"],
            ["SOURCE","metaEditingSource","20","formatPlain"],
            ["TEXT-REGION","metaEditingLocation","30","formatPlain"],
            ["DOMAIN","metaEditingSpeechDomain","20","formatPlain"],
            ["TYPE","metaEditingSpeechType","15","formatPlain"],
            ["CHANNEL","metaEditingChannel","15","formatPlain"],
            ["NUMBER OF \nSPEAKERS","metaUploadNoSpeakers","15","formatPlain"],
            ["SPEAKER 1","<get-spk1>","15","formatPlain"],
            ["SPEAKER 2","<get-spk2>","15","formatPlain"],
            ["SPEAKER 3","<get-spk3>","15","formatPlain"],
            ["KEYWORDS","metaEditingKeywords","30","formatPlain"],
            ["RECORDING\nDEVICE","metaEditingDevice","30","formatPlain"],
            ["RECORDING\nLOCATION","metaEditingRooms","30","formatPlain"],
            ["ORIGINAL\nFORMAT","metaTechFileFormat","15","formatPlain"],
            ["ORIGINAL\nSAMPLERATE (kHz)","<get-smplrate>","20","formatPlain"],
            ["ORIGINAL\nRESOLUTION (bit)","<get-resolution>","20","formatPlain"],
            ["ORIGINAL\nDATARATE (kbps)","<get-datarate>","20","formatPlain"],
            ["RECORDING\nQUALITY","metaEditingQuality","15","formatPlain"],
            ["URL","metaEditingURL","30","formatPlain"],
            ["LENGTH","metaTechLengthMilisec","15","formatLength"],
            ["NOTES","<empty>","30","formatPlain"],
            ["KORIGIRANO","metaEditingNameOfEditor","30","formatPlain"],
            ["CHECKED","metaEditingChecked","15","formatPlain"],
            ["APPROVED\nQUALITY","metaEditingApprovedQ","15","formatPlain"],
            ["APPROVED FOR\nTRANSCRIBING","metaEditingApprovedForT","15","formatPlain"],
            ["COMMENT FOR\nTRANSCRIBING","metaEditingCommentForT","15","formatPlain"],
            ["STARTED\nTRANSCRIBING","metaEditingStartedT","15","formatPlain"],
            ["APPROVED\nTRANSCRIPTION","metaEditingApprovedTRS","15","formatPlain"]
        ]

        i = 0
        for entry in xls_structure:
            sheet.write(6,i,entry[0],formatHead)
            sheet.set_column(i,i,int(entry[2]))
            i = i + 1
        sheet.autofilter('A7:AJ7')
        sheet.set_row(6, 30)
 
        row = 6
        for ThisSample in AllSamples:
            row = row + 1
            i = 0

            if (ThisSample.metaTechFileFormat == "WAV"):
                smplrate, resolution, datarate = formatWaveFileDataSimple(ThisSample.id)

            idOfSpeaker1 = ""
            idOfSpeaker2 = ""
            idOfSpeaker3 = ""

            for ThisSpeaker in AllSpeakers:
                if ThisSpeaker.recordingID == ThisSample.id:
                    if ThisSpeaker.recordingOrder == 1:
                        idOfSpeaker1 = ThisSpeaker.id
                    if ThisSpeaker.recordingOrder == 2:
                        idOfSpeaker2 = ThisSpeaker.id
                    if ThisSpeaker.recordingOrder == 3:
                        idOfSpeaker3 = ThisSpeaker.id

            for entry in xls_structure:
                columnName = entry[1]

                if columnName == "<empty>":
                    dataWrite = ""
                elif columnName == "<get-spk1>":
                    dataWrite = idOfSpeaker1
                elif columnName == "<get-spk2>":
                    dataWrite = idOfSpeaker2
                elif columnName == "<get-spk3>":
                    dataWrite = idOfSpeaker3
                elif columnName == "<get-smplrate>":
                    dataWrite = smplrate
                elif columnName == "<get-resolution>":
                    dataWrite = resolution
                elif columnName == "<get-datarate>":
                    dataWrite = datarate
                else:
                    dataWrite = getattr(ThisSample,columnName)

                formatNow = formatPlain
                if entry[3] == "formatLength":
                    dataWrite = dataWrite / 86400000
                    formatNow = formatLength
                
                sheet.write(row,i,dataWrite,formatNow)
                i = i + 1
        
        workbook.close()
        return send_file(xlsfilename, as_attachment=True, download_name="GS - samples - " + now + ".xlsx")


@viewAdmin.route('/admin-export-speakers')
@login_required
def admin_export_speakers():
    if (current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    else:
        
        AllSamples = database.session.query(Sample).all()
        AllSpeakers = database.session.query(Speaker).all()
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H-%M-%S")
        
        rootFolder = os.getcwd()
        xlsfilename = rootFolder + "/instance/speakers-export " + now + ".xlsx"
        workbook = xlsxwriter.Workbook(xlsfilename)
        sheet = workbook.add_worksheet()
        sheet.write(0,0,"Portal TODO")
        sheet.write(1,0,"Izpis govorcev")
        sheet.write(2,0,str(now))

        formatPlain = workbook.add_format()  
        formatHead = workbook.add_format({'bold':True, 'bg_color':'#C6E0B4'})
        formatLength = workbook.add_format({'num_format': 'HH:MM:SS'})
        formatDateTime = workbook.add_format({'num_format': 'YYYY-MM-DD HH:MM:SS'})

        xls_structure = [

            ["TEXT-ID","metaEditingTextID","30","formatPlain","REC"],
            ["SOURCE-ID","metaEditingSourceID","30","formatPlain","REC"],
            ["RECORDING-ID","metaEditingRecordingID","30","formatPlain","REC"],
            ["SUBCORPUS","metaEditingSubcorpus","20","formatPlain","REC"],
            ["IME IN PRIIMEK","metaUploadName","30","formatPlain","SPK"],
            ["PRS-ID","metaEditingPRSID","20","formatPlain","SPK"],
            ["GENDER","metaEditingGender","15","formatPlain","SPK"],
            ["AGE","metaEditingAge","15","formatPlain","SPK"],
            ["1LANG","metaEditingLanguageA","20","formatPlain","SPK"],
            ["REGISTER","metaEditingDialectType","20","formatPlain","SPK"],
            ["EDUCATION","metaEditingEducation","25","formatPlain","SPK"],
            ["PERM-RESD-SETTLEMENT","metaEditingLocationA","30","formatPlain","SPK"],
            ["PERM-RESD-STAT-REGION","metaEditingLocARegion","30","formatPlain","SPK"],
            ["PERM-RESD-COUNTRY","metaEditingLocACountry","30","formatPlain","SPK"],
            ["CHILD-RESD-SETTLEMENT","metaEditingLocationB","30","formatPlain","SPK"],
            ["CHILD-RESD-REGION","metaEditingLocBRegion","30","formatPlain","SPK"],
            ["CHILD-RESD-COUNTRY","metaEditingLocBCountry","30","formatPlain","SPK"],
            ["OTHER-RESD-SETTLEMENT","metaEditingLocationC","30","formatPlain","SPK"],
            ["OTHER-RESD-REGION","metaEditingLocCRegion","30","formatPlain","SPK"],
            ["OTHER-RESD-COUNTRY","metaEditingLocCCountry","30","formatPlain","SPK"],
            ["BILINGUAL","metaEditingBilingual","15","formatPlain","SPK"],
            ["BILING-DESCRIPTION","metaEditingLanguageB","20","formatPlain","SPK"],
            ["KORIGIRANO","metaEditingNameOfEditor","40","formatPlain","SPK"]
        ]

        i = 0
        for entry in xls_structure:
            sheet.write(6,i,entry[0],formatHead)
            sheet.set_column(i,i,int(entry[2]))
            i = i + 1
        sheet.autofilter('A7:W7')
        sheet.set_row(6, 30)


        row = 6
        for thisSpeaker in AllSpeakers:
            row = row + 1
            i = 0

            for entry in xls_structure:
                columnName = entry[1]
                dataWrite = getattr(thisSpeaker,columnName)
                formatNow = formatPlain
                sheet.write(row,i,dataWrite,formatNow)
                i = i + 1

        workbook.close()
        return send_file(xlsfilename, as_attachment=True, download_name="GS - speakers - " + now + ".xlsx")

@viewAdmin.route('/admin-export-transcripts')
@login_required
def admin_export_transcripts():
    if (current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    else:
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H-%M-%S")
        rootFolder = os.getcwd()
        xlsfilename = rootFolder + "/instance/transcripts-export " + now + ".xlsx"
        workbook = xlsxwriter.Workbook(xlsfilename)
        sheet = workbook.add_worksheet()
        sheet.write(0,0,"Portal TODO")
        sheet.write(1,0,"Izpis nabora transkripcij")
        sheet.write(2,0,str(now))

        Alltrs = database.session.query(Transcript).all()
        format1 = workbook.add_format({'bold':True, 'bg_color':'#C6E0B4'})
        format2 = workbook.add_format({'num_format': 'HH:MM:SS'})
        format3 = workbook.add_format({'num_format': 'YYYY-MM-DD HH:MM:SS'})

        sheet.write(6,0,"TRS ID",format1)
        sheet.write(6,1,"Recording ID",format1)
        sheet.write(6,2,"Tip transkripcije",format1)
        sheet.write(6,3,"Različica",format1)
        sheet.write(6,4,"Transkriptor",format1)
        sheet.write(6,5,"Odobreno",format1)
        sheet.write(6,6,"Odobril",format1)
        sheet.write(6,7,"Čas odobritve",format1)

        sheet.set_column(0,3,15)
        sheet.set_column(4,4,30)
        sheet.set_column(5,5,15)
        sheet.set_column(6,7,30)

        row = 6
        for thisTRS in Alltrs:
            row = row + 1

            if (thisTRS.trsType == 1):
                TRStip = "Pogovorna"
            elif (thisTRS.trsType == 2):
                TRStip = "Standardizirana"
            else:
                TRStip = "Neznano"

            sheet.write(row,0, thisTRS.id)
            sheet.write(row,1, thisTRS.recordingID)
            sheet.write(row,2, TRStip)
            sheet.write(row,3, thisTRS.version)
            sheet.write(row,4, thisTRS.transcriber)
            sheet.write(row,5, thisTRS.approved)
            sheet.write(row,6, thisTRS.approvedBy)
            sheet.write(row,7, thisTRS.approvedDate,format3)

        sheet.autofilter('A7:H7')
        workbook.close()
        return send_file(xlsfilename, as_attachment=True, download_name="GS - transcripts - " + now + ".xlsx")


@viewAdmin.route('/admin-dump-database')
@login_required
def dump_database():
    if(current_user.isAdmin == False):
        return redirect(url_for('viewUser.home'))
    else:
        
        output = ""
        
        try:
            output += "CLASS = USER\n"
            allClass = database.session.query(User).all()
            for dataRow in allClass:
                output += "    NEW ROW IN CLASS\n"
                for c in dataRow.__table__.columns:
                    if (c.name == "password"):
                        continue
                    output += '        '
                    output += '{}: {}\n'.format(c.name, getattr(dataRow, c.name))
            output += "\n"
        except:
            output += "CLASS = USER -- error in dumping\n"
        
        try:
            output += "CLASS = SAMPLE\n"
            allClass = database.session.query(Sample).all()
            for dataRow in allClass:
                output += "    NEW ROW IN CLASS\n"
                for c in dataRow.__table__.columns:
                    output += '        '
                    output += '{}: {}\n'.format(c.name, getattr(dataRow, c.name))
            output += "\n"
        except:
            output += "CLASS = SAMPLE -- error in dumping\n"
        
        try:
            output += "CLASS = SPEAKER\n"
            allClass = database.session.query(Speaker).all()
            for dataRow in allClass:
                output += "    NEW ROW IN CLASS\n"
                for c in dataRow.__table__.columns:
                    output += '        '
                    output += '{}: {}\n'.format(c.name, getattr(dataRow, c.name))
            output += "\n"
        except:
            output += "CLASS = SPEAKER -- error in dumping\n"

        try:
            output += "CLASS = TRANSCRIPT\n"
            allClass = database.session.query(Transcript).all()
            for dataRow in allClass:
                output += "    NEW ROW IN CLASS\n"
                for c in dataRow.__table__.columns:
                    output += '        '
                    output += '{}: {}\n'.format(c.name, getattr(dataRow, c.name))
            output += "\n"
        except:
            output += "CLASS = TRANSCRIPT -- error in dumping\n"
        
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d-%H-%M-%S")
        rootFolder = os.getcwd()
        filename= rootFolder + "/instance/dump-" + now + ".txt"
        with open(filename, "ab") as fM:
            fM.write(str.encode(output))

        return send_file(filename, as_attachment=True)


@viewAdmin.route('/admin-pass-change', methods=['GET', 'POST'])
@login_required
def admin_pass_change():

    maxID = database.session.query(User).count()
    dropdownOptions=""
    for i in range (1,maxID+1):
        dropdownOptions += "<option value=" + str(i) + ">" + str(i) + " - "
        dropdownOptions += html.escape(str(User.query.get(i).nameSurname)) + " - "
        dropdownOptions += html.escape(str(User.query.get(i).username))
        dropdownOptions += "</option>\n"

    if(current_user.id > 1):
        return redirect(url_for('viewUser.home'))
    
    elif request.method == 'GET':
        return render_template("PassEdit.html", 
            user=current_user, 
            username=current_user.username, 
            dropdownOptions=dropdownOptions,
            wide=False)
    
    else:
        userID = int(request.form.get('ID'))
        if (userID == 1):
            flash("NOPE", category='error')
            return render_template("PassEdit.html", 
            user=current_user, 
            username=current_user.username, 
            dropdownOptions=dropdownOptions,
            wide=False)
        
        newPass = str(request.form.get('PASS'))
        password = generate_password_hash(newPass, method='pbkdf2:sha256:1234987', salt_length=16)
        user = User.query.filter_by(id=userID).first()
        user.password = password
        database.session.commit()
        flash("OK", category='success')
        return render_template("PassEdit.html", 
            user=current_user, 
            username=current_user.username, 
            dropdownOptions=dropdownOptions,
            wide=False)
