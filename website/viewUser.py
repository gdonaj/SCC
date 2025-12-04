import os
import datetime
import librosa
from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from . import database
from .dbModels import Sample, Speaker
from .util import *


app = Flask(__name__)
viewUser = Blueprint('viewUser', __name__)


@viewUser.route('/view')
@login_required
def view():

    app.logger.info('Uporabnik pogledal svoje podatke: '+current_user.username)

    numAll = 0
    lenAll = 0
    numApr = 0
    lenApr = 0

    samplesList = ""

    allSamples = database.session.query(Sample).all()
    for sample in allSamples:
        if sample.userID == current_user.id:
            samplesList = samplesList + "<ul>"
            samplesList = samplesList + "ID = " + str(sample.id) + "<br />"
            samplesList = samplesList + "Naloženo = " + str(sample.uploadDate) + "<br />"
            samplesList = samplesList + "Dolžina = " + cMS(sample.metaTechLengthMilisec) + "<br />"
            numAll = numAll + 1
            lenAll = lenAll + sample.metaTechLengthMilisec
            if sample.metaEditingChecked == True:
                samplesList = samplesList + "Pregledan = DA <br />"
            else:
                samplesList = samplesList + "Pregledan = NE <br />"
            if sample.metaEditingApprovedQ == True:
                samplesList = samplesList + "Odobren = DA <br />"
                numApr = numApr + 1
                lenApr = lenApr + sample.metaEditingLengthAprv
            else:
                samplesList = samplesList + "Odobren = NE <br />"
            samplesList = samplesList + "Odobrena dolžina = " + cMS(sample.metaEditingLengthAprv) + "<br />"
            samplesList = samplesList + "</ul>"

    if (lenApr >= 40000000):
        prize = "da (5x)"
    elif (lenApr >= 36000000):
        prize = "da (4x)"
    elif (lenApr >= 27000000):
        prize = "da (3x)"
    elif (lenApr >= 18000000):
        prize = "da (2x)"
    elif (lenApr >=  9000000):
        prize = "da"
    else:
        prize = "ne"

    return render_template("view.html", 
                           user=current_user, 
                           numAll=numAll,
                           lenAll=cMS(lenAll),
                           numApr=numApr,
                           lenApr=cMS(lenApr),
                           samplesList=samplesList,
                           prize=prize
                           )


@viewUser.route('/success')
@login_required
def success():
    id = request.args.get('id')
    app.logger.info('Uporabnik uspešno zakljucil nalaganje in bil preusmerjen: ' + current_user.username)
    return render_template("success.html", user=current_user, id=id)


@viewUser.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        
        app.logger.info("Nalaganje posnetka ...")
        app.logger.info(" - uporabnik = " + current_user.username)
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d-%H-%M-%S")
        
        ################################ Numerical data from form to string ################################

        numberSpeakers= int(request.form.get('stGovorcev'))

        tmpSpeechChannelForm = str(request.form.get('formAF_channel'))
        tmpSpeechChannel = ""

        if (tmpSpeechChannelForm == "1"):
            tmpSpeechChannel = "Osebni stik"
        elif (tmpSpeechChannelForm == "2"):
            tmpSpeechChannel = "Avdio na daljavo"
        elif (tmpSpeechChannelForm == "3"):
            tmpSpeechChannel = "Video na daljavo"
        else:
            tmpSpeechChannel = "NAPAKA - " + tmpSpeechChannelForm

        tmpSpeechTypeForm = str(request.form.get('formAF_speech'))
        tmpSpeechType = ""
        
        if (tmpSpeechTypeForm == None):
            tmpSpeechType = "Ni podatka (napaka?)"
        elif (tmpSpeechTypeForm == "1"):
            tmpSpeechType = "Družabni pogovor"
        elif (tmpSpeechTypeForm == "2"):
            tmpSpeechType = "Intervju"
        elif (tmpSpeechTypeForm == "3"):
            tmpSpeechType = "Diskusija"
        elif (tmpSpeechTypeForm == "4"):
            tmpSpeechType = "Navodila"
        elif (tmpSpeechTypeForm == "5"):
            tmpSpeechType = "Pripoved"
        elif (tmpSpeechTypeForm == "6"):
            tmpSpeechType = "Razlaga"

        tmpSpeechSourceForm = str(request.form.get('formAF_source'))
        tmpSpeechSource = ""
        tmpSubcorpus = ""

        if (tmpSpeechSourceForm == None):
            tmpSpeechSource = "Ni podatka (napaka?)"
        elif (tmpSpeechSourceForm == "1"):
            tmpSpeechSource = "Doniran posnetek"
            tmpSubcorpus = "GosObcan"
        elif (tmpSpeechSourceForm == "2"):
            tmpSpeechSource = "Naročen posnetek"
            tmpSubcorpus = "GosObcan"
        
        ################################ Prepeare entry to database ################################

        thisSample = Sample(
            
            userID = current_user.id,
            
            metaUploadNoSpeakers  = request.form.get('stGovorcev'),
            metaUploadSource      = request.form.get('formAF_source'),
            metaUploadLocation    = request.form.get('formAF_location'),
            metaUploadRooms       = request.form.get('formAF_room'),
            metaUploadDate        = request.form.get('formAF_date'),
            metaUploadChannel     = request.form.get('formAF_channel'),
            metaUploadSpeechType  = request.form.get('formAF_speech'),
            metaUploadTool        = request.form.get('formAF_tool'),
            metaUploadDescription = request.form.get('formAF_description'),
            metaUploadKeyWords    = request.form.get('formAF_keywords'),

            metaTechFileSizeBytes = 0,
            metaTechFileFormat    = "",
            metaTechLengthMilisec = 0,
            metaTechFilenameWave  = "",
            metaTechFilenameFrmA  = "",
            metaTechFilenameFrmB  = "",
            metaTechFilenameFrmC  = "",
            metaTechFilenameMeta  = "",

            metaEditingTextID        = "",
            metaEditingSourceID      = "",
            metaEditingRecodingID    = "",
            metaEditingSubcorpus     = tmpSubcorpus,
            metaEditingDescription   = str(request.form.get('formAF_description')),
            metaEditingDate          = str(request.form.get('formAF_date')),
            metaEditingSource        = tmpSpeechSource,
            metaEditingLocation      = str(request.form.get('formAF_location')),
            metaEditingSpeechDomain  = tmpSpeechType,
            metaEditingSpeechType    = "Zasebni",
            metaEditingChannel       = tmpSpeechChannel,
            metaEditingKeywords      = str(request.form.get('formAF_keywords')),
            metaEditingDevice        = str(request.form.get('formAF_tool')),
            metaEditingRooms         = str(request.form.get('formAF_room')),
            metaEditingQuality       = 0,
            metaEditingURL           = "",
            metaEditingLengthAprv    = 0,
            metaEditingChecked       = False,
            metaEditingApprovedQ     = False,
            metaEditingApprovedForT  = False,
            metaEditingEditorComment = "",
            metaEditingCommentForT   = "",
            metaEditingStartedT      = False,
            metaEditingApprovedTRS   = False,
            metaEditingNameOfEditor  = "",

        )

        database.session.add(thisSample)
        database.session.commit()

        thisSampleID = thisSample.id
        SourceID = "GSo-P" + str(thisSampleID).zfill(4)

        ################################ Save files ################################

        newfilenameA = "<none>"
        newfilename1 = "<none>"
        newfilename2 = "<none>"
        newfilename3 = "<none>"
        newfilenameM = "<none>"
        newfilenameU = "<none>"

        rootFolder = os.getcwd()
        databaseFolder = rootFolder + "/database/"

        fA = request.files['formAF_FILE']
        newfilenameA= databaseFolder + "GSO-P" + str(thisSampleID).zfill(4) + "-" + now + "-Audio-" + fA.filename
        fA.save(newfilenameA)

        fileS1 = request.files['formS1_FILE']
        newfilename1= databaseFolder + "GSO-P" + str(thisSampleID).zfill(4) + "-" + now + "-Speaker1-" + fileS1.filename
        fileS1.save(newfilename1)

        if (numberSpeakers >= 2):
            fileS2 = request.files['formS2_FILE']
            newfilename2= databaseFolder + "GSO-P" + str(thisSampleID).zfill(4) + "-" + now + "-Speaker2-" + fileS2.filename
            fileS2.save(newfilename2)

        if (numberSpeakers >= 3):
            fileS3 = request.files['formS3_FILE']
            newfilename3= databaseFolder + "GSO-P" + str(thisSampleID).zfill(4) + "-" + now + "-Speaker3-" + fileS3.filename
            fileS3.save(newfilename3)

        newfilenameM = databaseFolder + "GSO-P" + str(thisSampleID).zfill(4) + "-" + now + "-Metadata.txt"
        newfilenameU = databaseFolder + "GSO-P" + str(thisSampleID).zfill(4) + "-" + now + "-MetadataUploader.txt"

        print (newfilenameA)
        print (newfilenameA.split('/', 1)[-1])

        thisSample.metaTechFilenameWave=newfilenameA.split('/')[-1]
        thisSample.metaTechFilenameFrmA=newfilename1.split('/')[-1]
        thisSample.metaTechFilenameFrmB=newfilename2.split('/')[-1]
        thisSample.metaTechFilenameFrmC=newfilename3.split('/')[-1]
        thisSample.metaTechFilenameMeta=newfilenameM.split('/')[-1]

        thisSample.metaEditingSourceID = SourceID

        ################################ Technical metadata ################################

        tempFileSize = os.path.getsize(newfilenameA)
        thisSample.metaTechFileSizeBytes = tempFileSize

        tempFileFormat = os.path.splitext(newfilenameA)[1][1:].upper()
        thisSample.metaTechFileFormat = tempFileFormat

        if (tempFileFormat == "WAV"):
            tempLength = int(librosa.get_duration(filename=newfilenameA)*1000)
            thisSample.metaTechLengthMilisec = tempLength

        database.session.commit()

        ################################ Metadata 1st speaker ################################

        tmpEducationForm = request.form.get('formS1_education')
        tmpEducation = ""
        
        if (tmpEducationForm == "1"):
            tmpEducation = "Osnovnošolska ali manj"
        elif (tmpEducationForm == "2"):
            tmpEducation = "Srednješolska"
        elif (tmpEducationForm == "3"):
            tmpEducation = "Višješolska ali visokošolska strokovna"
        elif (tmpEducationForm == "4"):
            tmpEducation = "Univerzitetna ali več"
        elif (tmpEducationForm == "NoAns"):
            tmpEducation = "Ne želim odgovoriti"
        elif (tmpEducationForm == None):
            tmpEducation = "Ni odgovora"
        else:
            tmpEducation = "NAPAKA - " + str(tmpEducationForm)
        
        tmpGender = ""
        tmpGenderForm = request.form.get('formS1_genderSEL')
        if (tmpGenderForm == "male"):
            tmpGender = "Moški"
        elif (tmpGenderForm == "female"):
            tmpGender = "Ženski"
        elif (tmpGenderForm == "NoAns"):
            tmpGender = "Ne želim odgovoriti"
        elif (tmpGenderForm == "oth"):
            tmpGender = request.form.get('formS1_genderWRITE')
        else:
            tmpGender = "NAPAKA - " + str(tmpGenderForm) 
            tmpGender += " - " + str(request.form.get('formS1_genderWRITE'))

        tmpLanguageA = ""
        tmpLanguageFormSLO = request.form.get('formS1_firstLangSlo')
        tmpLanguageFormSEL = request.form.get('formS1_firstLangSEL')
        tmpLanguageFormWRT = request.form.get('formS1_firstLangWRITE')
        
        if (tmpLanguageFormSLO == "SL"):
            tmpLanguageA = "SL"
        elif (tmpLanguageFormSLO == "NoAns"):
            tmpLanguageA = "Ne želim odgovoriti"
        elif (tmpLanguageFormSLO == "XX"):
            if (tmpLanguageFormSEL == "0"):
                tmpLanguageA = "NAPAKA - " + str(tmpLanguageFormSLO)
                tmpLanguageA += " - " + str(tmpLanguageFormSEL)
                tmpLanguageA += " - " + str(tmpLanguageFormWRT)
            elif (tmpLanguageFormSEL == "XX"):
                tmpLanguageA = tmpLanguageFormWRT
            else:
                tmpLanguageA = tmpLanguageFormSEL
        elif (tmpLanguageFormSLO == None):
            tmpLanguageA = "Ni odgovora"
        elif (tmpLanguageFormSEL == None):
            tmpLanguageA = "Ni odgovora"
        else:
            tmpLanguageA = "NAPAKA - " + str(tmpLanguageFormSLO)
            tmpLanguageA += " - " + str(tmpLanguageFormSEL)
            tmpLanguageA += " - " + str(tmpLanguageFormWRT)

        tmpBilingual = ""
        tmpBilingualForm = request.form.get('formS1_addLangTF')
        if (tmpBilingualForm == "true"):
            tmpBilingual = "Da"
        elif (tmpBilingualForm == "false"):
            tmpBilingual = "Ne"
        elif (tmpBilingualForm == "NoAns"):
            tmpBilingual = "Ne želim odgovoriti"
        elif (tmpBilingualForm == None):
            tmpBilingual = "Ni odgovora"
        else:
            tmpBilingual = "NAPAKA - " + str(tmpBilingualForm)
        
        tmpLanguageB = ""
        tmpLanguageBFormSEL = request.form.get('formS1_addLangSEL')
        tmpLanguageBFormWRT = request.form.get('formS1_addLangWRITE')

        if (tmpLanguageBFormSEL == "0"):
            tmpLanguageB = "NAPAKA - " + str(tmpLanguageBFormSEL)
            tmpLanguageB += " - " + str(tmpLanguageBFormWRT)
        elif (tmpLanguageBFormSEL == "XX"):
            tmpLanguageB = tmpLanguageBFormWRT
        else:
            tmpLanguageB = tmpLanguageBFormSEL

        thisSpeakerA = Speaker(
            recordingID = thisSampleID,
            recordingOrder = 1,
            bindingID = 0,
            
            metaUploadGender     = tmpGender,
            metaUploadEducation  = tmpEducation,
            metaUploadBilingual  = tmpBilingual,
            metaUploadLanguageA  = tmpLanguageA,
            metaUploadLanguageB  = tmpLanguageB,

            metaUploadName       = request.form.get('formS1_name'),
            metaUploadAge        = request.form.get('formS1_age'),
            metaUploadLocationA  = request.form.get('formS1_locationA'),
            metaUploadLocationB  = request.form.get('formS1_locationB'),
            metaUploadLocationC  = request.form.get('formS1_locationC'),

            metaEditingGender    = tmpGender,
            metaEditingLanguageA = tmpLanguageA,
            metaEditingEducation = tmpEducation,
            metaEditingBilingual = tmpBilingual,
            metaEditingLanguageB = tmpLanguageB,

            metaEditingAge       = request.form.get('formS1_age'),
            metaEditingLocationA = request.form.get('formS1_locationA'),
            metaEditingLocationB = request.form.get('formS1_locationB'),
            metaEditingLocationC = request.form.get('formS1_locationC'),
            
            metaEditingSourceID = SourceID,
            metaEditingSubcorpus = tmpSubcorpus,

            metaEditingTextID = "",
            metaEditingRecordingID = "",
            metaEditingPRSID = SourceID + "-G1",
            metaEditingDialectType = "",
            metaEditingDialectGRP = "",
            metaEditingDialect = "",
            metaEditingLocARegion = "",
            metaEditingLocACountry = "",
            metaEditingLocBRegion = "",
            metaEditingLocBCountry = "",
            metaEditingLocCRegion = "",
            metaEditingLocCCountry = "",
            metaEditingNameOfEditor = "",
            metaEditingLastEditTime = "",
        )

        if (thisSpeakerA.metaEditingLocationA == ""):
            thisSpeakerA.metaEditingLocationA = "None"
            thisSpeakerA.metaEditingLocARegion = "None"
            thisSpeakerA.metaEditingLocACountry = "None"
        
        if (thisSpeakerA.metaEditingLocationB == ""):
            thisSpeakerA.metaEditingLocationB = "None"
            thisSpeakerA.metaEditingLocBRegion = "None"
            thisSpeakerA.metaEditingLocBCountry = "None"

        if (thisSpeakerA.metaEditingLocationC == ""):
            thisSpeakerA.metaEditingLocationC = "None"
            thisSpeakerA.metaEditingLocCRegion = "None"
            thisSpeakerA.metaEditingLocCCountry = "None"

        database.session.add(thisSpeakerA)
        database.session.commit()
            
        ################################ Metadata 2nd speaker ################################

        if (numberSpeakers >= 2):

            tmpEducationForm = request.form.get('formS2_education')
            tmpEducation = ""
            
            if (tmpEducationForm == "1"):
                tmpEducation = "Osnovnošolska ali manj"
            elif (tmpEducationForm == "2"):
                tmpEducation = "Srednješolska"
            elif (tmpEducationForm == "3"):
                tmpEducation = "Višješolska ali visokošolska strokovna"
            elif (tmpEducationForm == "4"):
                tmpEducation = "Univerzitetna ali več"
            elif (tmpEducationForm == "NoAns"):
                tmpEducation = "Ne želim odgovoriti"
            elif (tmpEducationForm == None):
                tmpEducation = "Ni odgovora"
            else:
                tmpEducation = "NAPAKA - " + str(tmpEducationForm)
            
            tmpGender = ""
            tmpGenderForm = request.form.get('formS2_genderSEL')
            if (tmpGenderForm == "male"):
                tmpGender = "Moški"
            elif (tmpGenderForm == "female"):
                tmpGender = "Ženski"
            elif (tmpGenderForm == "NoAns"):
                tmpGender = "Ne želim odgovoriti"
            elif (tmpGenderForm == "oth"):
                tmpGender = request.form.get('formS2_genderWRITE')
            else:
                tmpGender = "NAPAKA - " + str(tmpGenderForm) 
                tmpGender += " - " + str(request.form.get('formS2_genderWRITE'))

            tmpLanguageA = ""
            tmpLanguageFormSLO = request.form.get('formS2_firstLangSlo')
            tmpLanguageFormSEL = request.form.get('formS2_firstLangSEL')
            tmpLanguageFormWRT = request.form.get('formS2_firstLangWRITE')
            
            if (tmpLanguageFormSLO == "SL"):
                tmpLanguageA = "SL"
            elif (tmpLanguageFormSLO == "NoAns"):
                tmpLanguageA = "Ne želim odgovoriti"
            elif (tmpLanguageFormSLO == "XX"):
                if (tmpLanguageFormSEL == "0"):
                    tmpLanguageA = "NAPAKA - " + str(tmpLanguageFormSLO)
                    tmpLanguageA += " - " + str(tmpLanguageFormSEL)
                    tmpLanguageA += " - " + str(tmpLanguageFormWRT)
                elif (tmpLanguageFormSEL == "XX"):
                    tmpLanguageA = tmpLanguageFormWRT
                else:
                    tmpLanguageA = tmpLanguageFormSEL
            elif (tmpLanguageFormSLO == None):
                tmpLanguageA = "Ni odgovora"
            elif (tmpLanguageFormSEL == None):
                tmpLanguageA = "Ni odgovora"
            else:
                tmpLanguageA = "NAPAKA - " + str(tmpLanguageFormSLO)
                tmpLanguageA += " - " + str(tmpLanguageFormSEL)
                tmpLanguageA += " - " + str(tmpLanguageFormWRT)

            tmpBilingual = ""
            tmpBilingualForm = request.form.get('formS2_addLangTF')
            if (tmpBilingualForm == "true"):
                tmpBilingual = "Da"
            elif (tmpBilingualForm == "false"):
                tmpBilingual = "Ne"
            elif (tmpBilingualForm == "NoAns"):
                tmpBilingual = "Ne želim odgovoriti"
            elif (tmpBilingualForm == None):
                tmpBilingual = "Ni odgovora"
            else:
                tmpBilingual = "NAPAKA - " + str(tmpBilingualForm)
            
            tmpLanguageB = ""
            tmpLanguageBFormSEL = request.form.get('formS2_addLangSEL')
            tmpLanguageBFormWRT = request.form.get('formS2_addLangWRITE')

            if (tmpLanguageBFormSEL == "0"):
                tmpLanguageB = "NAPAKA - " + str(tmpLanguageBFormSEL)
                tmpLanguageB += " - " + str(tmpLanguageBFormWRT)
            elif (tmpLanguageBFormSEL == "XX"):
                tmpLanguageB = tmpLanguageBFormWRT
            else:
                tmpLanguageB = tmpLanguageBFormSEL

            thisSpeakerA = Speaker(
                recordingID = thisSampleID,
                recordingOrder = 2,
                bindingID = 0,
                
                metaUploadGender     = tmpGender,
                metaUploadEducation  = tmpEducation,
                metaUploadBilingual  = tmpBilingual,
                metaUploadLanguageA  = tmpLanguageA,
                metaUploadLanguageB  = tmpLanguageB,

                metaUploadName       = request.form.get('formS2_name'),
                metaUploadAge        = request.form.get('formS2_age'),
                metaUploadLocationA  = request.form.get('formS2_locationA'),
                metaUploadLocationB  = request.form.get('formS2_locationB'),
                metaUploadLocationC  = request.form.get('formS2_locationC'),

                metaEditingGender    = tmpGender,
                metaEditingLanguageA = tmpLanguageA,
                metaEditingEducation = tmpEducation,
                metaEditingBilingual = tmpBilingual,
                metaEditingLanguageB = tmpLanguageB,

                metaEditingAge       = request.form.get('formS2_age'),
                metaEditingLocationA = request.form.get('formS2_locationA'),
                metaEditingLocationB = request.form.get('formS2_locationB'),
                metaEditingLocationC = request.form.get('formS2_locationC'),
                
                metaEditingTextID = "",
                metaEditingSourceID = SourceID,
                metaEditingRecordingID = "",
                metaEditingSubcorpus = tmpSubcorpus,
                metaEditingPRSID = SourceID + "-G2",
                metaEditingDialectType = "",
                metaEditingDialectGRP = "",
                metaEditingDialect = "",
                metaEditingLocARegion = "",
                metaEditingLocACountry = "",
                metaEditingLocBRegion = "",
                metaEditingLocBCountry = "",
                metaEditingLocCRegion = "",
                metaEditingLocCCountry = "",
                metaEditingNameOfEditor = "",
                metaEditingLastEditTime = "",
            )

            if (thisSpeakerA.metaEditingLocationA == ""):
                thisSpeakerA.metaEditingLocationA = "None"
                thisSpeakerA.metaEditingLocARegion = "None"
                thisSpeakerA.metaEditingLocACountry = "None"
        
            if (thisSpeakerA.metaEditingLocationB == ""):
                thisSpeakerA.metaEditingLocationB = "None"
                thisSpeakerA.metaEditingLocBRegion = "None"
                thisSpeakerA.metaEditingLocBCountry = "None"

            if (thisSpeakerA.metaEditingLocationC == ""):
                thisSpeakerA.metaEditingLocationC = "None"
                thisSpeakerA.metaEditingLocCRegion = "None"
                thisSpeakerA.metaEditingLocCCountry = "None"

            database.session.add(thisSpeakerA)
            database.session.commit()

        ################################ Metadata 3rd speaker ################################

        if(numberSpeakers >= 3):

            tmpEducationForm = request.form.get('formS3_education')
            tmpEducation = ""
            
            if (tmpEducationForm == "1"):
                tmpEducation = "Osnovnošolska ali manj"
            elif (tmpEducationForm == "2"):
                tmpEducation = "Srednješolska"
            elif (tmpEducationForm == "3"):
                tmpEducation = "Višješolska ali visokošolska strokovna"
            elif (tmpEducationForm == "4"):
                tmpEducation = "Univerzitetna ali več"
            elif (tmpEducationForm == "NoAns"):
                tmpEducation = "Ne želim odgovoriti"
            elif (tmpEducationForm == None):
                tmpEducation = "Ni odgovora"
            else:
                tmpEducation = "NAPAKA - " + str(tmpEducationForm)
            
            tmpGender = ""
            tmpGenderForm = request.form.get('formS3_genderSEL')
            if (tmpGenderForm == "male"):
                tmpGender = "Moški"
            elif (tmpGenderForm == "female"):
                tmpGender = "Ženski"
            elif (tmpGenderForm == "NoAns"):
                tmpGender = "Ne želim odgovoriti"
            elif (tmpGenderForm == "oth"):
                tmpGender = request.form.get('formS3_genderWRITE')
            else:
                tmpGender = "NAPAKA - " + str(tmpGenderForm) 
                tmpGender += " - " + str(request.form.get('formS3_genderWRITE'))

            tmpLanguageA = ""
            tmpLanguageFormSLO = request.form.get('formS3_firstLangSlo')
            tmpLanguageFormSEL = request.form.get('formS3_firstLangSEL')
            tmpLanguageFormWRT = request.form.get('formS3_firstLangWRITE')
            
            if (tmpLanguageFormSLO == "SL"):
                tmpLanguageA = "SL"
            elif (tmpLanguageFormSLO == "NoAns"):
                tmpLanguageA = "Ne želim odgovoriti"
            elif (tmpLanguageFormSLO == "XX"):
                if (tmpLanguageFormSEL == "0"):
                    tmpLanguageA = "NAPAKA - " + str(tmpLanguageFormSLO)
                    tmpLanguageA += " - " + str(tmpLanguageFormSEL)
                    tmpLanguageA += " - " + str(tmpLanguageFormWRT)
                elif (tmpLanguageFormSEL == "XX"):
                    tmpLanguageA = tmpLanguageFormWRT
                else:
                    tmpLanguageA = tmpLanguageFormSEL
            elif (tmpLanguageFormSLO == None):
                tmpLanguageA = "Ni odgovora"
            elif (tmpLanguageFormSEL == None):
                tmpLanguageA = "Ni odgovora"
            else:
                tmpLanguageA = "NAPAKA - " + str(tmpLanguageFormSLO)
                tmpLanguageA += " - " + str(tmpLanguageFormSEL)
                tmpLanguageA += " - " + str(tmpLanguageFormWRT)

            tmpBilingual = ""
            tmpBilingualForm = request.form.get('formS3_addLangTF')
            if (tmpBilingualForm == "true"):
                tmpBilingual = "Da"
            elif (tmpBilingualForm == "false"):
                tmpBilingual = "Ne"
            elif (tmpBilingualForm == "NoAns"):
                tmpBilingual = "Ne želim odgovoriti"
            elif (tmpBilingualForm == None):
                tmpBilingual = "Ni odgovora"
            else:
                tmpBilingual = "NAPAKA - " + str(tmpBilingualForm)
            
            tmpLanguageB = ""
            tmpLanguageBFormSEL = request.form.get('formS3_addLangSEL')
            tmpLanguageBFormWRT = request.form.get('formS3_addLangWRITE')

            if (tmpLanguageBFormSEL == "0"):
                tmpLanguageB = "NAPAKA - " + str(tmpLanguageBFormSEL)
                tmpLanguageB += " - " + str(tmpLanguageBFormWRT)
            elif (tmpLanguageBFormSEL == "XX"):
                tmpLanguageB = tmpLanguageBFormWRT
            else:
                tmpLanguageB = tmpLanguageBFormSEL

            thisSpeakerA = Speaker(
                recordingID = thisSampleID,
                recordingOrder = 3,
                bindingID = 0,
                
                metaUploadGender     = tmpGender,
                metaUploadEducation  = tmpEducation,
                metaUploadBilingual  = tmpBilingual,
                metaUploadLanguageA  = tmpLanguageA,
                metaUploadLanguageB  = tmpLanguageB,

                metaUploadName       = request.form.get('formS3_name'),
                metaUploadAge        = request.form.get('formS3_age'),
                metaUploadLocationA  = request.form.get('formS3_locationA'),
                metaUploadLocationB  = request.form.get('formS3_locationB'),
                metaUploadLocationC  = request.form.get('formS3_locationC'),

                metaEditingGender    = tmpGender,
                metaEditingLanguageA = tmpLanguageA,
                metaEditingEducation = tmpEducation,
                metaEditingBilingual = tmpBilingual,
                metaEditingLanguageB = tmpLanguageB,

                metaEditingAge       = request.form.get('formS3_age'),
                metaEditingLocationA = request.form.get('formS3_locationA'),
                metaEditingLocationB = request.form.get('formS3_locationB'),
                metaEditingLocationC = request.form.get('formS3_locationC'),
                
                metaEditingTextID = "",
                metaEditingSourceID = SourceID,
                metaEditingRecordingID = "",
                metaEditingSubcorpus = tmpSubcorpus,
                metaEditingPRSID = SourceID + "-G3",
                metaEditingDialectType = "",
                metaEditingDialectGRP = "",
                metaEditingDialect = "",
                metaEditingLocARegion = "",
                metaEditingLocACountry = "",
                metaEditingLocBRegion = "",
                metaEditingLocBCountry = "",
                metaEditingLocCRegion = "",
                metaEditingLocCCountry = "",
                metaEditingNameOfEditor = "",
                metaEditingLastEditTime = "",
            )

            if (thisSpeakerA.metaEditingLocationA == ""):
                thisSpeakerA.metaEditingLocationA = "None"
                thisSpeakerA.metaEditingLocARegion = "None"
                thisSpeakerA.metaEditingLocACountry = "None"
        
            if (thisSpeakerA.metaEditingLocationB == ""):
                thisSpeakerA.metaEditingLocationB = "None"
                thisSpeakerA.metaEditingLocBRegion = "None"
                thisSpeakerA.metaEditingLocBCountry = "None"

            if (thisSpeakerA.metaEditingLocationC == ""):
                thisSpeakerA.metaEditingLocationC = "None"
                thisSpeakerA.metaEditingLocCRegion = "None"
                thisSpeakerA.metaEditingLocCCountry = "None"

            database.session.add(thisSpeakerA)
            database.session.commit()

        ################################ Export metadata ################################

        output = ""
        for c in thisSample.__table__.columns:
            output += '{}: {}\n'.format(c.name, getattr(thisSample, c.name))
        output += "\n"

        with open(newfilenameM, "wb") as fM:
            fM.write(str.encode(output))

        outFromUpload = ""
        outFromUpload = outFromUpload + "Stevilo govorcev   = " + str(request.form.get('stGovorcev')) + '\n'
        outFromUpload = outFromUpload + "Vrsta posnetka     = " + str(request.form.get('formAF_source')) + '\n'
        outFromUpload = outFromUpload + "Kraj snemanja      = " + str(request.form.get('formAF_location')) + '\n'
        outFromUpload = outFromUpload + "Prostor govorcev   = " + str(request.form.get('formAF_room')) + '\n'
        outFromUpload = outFromUpload + "Datum snemanja     = " + str(request.form.get('formAF_date')) + '\n'
        outFromUpload = outFromUpload + "Kanal govora       = " + str(request.form.get('formAF_channel')) + '\n'
        outFromUpload = outFromUpload + "Vrsta govora       = " + str(request.form.get('formAF_speech')) + '\n'
        outFromUpload = outFromUpload + "Naprava snemanja   = " + str(request.form.get('formAF_tool')) + '\n'
        outFromUpload = outFromUpload + "Opis situacije     = " + str(request.form.get('formAF_description')) + '\n'
        outFromUpload = outFromUpload + "Kjučne besede      = " + str(request.form.get('formAF_keywords')) + '\n'
        outFromUpload = outFromUpload + '\n'
        outFromUpload = outFromUpload + "G1 ime in priimek  = " + str(request.form.get('formS1_name')) + '\n'
        outFromUpload = outFromUpload + "G1 spol            = " + str(request.form.get('formS1_genderSEL')) + '\n'
        outFromUpload = outFromUpload + "G1 spol (vpis)     = " + str(request.form.get('formS1_genderWRITE')) + '\n'
        outFromUpload = outFromUpload + "G1 starost         = " + str(request.form.get('formS1_age')) + '\n'
        outFromUpload = outFromUpload + "G1 izobrazba       = " + str(request.form.get('formS1_education')) + '\n'
        outFromUpload = outFromUpload + "G1 1. jezik SLO    = " + str(request.form.get('formS1_firstLangSlo')) + '\n'
        outFromUpload = outFromUpload + "G1 1. jezik        = " + str(request.form.get('formS1_firstLangSEL')) + '\n'
        outFromUpload = outFromUpload + "G1 1. jezik (vpis) = " + str(request.form.get('formS1_firstLangWRITE')) + '\n'
        outFromUpload = outFromUpload + "G1 dvojezicnost    = " + str(request.form.get('formS1_addLangTF')) + '\n'
        outFromUpload = outFromUpload + "G1 2. jezik        = " + str(request.form.get('formS1_addLangSEL')) + '\n'
        outFromUpload = outFromUpload + "G1 2. jezik (vpis) = " + str(request.form.get('formS1_addLangWRITE')) + '\n'
        outFromUpload = outFromUpload + "G1 kraj            = " + str(request.form.get('formS1_locationA')) + '\n'
        outFromUpload = outFromUpload + "G1 kraj otrostvo   = " + str(request.form.get('formS1_locationB')) + '\n'
        outFromUpload = outFromUpload + "G1 kraj drugo      = " + str(request.form.get('formS1_locationC')) + '\n'
        outFromUpload = outFromUpload + '\n'
        outFromUpload = outFromUpload + "G2 ime in priimek  = " + str(request.form.get('formS2_name')) + '\n'
        outFromUpload = outFromUpload + "G2 spol            = " + str(request.form.get('formS2_genderSEL')) + '\n'
        outFromUpload = outFromUpload + "G2 spol (vpis)     = " + str(request.form.get('formS2_genderWRITE')) + '\n'
        outFromUpload = outFromUpload + "G2 starost         = " + str(request.form.get('formS2_age')) + '\n'
        outFromUpload = outFromUpload + "G2 izobrazba       = " + str(request.form.get('formS2_education')) + '\n'
        outFromUpload = outFromUpload + "G2 1. jezik SLO    = " + str(request.form.get('formS2_firstLangSlo')) + '\n'
        outFromUpload = outFromUpload + "G2 1. jezik        = " + str(request.form.get('formS2_firstLangSEL')) + '\n'
        outFromUpload = outFromUpload + "G2 1. jezik (vpis) = " + str(request.form.get('formS2_firstLangWRITE')) + '\n'
        outFromUpload = outFromUpload + "G2 dvojezicnost    = " + str(request.form.get('formS2_addLangTF')) + '\n'
        outFromUpload = outFromUpload + "G2 2. jezik        = " + str(request.form.get('formS2_addLangSEL')) + '\n'
        outFromUpload = outFromUpload + "G2 2. jezik (vpis) = " + str(request.form.get('formS2_addLangWRITE')) + '\n'
        outFromUpload = outFromUpload + "G2 kraj            = " + str(request.form.get('formS2_locationA')) + '\n'
        outFromUpload = outFromUpload + "G2 kraj otrostvo   = " + str(request.form.get('formS2_locationB')) + '\n'
        outFromUpload = outFromUpload + "G2 kraj drugo      = " + str(request.form.get('formS2_locationC')) + '\n'
        outFromUpload = outFromUpload + '\n'
        outFromUpload = outFromUpload + "G3 ime in priimek  = " + str(request.form.get('formS3_name')) + '\n'
        outFromUpload = outFromUpload + "G3 spol            = " + str(request.form.get('formS3_genderSEL')) + '\n'
        outFromUpload = outFromUpload + "G3 spol (vpis)     = " + str(request.form.get('formS3_genderWRITE')) + '\n'
        outFromUpload = outFromUpload + "G3 starost         = " + str(request.form.get('formS3_age')) + '\n'
        outFromUpload = outFromUpload + "G3 izobrazba       = " + str(request.form.get('formS3_education')) + '\n'
        outFromUpload = outFromUpload + "G3 1. jezik SLO    = " + str(request.form.get('formS3_firstLangSlo')) + '\n'
        outFromUpload = outFromUpload + "G3 1. jezik        = " + str(request.form.get('formS3_firstLangSEL')) + '\n'
        outFromUpload = outFromUpload + "G3 1. jezik (vpis) = " + str(request.form.get('formS3_firstLangWRITE')) + '\n'
        outFromUpload = outFromUpload + "G3 dvojezicnost    = " + str(request.form.get('formS3_addLangTF')) + '\n'
        outFromUpload = outFromUpload + "G3 2. jezik        = " + str(request.form.get('formS3_addLangSEL')) + '\n'
        outFromUpload = outFromUpload + "G3 2. jezik (vpis) = " + str(request.form.get('formS3_addLangWRITE')) + '\n'
        outFromUpload = outFromUpload + "G3 kraj            = " + str(request.form.get('formS3_locationA')) + '\n'
        outFromUpload = outFromUpload + "G3 kraj otrostvo   = " + str(request.form.get('formS3_locationB')) + '\n'
        outFromUpload = outFromUpload + "G3 kraj drugo      = " + str(request.form.get('formS3_locationC')) + '\n'
        outFromUpload = outFromUpload + '\n'
        outFromUpload = outFromUpload + "FILE AUDIO         = " + newfilenameA + '\n'
        outFromUpload = outFromUpload + "FILE Speaker 1     = " + newfilename1 + '\n'
        outFromUpload = outFromUpload + "FILE Speaker 2     = " + newfilename2 + '\n'
        outFromUpload = outFromUpload + "FILE Speaker 3     = " + newfilename3 + '\n'
        outFromUpload = outFromUpload + '\n'
        
        with open(newfilenameU, "wb") as fD:
            fD.write(str.encode(outFromUpload))

        ################################ Finsh ################################

        notifyNewRecording(current_user.username,thisSampleID)
        return redirect(url_for('viewUser.success')+"?id="+str(thisSampleID)+"&len="+str(len))
        
    return render_template("home.html", user=current_user, username=current_user.username)
