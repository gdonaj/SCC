from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import database
from .dbModels import User

app = Flask(__name__)
viewAccount = Blueprint('viewAccount', __name__)

@viewAccount.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        nameSurname = request.form.get('name')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        agree = request.form.get('termsofservice')

        userN = User.query.filter_by(username=username).first()
        userE = User.query.filter_by(email=email).first()
        
        if len(username) < 1:
            flash('Napaka: izbrati morate uporabniško ime', category='error')
        elif len(nameSurname) < 1:
            flash('Napaka: vpisate morate svoje ime in priimek', category='error')
        elif len(email) < 1:
            flash('Napaka: vpisate morate svojo elektronsko pošto', category='error')
        elif(agree == None):
            flash('Napaka: za prijavo se morate strinjati s pogoji uporabe', category='error')
        elif userN:
            flash('Napaka: uporabnik s tem uporabniškim imenom že obstaja', category='error')
        elif userE:
            flash('Napaka: uporabnik s tem elektronskim naslovom že obstaja', category='error')
        elif password1 != password2:
            flash('Napaka: Vpisani gesli se ne ujemata', category='error')
        elif len(password1) < 8:
            flash('Napaka: Geslo mora biti dolgo vsaj 8 zankov.', category='error')
        else:

            new_user = User(email=email,
                            username=username, 
                            nameSurname=nameSurname,
                            isActive=True,
                            isAdmin=False,
                            isEditor=False,
                            isTranscriber=False,
                            totalRecoringsLengtMilisec=0,
                            approvedRecoringsLengtMilisec=0, 
                            prizeSelect="",
                            prizeSend=False,
                            password=generate_password_hash(password1, method='pbkdf2:sha256:1000000', salt_length=16)
                            )
            
            database.session.add(new_user)
            database.session.commit()

            app.logger.info("Uporabnik registriran:")
            app.logger.info(" - Uporabniško ime = " + str(new_user.username))
            app.logger.info(" - Ime in priimek = " + str(new_user.nameSurname))
            app.logger.info(" - Email = " + str(new_user.email))
            app.logger.info(" - Geslo = " + str(new_user.password))
            
            if (new_user.id == 1):
                new_user.isAdmin=True
                new_user.isEditor=True
                new_user.isTranscriber=True
            database.session.commit()

            login_user(new_user, remember=True)
            flash('Vaš uporabniški račun je bil uspešno ustvarjen', category='success')
            return redirect(url_for('viewUser.home'))
        
    if (current_user.is_authenticated):
        flash('Trenutno ste že prijavljeni z uporabniškim imenom: ' + current_user.username)
        return redirect(url_for('viewUser.home'))

    return render_template('sign_up.html', user=current_user)


@viewAccount.route('/login', methods=['GET', 'POST'])
def login():

    next = request.args.get('next')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Uspešno ste se prijavili!', category='success')
                login_user(user, remember=False)
                app.logger.info('Uporabnik uspešno prijavljen: '+username)
                if (next == None):
                    return redirect(url_for('viewUser.home'))
                else:
                    return redirect(next)
            else:
                app.logger.warning('Neuspešna prijava (ime) za uporabniško ime: '+username)
                flash('Napačno uporabniško ime ali geslo', category='error')
        else:
            app.logger.warning('Neuspešna prijava (geslo) za uporabniško ime: '+username)
            flash('Napačno uporabniško ime ali geslo', category='error')
 
    if (current_user.is_authenticated):
        flash('Trenutno ste že prijavljeni z uporabniškim imenom: ' + current_user.username)        
        if (next == None):
            return redirect(url_for('viewUser.home'))
        else:
            return redirect(next)

    return render_template('/login.html', user=current_user)


@viewAccount.route('/logout')
@login_required
def logout():
    app.logger.info('Uporabnik odjavljen: '+current_user.username)
    logout_user()
    return redirect(url_for('viewAccount.login'))


@viewAccount.route('/terms')
def terms():
    return render_template("terms.html", user=current_user)


@viewAccount.route('/privacy')
def privacy():
    return render_template("privacy.html", user=current_user)

@viewAccount.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        app.logger.info('Spremembe podatkov računa za uporabnika: '+current_user.username)
        if ("changeData" in request.form): 
            
            newNameSurname  = str(request.form.get('newNameSurname')).strip()
            newEmail  = str(request.form.get('newEmail')).strip()

            if (newNameSurname == ""):
                flash('Napaka: polje "ime in priimek" ne sme ostati prazno', category='error')
            elif (newEmail == ""):
                flash('Napaka: polje "elektronska pošta" ne sme ostati prazno', category='error')
            else:
                try:
                    user = User.query.filter_by(id=current_user.id).first()
                    user.nameSurname = newNameSurname
                    user.email = newEmail
                    database.session.commit()
                    flash('Spremembe podatkov so bile shranjene', category='success')
                except:
                    flash('Neznana napaka pri shranjevanju podatkov', category='error')

        elif ("changePass" in request.form):
            oldPass = str(request.form.get('oldPass'))
            newPass1 = str(request.form.get('newPass1'))
            newPass2 = str(request.form.get('newPass2'))

            if not (check_password_hash(current_user.password, oldPass)):
                flash('Napaka: vpisali ste napačno obstoječe geslo', category='error')
            elif (newPass1 != newPass2):
                flash('Napaka: gesli se ne ujemata', category='error')
            elif len(newPass1) < 8:
                flash('Napaka: novo geslo mora biti dolgo vsaj 8 zankov.', category='error')
            else:
                try:
                    password = generate_password_hash(newPass1, method='pbkdf2:sha256:1234987', salt_length=16)
                    user = User.query.filter_by(id=current_user.id).first()
                    user.password = password
                    database.session.commit()
                    flash('Spremembe gesla so bile shranjene', category='success')
                except:
                    flash('Neznana napaka pri shranjevanju podatkov', category='error')

        return render_template("account.html", 
                user=current_user,
                newNameSurname = current_user.nameSurname,
                newEmail = current_user.email
                )
    
    return render_template("account.html", 
            user=current_user,
            newNameSurname = current_user.nameSurname,
            newEmail = current_user.email
            )
