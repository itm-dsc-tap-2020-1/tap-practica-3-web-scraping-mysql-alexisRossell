from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import mysql.connector as mysql
import time


def save_to_database(pagina, cursor):
    request = Request(pagina, headers={
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0"
        },)
    print(f"Revisando la pagina: {pagina}")
    try:
        html = urlopen(request, timeout=2)
        rawHtml = html.read()
    except Exception:
        return
    try:
        soup = BeautifulSoup(rawHtml, "html.parser")
    except Exception:
	    return
    enlaces = soup.select("a")
    for i in enlaces:
        try:
            url: str = i["href"]
        except KeyError:
            continue
        if not url.startswith("http"):
            continue
        try:
            operacion.execute(f'INSERT INTO tabla VALUES ("{url}", false)')
        except mysql.errors.IntegrityError:
            continue


conexion = mysql.connect(host="localhost", user="root", passwd="", db="p3")
operacion = conexion.cursor(buffered=True)

website = input("Pagina web: ")
save_to_database(website, operacion)

try:
    while True:
        operacion.execute("SELECT * FROM tabla WHERE estatus=FALSE")
        pagina = operacion.fetchone()
        if not pagina:
            break
        url = pagina[0]
        try:
            save_to_database(url, operacion)
        except Exception:
            operacion.execute(f'UPDATE tabla SET estatus=TRUE WHERE pagina="{url}"')
            continue
        operacion.execute(f'UPDATE tabla SET estatus=TRUE WHERE pagina="{url}"')
        operacion.execute("SELECT * FROM tabla")
        rows = operacion.fetchall()
        print(f"Paginas guardadas en la base: {len(rows)}")
        time.sleep(1)
        conexion.commit()

except Exception:
    pass

conexion.close()
