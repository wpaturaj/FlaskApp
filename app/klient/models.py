# from app import db
from app import db_session
from app import Base
from datetime import datetime
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String,Numeric,DateTime

class Miasta(Base):
	__tablename__ = 'Miasta'
	__table_args__ = (PrimaryKeyConstraint('id_miasta'),{})
	id_miasta = Column(Integer,nullable=False)
	nazwa=Column(String,nullable=False)
	czas_dojazdu_do_magazynu = Column(Numeric(18,2),nullable=False)
	czas_na_dostawe = Column(Numeric(18,2),nullable=False)
	

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
	__table_args__ = (PrimaryKeyConstraint('id_klienta'),{})
	id_klienta=Column(Integer,nullable=False)
	id_miasta = Column(Integer,nullable=False)
	nazwa=Column(String(50),nullable=False)
	mail=Column(String(50),nullable=False)
	nr_telefonu=Column(String(50),nullable=False)

	def __init__(self, id_klienta, id_miasta, nazwa, mail, nr_telefonu):
		self.id_klienta = id_klienta
		self.id_miasta = id_miasta
		self.nazwa = nazwa
		self.mail = mail
		self.nr_telefonu = nr_telefonu

class Towary(Base):
	__tablename__ = 'Towary'
	__table_args__ = (PrimaryKeyConstraint('id_towaru'),{})
	id_towaru = Column(Integer,nullable=False)
	nazwa=Column(String,nullable=False)
	waga=Column(Numeric(18,2),nullable=False)
	cena=Column(Numeric(18,2),nullable=False)
	kategoria=Column(String,nullable=False)

	def __init__(self,  id_towaru, nazwa, waga, cena):
		self.id_towaru = id_towaru
		self.nazwa = nazwa
		self.waga = waga
		self.cena = cena
		self.kategoria=kategoria


class Zamowienia(Base):
	__tablename__ = 'Zamowienia'
	__table_args__ = (PrimaryKeyConstraint('id_zam'),{})
	id_zam = Column(Integer,nullable=False,primary_key=True,autoincrement=True)
	id_klienta = Column(Integer,nullable=False, autoincrement=False)
	data_zlozenia_zamowienia=Column(DateTime, nullable=False)
	status=nazwa=Column(String,default="N")

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
	# __table_args__ = (PrimaryKeyConstraint('id_zam','id_towaru'),{})
	id_zam = Column(Integer,nullable=False,primary_key=True,autoincrement=False)
	id_towaru = Column(Integer,nullable=False,autoincrement=False)
	ilosc_towaru=Column(Integer,nullable=False)


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
	# __table_args__ = (PrimaryKeyConstraint('id_zam','id_towaru'),{})
	id_samochodu = Column(Integer,nullable=False,primary_key=True,autoincrement=True)
	pojemnosc = Column(Integer,nullable=False)
	status=Column(String,nullable=False)
	wolne_miejsce=Column(Integer,nullable=False)
	data_powrotu=Column(DateTime, nullable=False)


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
	__table_args__ = (PrimaryKeyConstraint('id_zam'),{})
	id_zam = Column(Integer,nullable=False,primary_key=True,autoincrement=False)
	data_dostarczenia = Column(DateTime,nullable=False)
	id_samochodu=Column(Integer, nullable=False)
	id_miasto_last=Column(Integer)

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