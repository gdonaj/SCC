import os
from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user

from . import database
from .dbModels import Sample, Transcript
from .util import convTF

app = Flask(__name__)

viewTranscriber = Blueprint('viewTranscriber', __name__)

@viewTranscriber.route('/transcribe', methods=['GET', 'POST'])
@login_required
def transcriber():

    if(current_user.isTranscriber == False):
        return redirect(url_for('viewUser.home'))
    
    else:

        maxID = database.session.query(Sample).count()
        dropdownOptions=""
        for i in range (1,maxID+1):
            dropdownOptions += "<option value=" + str(i) + ">" + str(i)
            dropdownOptions += "</option>\n"

        if request.method == 'GET':
            return render_template("transcriber.html",
                user=current_user, 
                username=current_user.username, 
                dropdownOptions=dropdownOptions,
                dropdownOptionsTRS="",
                hiddenDiv="hidden",
                showID="0",
                trdData="",
                wide=True)
        
        showID = 0
        if ("showSample" in request.form):
            showID = int(request.form.get('idSelect'))
            if (showID == 0):
                flash("Izberite posnetek", category='error')
                return render_template("transcriber.html",
                    user=current_user, 
                    username=current_user.username, 
                    dropdownOptions=dropdownOptions,
                    dropdownOptionsTRS="",
                    hiddenDiv="hidden",
                    showID="0",
                    trdData="",
                    wide=True)

        elif ("showPrev" in request.form):
            showID = int(request.form.get('currentID'))-1
            if (showID < 1):
                showID = maxID

        elif ("showNext" in request.form):
            showID = int(request.form.get('currentID'))+1
            if (showID > maxID):
                showID = 1

        if ("dwnlFile" in request.form):
            showID = int(request.form.get('currentID'))
            dataFolder = os.getcwd() + "/database/"
            fileAudio = dataFolder + Sample.query.get(showID).metaTechFilenameWave
            if (request.form.get('startTRS')=="on"):
                Sample.query.get(showID).metaEditingStartedT = True
                database.session.commit()
            return send_file(fileAudio, as_attachment=True)

        if ("trsDownload" in request.form):
            showID = int(request.form.get('currentID'))
            dataFolder = os.getcwd() + "/database/"
            trsID = int(request.form.get('trsSelect'))
            fileTRS = dataFolder + Transcript.query.get(trsID).fileName
            return send_file(fileTRS, as_attachment=True)
        
        if ("changeFile" in request.form):
            showID = int(request.form.get('currentID'))
            trsFile = request.files['formTRSFile']
            OriginalFilename, OriginalFile_extension = os.path.splitext(trsFile.filename)
            OriginalFile_extension = OriginalFile_extension.lower()
            
            maxversion = 0
            maxTRS = database.session.query(Transcript).count()
            for i in range (1,maxTRS+1):
                if Transcript.query.get(i).recordingID == showID:
                    version = Transcript.query.get(i).version
                    if (version > maxversion):
                        maxversion = version

            trsType = 0
            trsTypeS = request.form.get('trsType')
            print(" ")
            print(trsType)
            print(trsTypeS)
            print(" ")
            if (trsTypeS == "pogovorna"):
                trsType = 1
            elif (trsTypeS == "standardizirana"):
                trsType = 2
            print(trsType)
            print(" ")
            print(" ------------------ ")
            
            newfilename  = "GSo-P" + str(request.form.get('currentID')).zfill(4) + "."
            newfilename += "v" + str(maxversion+1).zfill(4) + "." + str(trsType) + OriginalFile_extension
            trsFile.save(os.getcwd() + "/database/" + newfilename)
            thisTRS = Transcript(
                recordingID = request.form.get('currentID'),
                trsType = trsType,
                version = (maxversion+1),
                fileName = newfilename,
                transcriber = current_user.nameSurname + " (" + current_user.username + ")",
                approved = False,
                approvedBy = "",
                approvedDate = "")
            
            database.session.add(thisTRS)
            database.session.commit()
            flash('Transkripcija je bila uspešno naložena', category='success')

        dropdownOptionsTRS=""
        maxTRS = database.session.query(Transcript).count()
        j = 0
        maxversion = 0
        for i in range (1,maxTRS+1):
            if Transcript.query.get(i).recordingID == showID:
                j += 1
                version = Transcript.query.get(i).version
                if (version > maxversion):
                    maxversion = version
                ime = str(j) + " - različica " + str(version) + " - "
                if (Transcript.query.get(i).trsType == 1):
                    ime += "Pogovorna"
                elif (Transcript.query.get(i).trsType == 2):
                    ime += "Standardizirana"
                dropdownOptionsTRS += "<option value=" + str(i) + ">" + ime
                dropdownOptionsTRS += "</option>\n"

        trdData = ""
        # trdData += "ID: " + str(Sample.query.get(showID).id) + "<br />"
        trdData += "Podkorpus: " + Sample.query.get(showID).metaEditingSubcorpus + "<br />"
        trdData += "Opis: " + Sample.query.get(showID).metaEditingDescription + "<br />"
        trdData += "Odobrena kvaliteta: " + convTF(Sample.query.get(showID).metaEditingApprovedQ) + "<br />"
        trdData += "<b>"
        trdData += "Odobren za transkripcijo: " + convTF(Sample.query.get(showID).metaEditingApprovedForT) + "<br />"
        trdData += "</b>"
        trdData += "Začeta transkripcija: " + convTF(Sample.query.get(showID).metaEditingStartedT) + "<br />"
        trdData += "Odobrena transkripcija: " + convTF(Sample.query.get(showID).metaEditingApprovedTRS) + "<br />"
        trdData += "<br /><b>"
        trdData += "Komentar za transkriptorja: " + Sample.query.get(showID).metaEditingCommentForT + "<br />"
        trdData += "</b>"
        
        return render_template("transcriber.html",
            user=current_user, 
            username=current_user.username, 
            dropdownOptions=dropdownOptions,
            dropdownOptionsTRS=dropdownOptionsTRS,
            hiddenDiv="",
            showID=showID,
            trdData=trdData,
            wide=True)
    
