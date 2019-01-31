from app.flota import flota
from app import db_session
from app.klient.models import Samochody
from app.klient.models import Klienci
from app.klient.models import Towary
from app.klient.models import Zamowienia
from app.klient.models import Zamowienia_Towary
from app.klient.models import Zamowienia_Samochody
from flask import render_template
from flask import request,flash
# from sqlalchemy import func
import datetime as dt
# from sqlalchemy.orm.attributes import flag_modified
# import pyodbc

@flota.route('/dodajAuto',methods=['GET','POST'])
def display_news():
	if request.method == "POST":
		id_sam=db_session.query(func.max(Samochody.id_samochodu)).scalar()+1
		pojemn=request.form['auto_lad']
		status='5'
		wolne_m=pojemn
		data_powr=None
		print(id_sam,pojemn,status,wolne_m,data_powr)
		# Samochody.create_samochody(id_sam,pojemn,status,wolne_m,data_powr)
		nr_zam=request.form["zam_select"]
		czas_dojaz=request.form["days_nb"]
		print(len(nr_zam))
		print("nazwa")
		print(nr_zam)
		print(pojemn)
		if( nr_zam!="-"):
			nr_zam=int(nr_zam)
			potrzebne_msc=db_session.query(Zamowienia_Towary.ilosc_towaru,Towary.waga).filter(Zamowienia_Towary.id_zam==nr_zam).join(Towary,Zamowienia_Towary.id_towaru==Towary.id_towaru).all()
			calk_waga=sum([x[0]*x[1] for x in potrzebne_msc])
			print("waga")
			print(calk_waga)
			obecnie_zam=db_session.query(Zamowienia.id_zam,Samochody.pojemnosc).filter(Zamowienia.status=="O").filter(Zamowienia.id_zam==nr_zam).join(Zamowienia_Samochody,Zamowienia_Samochody.id_zam==Zamowienia.id_zam).join(Samochody,Zamowienia_Samochody.id_samochodu==Samochody.id_samochodu).all()
			calk_pojemn=sum([x[1] for x in obecnie_zam])
			if float(calk_pojemn)+float(pojemn)>float(calk_waga):
				db_session.query(Zamowienia).filter(Zamowienia.id_zam==nr_zam).update({Zamowienia.status: 'P'}, synchronize_session=False)
				db_session.commit()
				print("!!!!TU!!")
			else:
				pass
			# Samochody.create_samochody(id_sam,pojemn,status,max(0,float(pojemn)-calk_waga+calk_pojemn),data_powr)
			data_wyj=db_session.query(Zamowienia.data_zlozenia_zamowienia).filter(Zamowienia.id_zam==nr_zam).all()
			print(data_wyj[0][0])
			Samochody.create_samochody(id_sam,pojemn,status,max(0,float(pojemn)-float(calk_waga)+float(calk_pojemn)),data_powr)
			# create_zam_samochody(cls,id_zam,data_wyj[0]+ dt.timedelta(days=int(czas_dojaz)),id_samochodu,id_miasto_last)
			Zamowienia_Samochody.create_zam_samochody(nr_zam,data_wyj[0][0]+ dt.timedelta(days=int(czas_dojaz)),id_sam,0)
		odrzucone=db_session.query(Zamowienia.id_zam,Klienci.nazwa).filter(Zamowienia.status=="O").outerjoin(Klienci,Zamowienia.id_klienta==Klienci.id_klienta)
		nr_zamowienia=db_session.query(Zamowienia.id_zam).filter(Zamowienia.status=="O").outerjoin(Klienci,Zamowienia.id_klienta==Klienci.id_klienta)
		print("tu")
		print(list(odrzucone.all()))
		samochody=db_session.query(Samochody)
		braks=db_session.query(Zamowienia.id_zam,Samochody.pojemnosc).filter(Zamowienia.status=="O").join(Zamowienia_Samochody,Zamowienia_Samochody.id_zam==Zamowienia.id_zam).join(Samochody,Zamowienia_Samochody.id_samochodu==Samochody.id_samochodu).all()
		obecnie_jest=sum([x[1] for x in braks])		
		calk_wag=db_session.query(Zamowienia.id_zam,Zamowienia_Towary.ilosc_towaru,Towary.waga).filter(Zamowienia.status=="O").join(Zamowienia_Towary,Zamowienia.id_zam==Zamowienia_Towary.id_zam).join(Towary,Zamowienia_Towary.id_towaru==Towary.id_towaru).all()
		calk_waga=sum([x[1]*x[2] for x in calk_wag])
		obecnie_brakuje=calk_waga-obecnie_jest
		return render_template('flota.html',odrzucone=odrzucone,samochody=samochody,nr_zamowienia=nr_zamowienia,obecnie_brakuje=obecnie_brakuje)