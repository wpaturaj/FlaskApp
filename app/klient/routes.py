from app.klient import dodanie
from app import db_session
from app.klient.models import Miasta
from app.klient.models import Klienci
from app.klient.models import Towary
from app.klient.models import Zamowienia
from app.klient.models import Zamowienia_Towary
from flask import render_template
from flask import request,flash,jsonify
from datetime import datetime
# from sqlalchemy import and_

@dodanie.route('/dodaj')
def display_all():
	db_session.commit()
	firmy=db_session.query(Klienci).all()
	kategorie=db_session.query(Towary.kategoria).distinct()
	return render_template('dodaj.html',firmy=firmy,kategorie=kategorie)


@dodanie.route('/kategoria/<state>')
def towar(state):
	print(state)
	firmy=db_session.query(Towary).filter(Towary.kategoria==state)
	print(firmy)
	firm_obj=[]
	for f in firmy:
		print(f.nazwa)
		f_obj={}
		f_obj['nazwa']=f.nazwa
		firm_obj.append(f_obj)
	print(firm_obj)
	return jsonify({'firmy':firm_obj})

# id_zam,id_klienta,data_zlozenia_zamowienia,status)
@dodanie.route('/produkt',methods=['GET','POST'])
def display_news():
	# try:
	if request.method == "POST":
		comp = request.form['comp_select']
		#Nazwa firmy
		id_kli=db_session.query(Klienci.id_klienta).filter(Klienci.nazwa==comp).all()
		print(id_kli[0][0])
		print('ok')
		start_dts = request.form['start_t']
		print(start_dts)
		#Sprawdzenie czy zamowienie z dzis dodane do tabeli Zamowienia
		check_zamowienia=db_session.query(Zamowienia.id_zam).filter(and_(Zamowienia.id_klienta==id_kli[0][0],
			Zamowienia.data_zlozenia_zamowienia==start_dts)).all()
		if len(check_zamowienia)==0:
			Zamowienia.create_zamowienie(id_klienta=id_kli[0][0],data_zlozenia_zamowienia=start_dts,status='N')
			#Jesli nie bylo zamowienia to teraz bierzemy id
			check_zamowienia=db_session.query(Zamowienia.id_zam).filter(and_(Zamowienia.id_klienta==id_kli[0][0],
			Zamowienia.data_zlozenia_zamowienia==start_dts)).all()
		print(len(check_zamowienia))
		print(check_zamowienia)
		#id towaru
		nazwa_tow=request.form['prod_sel']
		print(nazwa_tow)
		#Ilosc towaru
		ilosc_tow=request.form['produkt1']
		print(ilosc_tow)
		#querowanie id towaru	
		id_tow=db_session.query(Towary.id_towaru).filter(Towary.nazwa==nazwa_tow).all()
		#Dodanie zamowienia
		print(id_tow[0][0])
		#Sprawdzamy czy już było takie zamówienie w bazie danych # na ten sam produkt
		check_zamowienia_tow=db_session.query(Zamowienia_Towary.ilosc_towaru).filter(and_(Zamowienia_Towary.id_towaru==id_tow[0][0],
			Zamowienia_Towary.id_zam==check_zamowienia[0][0]))
		print(check_zamowienia_tow)
		if len(check_zamowienia_tow.all())==0:
			Zamowienia_Towary.create_zamowienie_towary(id_zam=check_zamowienia[0][0],
														id_towaru=id_tow[0][0],
														ilosc_towaru=ilosc_tow)
		else:
			print("ten krok")
			# check_zamowienia_tow.value=1000
			check_zamowienia_tow.update({'ilosc_towaru': float(check_zamowienia_tow.all()[0][0])+float(ilosc_tow)})
			db_session.commit()
		print("czy juz bylo zam")
		print(len(check_zamowienia))
		print(list(check_zamowienia_tow.all()))
		print("Value")
		print(print(len(check_zamowienia)))

	kategorie=db_session.query(Towary.kategoria).distinct()
	firmy=db_session.query(Klienci).all()
	zam_tow=db_session.query(Zamowienia.id_zam,Klienci.id_klienta,Towary.nazwa,Zamowienia_Towary.ilosc_towaru).filter(Zamowienia.status=="N").outerjoin(Zamowienia_Towary,Zamowienia.id_zam==Zamowienia_Towary.id_zam).outerjoin(Klienci,Zamowienia.id_klienta==Klienci.id_klienta).outerjoin(Towary,Zamowienia_Towary.id_towaru==Towary.id_towaru)
	print("tu")
	print(zam_tow.column_descriptions)
	return render_template('dodaj.html',firmy=firmy,kategorie=kategorie,zam_tow=zam_tow)
