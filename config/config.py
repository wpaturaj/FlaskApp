import urllib
params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=LAPTOP-LRI3PN7A;DATABASE=PBL_project5;UID=wojte;PWD=vbn@1995;Trusted_Connection=yes;')
SQLALCHEMY_DATABASE_URI="mssql+pyodbc:///?odbc_connect=%s" % params