from app import db
from app import db_session
from app import Base
# from app import Base

from datetime import datetime

class Miasta(Base):
	__tablename__ = 'Miasta'
	__table_args__ = (db.PrimaryKeyConstraint('id_miasta'),{})
	id_miasta = db.Column(db.Integer,nullable=False)
	nazwa=db.Column(db.String,nullable=False)
	czas_dojazdu_do_magazynu = db.Column(db.Numeric(18,2),nullable=False)
	czas_na_dostawe = db.Column(db.Numeric(18,2),nullable=False)
	

	def __init__(self,  id_miasta, nazwa, czas_dojazdu_do_magazynu, czas_na_dostawe):
		self.id_miasta = id_miasta
		self.nazwa = nazwa
		self.czas_dojazdu_do_magazynu = czas_dojazdu_do_magazynu
		self.czas_na_dostawe = czas_na_dostawe

	@classmethod
	def create_zamowienie(cls,firma,produkt1,produkt2):
		zamow=cls(firma=firma,
					produkt1=produkt1,
					produkt2=produkt2)
		db_session.add(zamow)
		db_session.commit()
		return zamow

class Klienci(Base):
	__tablename__ = 'Klienci'
	__table_args__ = (db.PrimaryKeyConstraint('id_klienta'),{})
	id_klienta=db.Column(db.Integer,nullable=False)
	id_miasta = db.Column(db.Integer,nullable=False)
	nazwa=db.Column(db.String(50),nullable=False)
	mail=db.Column(db.String(50),nullable=False)
	nr_telefonu=db.Column(db.String(50),nullable=False)

	def __init__(self, id_klienta, id_miasta, nazwa, mail, nr_telefonu):
		self.id_klienta = id_klienta
		self.id_miasta = id_miasta
		self.nazwa = nazwa
		self.mail = mail
		self.nr_telefonu = nr_telefonu

class Towary(Base):
	__tablename__ = 'Towary'
	__table_args__ = (db.PrimaryKeyConstraint('id_towaru'),{})
	id_towaru = db.Column(db.Integer,nullable=False)
	nazwa=db.Column(db.String,nullable=False)
	waga=db.Column(db.Numeric(18,2),nullable=False)
	cena=db.Column(db.Numeric(18,2),nullable=False)
	kategoria=db.Column(db.String,nullable=False)

	def __init__(self,  id_towaru, nazwa, waga, cena):
		self.id_towaru = id_towaru
		self.nazwa = nazwa
		self.waga = waga
		self.cena = cena
		self.kategoria=kategoria


class Zamowienia(Base):
	__tablename__ = 'Zamowienia'
	__table_args__ = (db.PrimaryKeyConstraint('id_zam'),{})
	id_zam = db.Column(db.Integer,nullable=False,primary_key=True,autoincrement=True)
	id_klienta = db.Column(db.Integer,nullable=False, autoincrement=False)
	data_zlozenia_zamowienia=db.Column(db.DateTime, nullable=False)
	status=nazwa=db.Column(db.String,default="N")

	def __init__(self,  id_klienta, data_zlozenia_zamowienia, status):
		self.id_klienta = id_klienta
		self.data_zlozenia_zamowienia = data_zlozenia_zamowienia
		self.status = status

	@classmethod
	def create_zamowienie(cls,id_klienta,data_zlozenia_zamowienia,status):
		zamow=cls(
					id_klienta=id_klienta,
					data_zlozenia_zamowienia=data_zlozenia_zamowienia,
					status=status)
		db_session.add(zamow)
		db_session.commit()
		return zamow

class Zamowienia_Towary(Base):
	__tablename__ = 'Zamowienia_Towary'
	# __table_args__ = (db.PrimaryKeyConstraint('id_zam','id_towaru'),{})
	id_zam = db.Column(db.Integer,nullable=False,primary_key=True,autoincrement=False)
	id_towaru = db.Column(db.Integer,nullable=False,autoincrement=False)
	ilosc_towaru=db.Column(db.Integer,nullable=False)


	def __init__(self,  id_zam, id_towaru, ilosc_towaru):
		self.id_zam = id_zam
		self.id_towaru = id_towaru
		self.ilosc_towaru = ilosc_towaru

	@classmethod
	def create_zamowienie_towary(cls,id_zam,id_towaru,ilosc_towaru):
		zamow=cls(
					id_zam=id_zam,
					id_towaru=id_towaru,
					ilosc_towaru=ilosc_towaru)
		db_session.add(zamow)
		db_session.commit()
		return zamow

class Samochody(Base):
	__tablename__ = 'Samochody'
	# __table_args__ = (db.PrimaryKeyConstraint('id_zam','id_towaru'),{})
	id_samochodu = db.Column(db.Integer,nullable=False,primary_key=True,autoincrement=True)
	pojemnosc = db.Column(db.Integer,nullable=False)
	status=db.Column(db.String,nullable=False)
	wolne_miejsce=db.Column(db.Integer,nullable=False)
	data_powrotu=db.Column(db.DateTime, nullable=False)


	def __init__(self,  id_samochodu, pojemnosc, status,wolne_miejsce,data_powrotu):
		self.id_samochodu = id_samochodu
		self.pojemnosc = pojemnosc
		self.status = status
		self.wolne_miejsce = wolne_miejsce
		self.data_powrotu = data_powrotu

	@classmethod
	def create_samochody(cls,id_samochodu,pojemnosc,status,wolne_miejsce,data_powrotu):
		zamow=cls(
					id_samochodu=id_samochodu,
					pojemnosc=pojemnosc,
					status=status,
					wolne_miejsce=wolne_miejsce,
					data_powrotu=data_powrotu)
		db_session.add(zamow)
		db_session.commit()
		return zamow

class Zamowienia_Samochody(Base):
	__tablename__ = 'Zamowienia_Samochody'
	__table_args__ = (db.PrimaryKeyConstraint('id_zam'),{})
	id_zam = db.Column(db.Integer,nullable=False,primary_key=True,autoincrement=False)
	data_dostarczenia = db.Column(db.DateTime,nullable=False)
	id_samochodu=db.Column(db.Integer, nullable=False)
	id_miasto_last=db.Column(db.Integer)

	@classmethod
	def create_zam_samochody(cls,id_zam,data_dostarczenia,id_samochodu,id_miasto_last):
		zamow=cls(
					id_zam=id_zam,
					data_dostarczenia=data_dostarczenia,
					id_samochodu=id_samochodu,
					id_miasto_last=id_miasto_last)
		db_session.add(zamow)
		db_session.commit()
		return zamow
	# def __init__(self,  id_klienta, data_zlozenia_zamowienia, status):
	# 	self.id_klienta = id_klienta
	# 	self.data_zlozenia_zamowienia = data_zlozenia_zamowienia
	# 	self.status = status
	# def __repr__(self):
	# 	return "<CapacityMin('%s','%s','%s','%s','%s','%s')>" % (self.id_klienta, self.id_miasta ,
	# 	        self.nazwa ,self.mail,
	# 	        self.nr_telefonu)
# 	
# class Users(Base):
#     __table__ = Base.metadata.tables['zamowieniaa']