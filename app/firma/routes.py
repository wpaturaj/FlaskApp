from app.firma import firma
from app import db_session
from app import ok
from app.klient.models import Miasta
from app.klient.models import Klienci
from app.klient.models import Towary
from app.klient.models import Zamowienia
from app.klient.models import Zamowienia_Towary
from app.klient.models import Zamowienia_Samochody
from app.klient.models import Samochody
import pandas as pd
import pyodbc
import pandas as pd
import datetime as dt
import numpy as np
import datetime
from flask import render_template
from flask import request,flash
from sqlalchemy import and_, extract

@firma.route('/organizuj',methods=['GET','POST'])
def display_organizuj():
	start_dts = request.form["start_firma_dt"]
	print(start_dts)
	start_dts=datetime.datetime.strptime(start_dts,'%Y-%m-%d')

	# Algorytm
	cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=LAPTOP-LRI3PN7A;" #nazwa serwera
                      "Database=PBL_project5;" #nazwa bazy danych
                      "Trusted_Connection=yes;")

	cursor = cnxn.cursor() #ustawienie sql-owego kursora

	czas_dojazdu = pd.read_sql_query("SELECT * FROM dbo.Czas_dojazdu ", cnxn)
	klient_z_miastem=pd.read_sql_query("SELECT a.id_klienta,a.id_miasta,a.nazwa,b.czas_dojazdu_do_magazynu,b.czas_na_dostarczenie FROM dbo.Klienci as a inner join dbo.Miasta as b on a.id_miasta=b.id_miasta ", cnxn)
	#Samochody status robimy != 5 !!!
	samochody = pd.read_sql_query("SELECT * FROM dbo.Samochody WHERE status <> '5' ", cnxn)
	samochody['data_powrotu'] =  pd.to_datetime(samochody['data_powrotu'], format='%d%b%Y:%H:%M:%S.%f')
	zamowienia_towary = pd.read_sql_query("    SELECT a.id_zam,b.id_klienta,e.id_miasta,b.status,Sum(a.ilosc_towaru*c.cena) AS Wartosc_calk, Sum(a.ilosc_towaru*c.waga) AS Waga_calk,\
	   b.data_zlozenia_zamowienia,e.czas_dojazdu_do_magazynu,e.czas_na_dostarczenie,\
	   DATEADD(day,czas_na_dostarczenie, data_zlozenia_zamowienia) as max_dost \
	   from Zamowienia_Towary as a join dbo.Zamowienia as b \
		on (a.id_zam=b.id_zam and b.status='N') \
		inner join dbo.Towary as c \
			on a.id_towaru=c.id_towaru \
		inner join dbo.Klienci as d \
			on b.id_klienta=d.id_klienta \
		inner join dbo.Miasta as e \
			on d.id_miasta=e.id_miasta \
		group by a.id_zam,b.id_klienta,b.status,b.data_zlozenia_zamowienia,e.id_miasta, DATEADD(day,czas_na_dostarczenie, data_zlozenia_zamowienia),e.czas_dojazdu_do_magazynu,e.czas_na_dostarczenie order by czas_na_dostarczenie ASC, Wartosc_calk DESC",cnxn)
	zamowienia_samochody=pd.read_sql_query("SELECT * FROM dbo.Zamowienia_Samochody", cnxn)

	miasta = pd.read_sql_query("SELECT * FROM dbo.Miasta ", cnxn)
	zamowienia = pd.read_sql_query("SELECT * FROM dbo.Zamowienia WHERE status <> 'P'", cnxn)

	#samochody z datę powrotu teraz mają zaktualizowaną datę powrotu na teraz
	samochody.loc[samochody['status'] == '0', 'data_powrotu'] = np.datetime64(start_dts)

	#tymczasowo na brak danych - DO USUNIECIA!!!!!
	#zamowienia_samochody['id_miasta_last'] = np.nan
	#zamowienia_samochody['id_miasta_last'] = 2

	zakonczono = 0
	df = zamowienia_towary
	teraz = start_dts

	zamowienia_nieprzydzielone =[]
	waga_nieprzydzielona =[]
	#pierwsze przypisanie, by wejść w algorytm
	check = 1


	#krok 1
	samochody.loc[samochody['data_powrotu'] <= teraz, 'status'] = '0'
	samochody.loc[samochody['data_powrotu'] <= teraz, 'wolne_miejsce'] = samochody['pojemnosc']

	#i = 2
	#zamowienie=df.loc[i,]
	while(check>0):
	    for i in range(df.shape[0]): #w tym ukryty jest punkt 12
	        zamowienie=df.loc[i,]
	        if(zamowienie.status == 'N'): #dodatkowy warunek, by potem nie przerabiać znowu tych bez 'N'
	            #krok 4
	            if df.status[i]!='P':
	                # Wolne miejsca w autach
	                wolne_msc=samochody.groupby(['status']).sum()['wolne_miejsce']
	                #idx statusuow dostepnych aut !!!!!NIE powinno być też 1?
	                #idx_dost=[val for val in wolne_msc.index if val in ['0','3','4']]
	                idx_dost = [val for val in wolne_msc.index if val in ['0', '3', '4', '1']]
	                dostepne_msc=sum(wolne_msc.loc[idx_dost,].values)
	                #krok 5
	                if zamowienie.Waga_calk <= dostepne_msc:
	                    while(zamowienie.Waga_calk>0):
	                        #Krok 6
	                        #zmienna pomocnicza
	                        nie_zdazy_zaden_1_i_4 = 1
	                        if ('1' in list(samochody.status) or '4' in list(samochody.status)):
	                            #Krok 7
	                            if zamowienia_samochody.shape[0]>0:
	                                
	                                czas_dojz_do_miasta=czas_dojazdu.loc[czas_dojazdu.id_miasta2==zamowienie.id_miasta,]
	                                #czas_dojz_do_miasta dojoinowac nizej po id_miasta_last=id_miasta2
	                                zamowienia_samochody.id_miasto_last=zamowienia_samochody.id_miasto_last.apply(int)
	                                temp_zamowien_samoch = pd.merge(zamowienia_samochody, czas_dojz_do_miasta, left_on = 'id_miasto_last', right_on = 'id_miasta1')
	                                # dodadajemy dane z miasta, by mieć dostęp do czasu dojazdu do magazynu
	                                temp_zamowien_samoch = pd.merge(temp_zamowien_samoch, miasta, left_on='id_miasto_last', right_on='id_miasta')
	                                #usuwamy czas na dostarczenie związany z zamówieniem ostatnego samochodu
	                                temp_zamowien_samoch.drop(columns=['czas_na_dostarczenie', 'nazwa', 'id_miasta1', 'id_miasta'], inplace=True)
	                                temp_zamowien_samoch['n_czas_dost'] = np.nan
	                                temp_zamowien_samoch.rename(index=str, columns={"czas_dojazdu_do_magazynu": "czas_dojazdu_do_magazynu_last", "id_miasta2": "id_miasta_rozpatrywane_zamow"}, inplace=True)

	                                #sortowanie po dacie dostarczenia związanej z ostatnim zamówieniem - w ten sposób weźmiemy samochody ze statusem związnym tylko z ostatnim realizowanym przez nie zamówieniem w następnym kroku (nth(0))
	                                #temp_zamowien_samoch = temp_zamowien_samoch.sort_values('data_dostarczenia', ascending=False)
	                                temp_zamowien_samoch['id_sam_do_grup']=temp_zamowien_samoch['id_samochodu']
	                                #nie wiem, czy działa jak powinno - TUTAJ BŁĄD ZWIĄZANY Z SYTUACJĄ GDY MAMY TE SAME DATY DOSTARCZENIA
	                                temp_zamowien_samoch = temp_zamowien_samoch.groupby('id_sam_do_grup').last()

	                                #łączymy z informacjami o statusie
	                                #pd.concat([temp_zamowien_samoch, samochody], axis=1)
	                                temp_zamowien_samoch.id_samochodu = temp_zamowien_samoch.id_samochodu.astype(int)
	                                temp_zamowien_samoch = pd.merge(temp_zamowien_samoch, samochody, left_on='id_samochodu', right_on='id_samochodu')

	                                #wydobywamy czas na dostarczenie związany z obecnym miastem
	                                temp_zamowien_samoch = pd.merge(temp_zamowien_samoch, miasta, left_on='id_miasta_rozpatrywane_zamow', right_on='id_miasta')
	                                temp_zamowien_samoch.drop(columns=['nazwa', 'id_miasta'], inplace=True)

	                                #dodanie kolumny określającej, czy bierzemy pod uwagę w dalszym wyborze
	                                temp_zamowien_samoch['czy_ok'] = np.nan

	                                #zmienna przechowująca ostateczną datę dostarczenia dla rozpatrywanego zamówienia
	                                data_maks_dost = np.datetime64(zamowienie.data_zlozenia_zamowienia + dt.timedelta(days=temp_zamowien_samoch.loc[0, 'czas_na_dostarczenie']))

	                                #rozdzielmy temp_zamowien_samoch na podgrupy związane ze statusem auta 1 i 4
	                                temp_zamowien_samoch_1 = temp_zamowien_samoch.loc[temp_zamowien_samoch['status'] == '1']
	                                temp_zamowien_samoch_4 = temp_zamowien_samoch.loc[temp_zamowien_samoch['status'] == '4']


	                                if temp_zamowien_samoch_1.shape[0] > 0:
	                                    #aktualizacja n_czas_dost
	                                    temp_zamowien_samoch_1.n_czas_dost = temp_zamowien_samoch_1.data_dostarczenia + temp_zamowien_samoch_1.czas.apply(lambda x: dt.timedelta(days=x))

	                                if temp_zamowien_samoch_4.shape[0] > 0:
	                                    # aktualizacja n_czas_dost
	                                    temp_zamowien_samoch_4.n_czas_dost = temp_zamowien_samoch_4.data_powrotu + temp_zamowien_samoch_4.czas_dojazdu_do_magazynu.apply(lambda x: dt.timedelta(days=x))

	                                #łączymy ponownie w 1 df
	                                temp_zamowien_samoch=pd.concat([temp_zamowien_samoch_1, temp_zamowien_samoch_4], ignore_index=True)

	                                temp_zamowien_samoch['czy_ok']=(temp_zamowien_samoch['n_czas_dost'] <= data_maks_dost)
	                                temp_zamowien_samoch = temp_zamowien_samoch.loc[temp_zamowien_samoch['czy_ok'] == True]

	                                if(temp_zamowien_samoch.shape[0]>0):
	                                    nie_zdazy_zaden_1_i_4 = 0
	                                    #temp_zamowien_samoch = temp_zamowien_samoch.iloc[temp_zamowien_samoch['n_czas_dost'].argmax()]
	                                    max_row = np.argmin(temp_zamowien_samoch['n_czas_dost'].values)

	                                    #Krok 8
	                                    #WYBRANY SAMOCHÓD :)
	                                    temp_zamowien_samoch = temp_zamowien_samoch.reset_index(drop=True)
	                                    samochod_wybrany = temp_zamowien_samoch.loc[max_row,]

	                                    #aktualizacja zamowienia_samochody
	                                    rows1 = [[zamowienie.id_zam,  samochod_wybrany.n_czas_dost,  samochod_wybrany.id_samochodu, int(zamowienie.id_miasta)]]
	                                    tempDf1 = pd.DataFrame(rows1, columns=list(zamowienia_samochody.columns))
	                                    zamowienia_samochody = zamowienia_samochody.append(tempDf1, ignore_index=True)

	                                    #Krok 9
	                                    #przydzielenie ładunku i sprawdzenie, czy się zmieścił
	                                    czy_zmiesicil = (samochod_wybrany.wolne_miejsce >= zamowienie.Waga_calk)
	                                    if czy_zmiesicil:
	                                        #Krok 11
	                                        samochod_wybrany.wolne_miejsce = samochod_wybrany.wolne_miejsce - zamowienie.Waga_calk
	                                        if (samochod_wybrany.wolne_miejsce == 0):
	                                            samochod_wybrany.status = '2' # ??? jeżeli samochód został zapełniony w 100% trzeba już mu zmienić status, by nie został ponownie rozpatrywany
	                                        zamowienie.Waga_calk = 0
	                                        df.loc[df['id_zam'] == zamowienie.id_zam, 'Waga_calk'] = 0
	                                        zamowienia.loc[zamowienia['id_zam'] == zamowienie.id_zam, 'status'] = 'P'
	                                        df.loc[df['id_zam'] == zamowienie.id_zam, 'status'] = 'P'

	                                    else:
	                                        #Krok 10
	                                        zamowienie.Waga_calk = zamowienie.Waga_calk - samochod_wybrany.wolne_miejsce
	                                        df.loc[zamowienia['id_zam'] == zamowienie.id_zam, 'Waga_calk'] = zamowienie.Waga_calk
	                                        samochod_wybrany.wolne_miejsce = 0
	                                        samochod_wybrany.status = '2'
	                                        #tutaj chyba wraca do 6

	                                    #aktualizacja powrotu - musi być tutaj - wcześniej, niż zakładał schemat
	                                    samochody.loc[samochody['id_samochodu'] == samochod_wybrany.id_samochodu, 'data_powrotu'] = samochod_wybrany.n_czas_dost + dt.timedelta(days=samochod_wybrany.czas_dojazdu_do_magazynu)
	                                    #aktualizacja wolnego miejsca
	                                    samochody.loc[samochody['id_samochodu'] == samochod_wybrany.id_samochodu, 'wolne_miejsce'] = samochod_wybrany.wolne_miejsce
	                                    #aktualizacja statusów, bo niektóre mogły się zmienić na '2'
	                                    samochody.loc[samochody['id_samochodu'] == samochod_wybrany.id_samochodu, 'status'] = samochod_wybrany.status
	                                else:
	                                    nie_zdazy_zaden_1_i_4 = 1

	                        #Krok 20
	                        if(('0' in list(samochody.status) or '3' in list(samochody.status)) & (nie_zdazy_zaden_1_i_4 == 1)):  #(nie ma o statusie 1 i 4)
	                            #Krok 21
	                            samoch_3 = samochody[samochody.status == '3']
	                            samoch_0 = samochody[samochody.status == '0']

	                            if '3' in list(samochody.status):
	                                #Krok 26
	                                samoch_3['czy_ok'] = ((samoch_3.data_powrotu + dt.timedelta(days=zamowienie.czas_dojazdu_do_magazynu)) <= zamowienie.max_dost)
	                                samoch_3 = samoch_3.loc[samoch_3['czy_ok'] == True]
	                                samoch_3.drop(columns=['czy_ok'], inplace=True)

	                            samoch_wst = pd.concat([samoch_0, samoch_3], ignore_index=True)

	                            if ('0' in list(samoch_wst.status) or '3' in list(samoch_wst.status)):
	                                #Krok 22-25 # rozdysponujemy po 'calych' autach zamowienia
	                                #samoch_sorted=samochody[samochody.status=='0'].sort_values('pojemnosc',ascending=False)
	                                #j=0
	                                while(zamowienie.Waga_calk>0):
	                                    #while(zamowienie.Waga_calk>max(samoch_sorted.pojemnosc))
	                                    #Krok 23
	                         #          #update miejsca
	                                    samoch_sorted = samoch_wst[(samoch_wst.status == '0') | (samoch_wst.status == '3')].sort_values('pojemnosc',ascending=False)
	                                    nr_samoch=samoch_sorted[(samoch_wst.status == '0') | (samoch_wst.status == '3')].iloc[0,]['id_samochodu']
	                                    status=samoch_sorted[(samoch_wst.status == '0') | (samoch_wst.status == '3')].iloc[0,]['status']
	                                    samochody.loc[samochody.id_samochodu==nr_samoch,'wolne_miejsce'] = max([float(samochody[samochody.id_samochodu==nr_samoch]['pojemnosc']-zamowienie.Waga_calk),0])
	                                    #pomocnicza
	                                    pojemnosc = samochody.loc[samochody.id_samochodu==nr_samoch,'pojemnosc']
	                                    pojemnosc = pojemnosc.values
	                                    pojemnosc = pojemnosc[0]
	                                    #status 1 ma jeszcze msc badz 0 nie ma msc
	                                    if int(samochody.loc[samochody.id_samochodu==nr_samoch,'wolne_miejsce'])>0: #zamowienie sie zmiesciło
	                                        if (status == '0'):
	                                            samochody.loc[samochody.id_samochodu==nr_samoch,'status'] = '1'
	                                            samoch_wst.loc[samoch_wst.id_samochodu==nr_samoch,'status'] = '1'
	                                        else:
	                                            samochody.loc[samochody.id_samochodu == nr_samoch, 'status'] = '4'
	                                            samoch_wst.loc[samoch_wst.id_samochodu == nr_samoch, 'status'] = '4'
	                                        df.loc[df['id_zam'] == zamowienie.id_zam, 'Waga_calk'] = 0
	                                        zamowienie.Waga_calk = np.float64(0)

	                                    else: #zamowienie nie zmiesilo się, ale przypisujemy calosc
	                                        samochody.loc[samochody.id_samochodu==nr_samoch,'status'] = '2'
	                                        samoch_wst.loc[samoch_wst.id_samochodu == nr_samoch, 'status'] = '2'
	                                        df.loc[df['id_zam'] == zamowienie.id_zam, 'Waga_calk'] = df.loc[df['id_zam'] == zamowienie.id_zam, 'Waga_calk'] - pojemnosc
	                                        zamowienie.Waga_calk = np.float64(df.loc[df['id_zam'] == zamowienie.id_zam, 'Waga_calk'])

	                                    rows = [[zamowienie.id_zam,teraz+dt.timedelta(days=zamowienie.czas_dojazdu_do_magazynu),nr_samoch, zamowienie.id_miasta]]
	                                    tempDf = pd.DataFrame(rows,columns=list(zamowienia_samochody.columns))
	                                    #aktuaizacja zamowienia_samochody
	                                    zamowienia_samochody=zamowienia_samochody.append(tempDf)
	                                    #zamowienie.Waga_calk = max([0,float(zamowienie.Waga_calk-samochody[samochody.id_samochodu == nr_samoch]['pojemnosc'])])
	                                    # + moja sugestia - aktualizować czas powrotu
	                                    x = tempDf.data_dostarczenia + dt.timedelta(days=zamowienie.czas_dojazdu_do_magazynu)
	                                    x = x.values
	                                    x = x[0]
	                                    samochody.loc[samochody.id_samochodu == nr_samoch, 'data_powrotu'] = x
	                         #               #j+=1
	                                df.loc[i,'status']='P'
	                                zamowienia.loc[zamowienia.id_zam == zamowienie.id_zam, 'status'] = 'P'

	    #Krok 13 - bez aktualizacji daty powrotu, z wyrzuceniem statusu 5
	    samochody.loc[samochody.status != '0', 'status'] = '2'
	    check = 0
	    #Krok 14
	    samochody.to_string()
	    if not ('N' in list(zamowienia.status)):
	        #koniec
	        pass

	    else:
	        #Krok 15
	        #df_1 = df.loc[df['status'] == 'N']
	        for i in range(df.shape[0]):
	            zamowienie = df.loc[i,]
	            if(zamowienie.status == 'N'):
	                #ile ze statusem 3 spełni
	                samochody.loc[((samochody.data_powrotu + dt.timedelta(days=zamowienie.czas_dojazdu_do_magazynu)) <= zamowienie.max_dost) & (samochody.status != '0') & (samochody.pojemnosc >= zamowienie.Waga_calk), 'status'] = 'x'
	                ile_spelnia = samochody.loc[samochody.status == 'x', 'status'].count()
	                samochody.loc[samochody.status == 'x', 'status'] = '3'
	                #samochody ze statusem 3 muszą mieć na nowo pojemność == wolne_miejsce ???
	                samochody.loc[samochody.status == '3', 'wolne_miejsce'] = samochody.pojemnosc
	                #ile ze statusem 0 spełni
	                samochody.loc[((samochody.data_powrotu + dt.timedelta(days=zamowienie.czas_dojazdu_do_magazynu)) <= zamowienie.max_dost) & (samochody.status == '0') & (samochody.pojemnosc >= zamowienie.Waga_calk), 'status'] = 'x'
	                ile_spelnia += samochody.loc[samochody.status == 'x', 'status'].count()
	                samochody.loc[samochody.status == 'x', 'status'] = '0'

	                if (ile_spelnia != 0):
	                    print('check został zwiększony')
	                    check+=1

	                else:
	                    zamowienie.status = 'O'
	                    df.loc[df['id_zam'] == zamowienie.id_zam, 'status'] = 'O'
	                    zamowienia.loc[zamowienia['id_zam'] == zamowienie.id_zam, 'status'] = 'O'
	                    zamowienia_nieprzydzielone.append(zamowienie.id_zam)
	                    waga_nieprzydzielona.append(zamowienie.Waga_calk)
	        #if check !=0:
	            #powrót do początku algorytmu (punkt 3)
	         #   pass
	        #else:
	         #   print("Koniec algorytmu")
	          #  ilosc_nieprzydzielonych = df.loc[df.status == 'O', 'status'].count()
	           # pass

	print("Koniec algorytmu")

	samochody.loc[samochody.status != '0', 'status'] = '2'
	print('Nie ma nieobsłużonych zamówień')
	print(samochody.to_string())
	print(zamowienia.to_string())
	print(df.to_string())
	print(zamowienia_samochody.to_string())
	if (len(zamowienia_nieprzydzielone) == 0 & len(waga_nieprzydzielona) == 0):
	    print('Nie ma nieobsłużonych zamówień')
	else:
	    print('Uwaga - nie obsłużono ', len(zamowienia_nieprzydzielone), ' zamówień!')
	    print('Nieobsłużone zamówienia: ',zamowienia_nieprzydzielone)
	    print('Nieprzydzielone do tych zamowień wagi towarów: ',waga_nieprzydzielona)

	#print(start_dts)
	print("try update samochody")
	for index,row in samochody.iterrows():
	    cursor.execute("Update dbo.Samochody set status=?, wolne_miejsce=?, data_powrotu=? where id_samochodu=?", 
	                    row['status'],row['wolne_miejsce'],row['data_powrotu'],row['id_samochodu']) 
	cnxn.commit()
	print("try update zamowienia")
	for index,row in zamowienia.iterrows():
	    cursor.execute("Update dbo.Zamowienia set status=? where id_zam=? and id_klienta=?", 
	                   row['status'],row['id_zam'], row['id_klienta']) 
	cnxn.commit()
	cursor.execute("DELETE FROM dbo.Zamowienia_Samochody")
	print("try update zamowienia_samochody")
	for index,row in zamowienia_samochody.iterrows():
	    cursor.execute("INSERT INTO dbo.Zamowienia_Samochody([id_zam],[data_dostarczenia],[id_samochodu],[id_miasto_last]) values (?,?,?,?)", 
	                   row['id_zam'], row['data_dostarczenia'],row['id_samochodu'],row['id_miasto_last']) 
	cnxn.commit()

	komunikat='Zamówienia złożone w dniu: '+str(start_dts)
	lista=[komunikat,"Przydzielone","Nieprzydzielone","Odrzucone"]
	przydzielone=db_session.query(Zamowienia.id_zam,Zamowienia_Samochody.data_dostarczenia,Zamowienia_Samochody.id_samochodu,Klienci.nazwa).filter(Zamowienia.status=="P").filter(extract('year', Zamowienia.data_zlozenia_zamowienia) == start_dts.year).filter(extract('month', Zamowienia.data_zlozenia_zamowienia) == start_dts.month).filter(extract('day', Zamowienia.data_zlozenia_zamowienia) == start_dts.day).join(Zamowienia_Samochody,Zamowienia.id_zam==Zamowienia_Samochody.id_zam).outerjoin(Klienci,Zamowienia.id_klienta==Klienci.id_klienta)
	nieprzydzielone=db_session.query(Zamowienia.id_zam,Klienci.nazwa).filter(Zamowienia.status=="N").filter(extract('year', Zamowienia.data_zlozenia_zamowienia) == start_dts.year).filter(extract('month', Zamowienia.data_zlozenia_zamowienia) == start_dts.month).filter(extract('day', Zamowienia.data_zlozenia_zamowienia) == start_dts.day).outerjoin(Klienci,Zamowienia.id_klienta==Klienci.id_klienta)
	odrzucone=db_session.query(Zamowienia.id_zam,Klienci.nazwa).filter(Zamowienia.status=="O").filter(extract('year', Zamowienia.data_zlozenia_zamowienia) == start_dts.year).filter(extract('month', Zamowienia.data_zlozenia_zamowienia) == start_dts.month).filter(extract('day', Zamowienia.data_zlozenia_zamowienia) == start_dts.day).outerjoin(Klienci,Zamowienia.id_klienta==Klienci.id_klienta)

	return render_template('firma.html',lista=lista,przydzielone=przydzielone,nieprzydzielone=nieprzydzielone,odrzucone=odrzucone)
