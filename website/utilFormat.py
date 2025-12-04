from .dbModels import User, Sample, Transcript, Speaker
from .util import *
import subprocess
import os
import numpy as np
import wave

def formatDataBaseContentSpeaker(id):
    
    content = "<p style=\"font-weight: 600; text-align: center;\">Metapodatki</p>"

    content += "ID govorca: "                     + str(Speaker.query.get(id).id                     ) + "<br/>"
    content += "Text ID: "                        + str(Speaker.query.get(id).metaEditingTextID      ) + "<br/>"
    content += "Source ID: "                      + str(Speaker.query.get(id).metaEditingSourceID    ) + "<br/>"
    content += "Recording ID: "                   + str(Speaker.query.get(id).metaEditingRecordingID ) + "<br/>"
    content += "Subcorpus: "                      + str(Speaker.query.get(id).metaEditingSubcorpus   ) + "<br/>"
    content += "PRS-ID: "                         + str(Speaker.query.get(id).metaEditingPRSID       ) + "<br/>"
    content += "Spol: "                           + str(Speaker.query.get(id).metaEditingGender      ) + "<br/>"
    content += "Starost: "                        + str(Speaker.query.get(id).metaEditingAge         ) + "<br/>"
    content += "Prvi jezik: "                     + str(Speaker.query.get(id).metaEditingLanguageA   ) + "<br/>"
    content += "Dialekt: "                        + str(Speaker.query.get(id).metaEditingDialectType ) + "<br/>"
    content += "Narečna skupina: "                + str(Speaker.query.get(id).metaEditingDialectGRP  ) + "<br/>"
    content += "Narečje: "                        + str(Speaker.query.get(id).metaEditingDialect     ) + "<br/>"
    content += "Izbrazba: "                       + str(Speaker.query.get(id).metaEditingEducation   ) + "<br/>"
    content += "Kraj bivanja: "                   + str(Speaker.query.get(id).metaEditingLocationA   ) + "<br/>"
    content += "Regija bivanja: "                 + str(Speaker.query.get(id).metaEditingLocARegion  ) + "<br/>"
    content += "Država bivanja: "                 + str(Speaker.query.get(id).metaEditingLocACountry ) + "<br/>"
    content += "Kraj bivanja v otroštvu: "        + str(Speaker.query.get(id).metaEditingLocationB   ) + "<br/>"
    content += "Regija bivanja v otroštvu: "      + str(Speaker.query.get(id).metaEditingLocBRegion  ) + "<br/>"
    content += "Država bivanja v otroštvu: "      + str(Speaker.query.get(id).metaEditingLocBCountry ) + "<br/>"
    content += "Dodatni kraj bivanja: "           + str(Speaker.query.get(id).metaEditingLocationC   ) + "<br/>"
    content += "Regija dodatnega kraja bivanja: " + str(Speaker.query.get(id).metaEditingLocCRegion  ) + "<br/>"
    content += "Država dodatnega kraja bivanja: " + str(Speaker.query.get(id).metaEditingLocCCountry ) + "<br/>"
    content += "Dvojezičnost: "                   + str(Speaker.query.get(id).metaEditingBilingual   ) + "<br/>"
    content += "Dodatni prvi jezik: "             + str(Speaker.query.get(id).metaEditingLanguageB   ) + "<br/>"
    content += "Nazadnje urejal: "                + str(Speaker.query.get(id).metaEditingNameOfEditor) + "<br/>"
    content += "Datum zadnjega urejanja: "        + str(Speaker.query.get(id).metaEditingLastEditTime) + "<br/>"
    content += "<p style=\"font-weight: 600; text-align: center; padding-top: 20px;\">Originalni metapodatki</p>"
    content += "Ime in priimek: "          + str(Speaker.query.get(id).metaUploadName         ) + "<br/>"
    content += "Spol: "                    + str(Speaker.query.get(id).metaUploadGender       ) + "<br/>"
    content += "Starost: "                 + str(Speaker.query.get(id).metaUploadAge          ) + "<br/>"
    content += "Izobrazba: "               + str(Speaker.query.get(id).metaUploadEducation    ) + "<br/>"
    content += "Dvojezičnost: "            + str(Speaker.query.get(id).metaUploadBilingual    ) + "<br/>"
    content += "Prvi jezik: "              + str(Speaker.query.get(id).metaUploadLanguageA    ) + "<br/>"
    content += "Dodatni prvi jezik: "      + str(Speaker.query.get(id).metaUploadLanguageB    ) + "<br/>"
    content += "Kraj bivanja: "            + str(Speaker.query.get(id).metaUploadLocationA    ) + "<br/>"
    content += "Kraj bivanja v otroštvu: " + str(Speaker.query.get(id).metaUploadLocationB    ) + "<br/>"
    content += "Dodatni kraj(i) bivanja: " + str(Speaker.query.get(id).metaUploadLocationC    ) + "<br/>"
    content += "<p style=\"font-weight: 600; text-align: center; padding-top: 20px;\">Vir govorca</p>"
    content += "ID posnetka: "             + str(Speaker.query.get(id).recordingID            ) + "<br/>"
    content += "Zaporedni na posnetku: "   + str(Speaker.query.get(id).recordingOrder         ) + "<br/>"
    content += "Vezava govorca? "          + str(Speaker.query.get(id).bindingID              ) + "<br/>"

    return content

def formatDataBaseContentSample(id):
    userID = Sample.query.get(id).userID

    content = "<p style=\"font-weight: 600; text-align: center;\">Metapodatki</p>"
    content += "ID: " + str(Sample.query.get(id).id) + "<br/>"
    content += "Text ID: "       + str(Sample.query.get(id).metaEditingTextID) + "<br/>"
    content += "Source ID: "     + str(Sample.query.get(id).metaEditingSourceID) + "<br/>"
    content += "Recording ID: "  + str(Sample.query.get(id).metaEditingRecodingID) + "<br/>"
    content += "Subcorpus: "     + str(Sample.query.get(id).metaEditingSubcorpus) + "<br/>"
    content += "Description: "   + str(Sample.query.get(id).metaEditingDescription) + "<br/>"
    content += "Date: "          + str(Sample.query.get(id).metaEditingDate) + "<br/>"
    content += "Source: "        + str(Sample.query.get(id).metaEditingSource) + "<br/>"
    content += "Location: "      + str(Sample.query.get(id).metaEditingLocation) + "<br/>"
    content += "Speech domain: " + str(Sample.query.get(id).metaEditingSpeechDomain) + "<br/>"
    content += "Speech type: "   + str(Sample.query.get(id).metaEditingSpeechType) + "<br/>"
    content += "Channel: "       + str(Sample.query.get(id).metaEditingChannel) + "<br/>"
    content += "Keywords: "      + str(Sample.query.get(id).metaEditingKeywords) + "<br/>"
    content += "Device: "        + str(Sample.query.get(id).metaEditingDevice) + "<br/>"
    content += "Rooms: "         + str(Sample.query.get(id).metaEditingRooms) + "<br/>"
    content += "Quality: "       + str(Sample.query.get(id).metaEditingQuality) + "<br/>"
    content += "URl: "           + str(Sample.query.get(id).metaEditingURL) + "<br/>"
    content += "Preverjen: "                   + convTF(str(Sample.query.get(id).metaEditingChecked     )) + "<br/>"
    content += "Odobrena dolžina: "            + cMS(Sample.query.get(id).metaEditingLengthAprv  ) + "<br/>"
    content += "Odobrena kvaliteta: "          + convTF(str(Sample.query.get(id).metaEditingApprovedQ   )) + "<br/>"
    content += "Odobreno za transkribiranje: " + convTF(str(Sample.query.get(id).metaEditingApprovedForT)) + "<br/>"
    content += "Komentar za transkriptorja: "  + str(Sample.query.get(id).metaEditingCommentForT ) + "<br/>"
    content += "Transkribiranje začeto: "      + convTF(str(Sample.query.get(id).metaEditingStartedT    )) + "<br/>"
    content += "Odobrene transkripcije: "      + convTF(str(Sample.query.get(id).metaEditingApprovedTRS )) + "<br/>"
    content += "Komentar urejevalca: "         + str(Sample.query.get(id).metaEditingEditorComment) + "<br/>"
    content += "Nazadnje urejal: "             + str(Sample.query.get(id).metaEditingNameOfEditor) + "<br/>"
    content += "Datum zadnjega urejanja: "     + str(Sample.query.get(id).metaEditingLastEditTime) + "<br/>"
    content += "<p style=\"font-weight: 600; text-align: center; padding-top: 20px;\">Uporabnik in originalni metapodatki</p>"
    content += "Ime in priimek: " + str(User.query.get(userID).nameSurname) + "<br/>"
    content += "Uporabniško ime: " + str(User.query.get(userID).username) + "<br/>"
    content += "Elektronski naslov: " + convMail(User.query.get(userID).email) + "<br/>"
    content += "<br/>"
    content += "Število govorcev: " + str(Sample.query.get(id).metaUploadNoSpeakers) + "<br/>"
    content += "Vrsta snemanja: " + str(Sample.query.get(id).metaUploadSource) + "<br/>"
    content += "Kraj snemanja: " + str(Sample.query.get(id).metaUploadLocation) + "<br/>"
    content += "Prostori: " + str(Sample.query.get(id).metaUploadRooms) + "<br/>"
    content += "Datum: " + str(Sample.query.get(id).metaUploadDate) + "<br/>"
    content += "Kanal: " + str(Sample.query.get(id).metaUploadChannel) + "<br/>"
    content += "Vrsta govora: " + str(Sample.query.get(id).metaUploadSpeechType) + "<br/>"
    content += "Naprava: " + str(Sample.query.get(id).metaUploadTool) + "<br/>"
    content += "Opis situacije: " + str(Sample.query.get(id).metaUploadDescription) + "<br/>"
    content += "Ključne besede: " + str(Sample.query.get(id).metaUploadKeyWords) + "<br/>"
    content += "<p style=\"font-weight: 600; text-align: center; padding-top: 20px;\">Tehnične podrobnosti</p>"
    content += "Datum in čas nalaganja: " + str(Sample.query.get(id).uploadDate) + "<br/>"
    content += "Velikost audio datoteke: " + str(Sample.query.get(id).metaTechFileSizeBytes) + "<br/>"
    content += "Format audio datoteke: " + str(Sample.query.get(id).metaTechFileFormat) + "<br/>"
    content += "Dolžina posnetka (wav): " + cMS(Sample.query.get(id).metaTechLengthMilisec) + "<br/>"
    
    return content

def formatDataBaseContentUser(id):
    
    content = ""
    content += "ID: " + str(User.query.get(id).id) + "<br/>"
    content += "Ime in priimek: " + str(User.query.get(id).nameSurname) + "<br/>"
    content += "Uporabniško ime: " + str(User.query.get(id).username) + "<br/>"
    content += "Elektronski naslov: " + convMail(User.query.get(id).email) + "<br/>"
    content += "Aktiviran: " + convTF(str(User.query.get(id).isActive)) + "<br/>"
    content += "Administrator: " + convTF(str(User.query.get(id).isAdmin)) + "<br/>"
    content += "Urednik: " + convTF(str(User.query.get(id).isEditor)) + "<br/>"
    content += "Transkriptor: " + convTF(str(User.query.get(id).isTranscriber)) + "<br/>"
    content += "Skupna dolžina posnetkov: " + cMS(User.query.get(id).totalRecoringsLengtMilisec) + "<br/>"
    content += "Odobrena dolžina posnetkov: " + cMS(User.query.get(id).approvedRecoringsLengtMilisec) + "<br/>"
    content += "Izbrana nagrada: " + str(User.query.get(id).prizeSelect) + "<br/>"
    content += "Nagrada poslana: " + convTF(str(User.query.get(id).prizeSend)) + "<br/>"

    nameSurname = str(User.query.get(id).nameSurname)
    email = str(User.query.get(id).email)
    administrator = User.query.get(id).isAdmin
    transkriptor = User.query.get(id).isTranscriber
    izbrananagrada = str(User.query.get(id).prizeSelect)
    poslananagrada = User.query.get(id).prizeSend

    return content, nameSurname, email, administrator, transkriptor, izbrananagrada, poslananagrada

def formatWaveFileDataSimple(showID):

    try:
        soxContent = subprocess.run(['sox', '--i', "database/" + Sample.query.get(showID).metaTechFilenameWave], stdout=subprocess.PIPE)
        soxContent=soxContent.stdout.decode('utf-8').replace("\n","<br />")
        fileName = os.getcwd() + "/database/" + Sample.query.get(showID).metaTechFilenameWave

        fileData = wave.open(fileName, mode = 'rb')
        sample_width = fileData.getsampwidth() * 8
        sample_rate = fileData.getframerate()
        no_channels = fileData.getnchannels()

        datarate = round( sample_width * sample_rate * no_channels / 1000 )
        datarate = str(datarate) + "k"
        return sample_rate, sample_width, datarate
    except:
        return "","",""

def formatWaveFileData(showID):

    soxContent = subprocess.run(['sox', '--i', "database/" + Sample.query.get(showID).metaTechFilenameWave], stdout=subprocess.PIPE)
    soxContent=soxContent.stdout.decode('utf-8').replace("\n","<br />")

    if (soxContent == ""):
        return "Napaka"
    
    fileName = os.getcwd() + "/database/" + Sample.query.get(showID).metaTechFilenameWave
    fileData = wave.open(fileName, mode = 'rb')
    params = fileData.getparams()
    num_frames = fileData.getnframes()
    raw_data = fileData.readframes(num_frames)
    sample_width = fileData.getsampwidth()
    if sample_width == 1:
        dtype = np.uint8
        sample_width_pow = 7
    elif sample_width == 2:
        dtype = np.int16
        sample_width_pow = 15
    elif sample_width == 3:
        # dtype = np.int32
        # sample_width_pow = 23
        soxContent += "Določanje največje in najmanjše glasnosti pri" + "<br />"
        soxContent += "24-bitnih datotekah ni implementirano" + "<br />"
        return soxContent
    elif sample_width == 4:
        dtype = np.int32
        sample_width_pow = 31
    else:
        raise ValueError("Unsupported sample width")
    audio_data = np.frombuffer(raw_data, dtype=dtype)
    min_val = np.min(audio_data) / pow(2,sample_width_pow)
    max_val = np.max(audio_data) / pow(2,sample_width_pow)
    if sample_width == 1:
        min_val = min_val - 1.0
        max_val = max_val - 1.0
        
    soxContent += "Največja glasnost relativno v negativno smer: " + str(min_val) + "<br />"
    soxContent += "Največja glasnost relativno v pozitivno smer: " + str(max_val) + "<br />"

    return soxContent
