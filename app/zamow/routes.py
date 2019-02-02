from app.zamow import main
# from app.klient.models import Miasta
from flask import render_template
from flask import request,flash

from sqlalchemy import extract
from app import db_session
# from app.klient.models import Miasta
# from app.klient.models import Klienci
# from app.klient.models import Towary
# from app.klient.models import Zamowienia
# from app.klient.models import Samochody
# from app.klient.models import Zamowienia_Towary
# from app.klient.models import Zamowienia_Samochody
from flask_jsonpify import jsonify
@main.route('/')
def display_all():
	# zamowienia=Zamowienia.query.all()
	return render_template('home.html')



@main.route('/dodaj',methods=['GET','POST'])
def display_dodaj():
	# zamowienia=Zamowienia.query.all()
	firmy=db_session.query(Klienci).all()
	kategorie=db_session.query(Towary.kategoria).distinct()
	zam_tow=db_session.query(Zamowienia.id_zam,Klienci.nazwa,Towary.nazwa,Zamowienia_Towary.ilosc_towaru).filter(Zamowienia.status=="N").outerjoin(Zamowienia_Towary,Zamowienia.id_zam==Zamowienia_Towary.id_zam).outerjoin(Klienci,Zamowienia.id_klienta==Klienci.id_klienta).outerjoin(Towary,Zamowienia_Towary.id_towaru==Towary.id_towaru)
	print("tu")
	return render_template('dodaj.html',firmy=firmy,kategorie=kategorie,zam_tow=zam_tow)

@main.route('/flota',methods=['GET','POST'])
def display_flota():
	odrzucone=db_session.query(Zamowienia.id_zam,Klienci.nazwa).filter(Zamowienia.status=="O").outerjoin(Klienci,Zamowienia.id_klienta==Klienci.id_klienta)
	nr_zamowienia=db_session.query(Zamowienia.id_zam).filter(Zamowienia.status=="O").outerjoin(Klienci,Zamowienia.id_klienta==Klienci.id_klienta)
	samochody=db_session.query(Samochody)
	braks=db_session.query(Zamowienia.id_zam,Samochody.pojemnosc).filter(Zamowienia.status=="O").join(Zamowienia_Samochody,Zamowienia_Samochody.id_zam==Zamowienia.id_zam).join(Samochody,Zamowienia_Samochody.id_samochodu==Samochody.id_samochodu).all()
	obecnie_jest=sum([x[1] for x in braks])		
	calk_wag=db_session.query(Zamowienia.id_zam,Zamowienia_Towary.ilosc_towaru,Towary.waga).filter(Zamowienia.status=="O").join(Zamowienia_Towary,Zamowienia.id_zam==Zamowienia_Towary.id_zam).join(Towary,Zamowienia_Towary.id_towaru==Towary.id_towaru).all()
	calk_waga=sum([x[1]*x[2] for x in calk_wag])
	obecnie_brakuje=calk_waga-obecnie_jest
	return render_template('flota.html',odrzucone=odrzucone,samochody=samochody,nr_zamowienia=nr_zamowienia,obecnie_brakuje=obecnie_brakuje)

@main.route('/firma',methods=['GET','POST'])
def display_firma():
	komunikat='Zamówienia złożone w dniu: '
	lista=[komunikat,"Przydzielone","Nieprzydzielone","Odrzucone"]
	return render_template('firma.html',lista=lista)