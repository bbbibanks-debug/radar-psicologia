import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import unicodedata
import re


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# =========================
# UTIL
# =========================

def normalizar(texto):

    texto = "".join(
        c for c in unicodedata.normalize(
            "NFD",
            texto
        )
        if unicodedata.category(c) != "Mn"
    )

    return texto.lower()


def limpar(texto):

    texto = re.sub(
        r"\\s+",
        " ",
        texto
    )

    return texto.strip()


# =========================
# PALAVRAS
# =========================

with open(
    "palavras.txt",
    encoding="utf-8"
) as f:

    palavras = [
        normalizar(x.strip())
        for x in f
        if x.strip()
    ]


# =========================
# SITES
# =========================

with open(
    "sites.txt",
    encoding="utf-8"
) as f:

    sites = [
        x.strip()
        for x in f
        if x.strip()
    ]


# =========================
# SCRAPING
# =========================

noticias = []
vistos = set()

lixo = [
    "login",
    "cadastre",
    "assine",
    "newsletter",
    "facebook",
    "instagram",
    "twitter",
    "youtube",
    "whatsapp"
]

for site in sites:

    print(f"Raspando {site}")

    try:

        response = requests.get(
            site,
            headers=HEADERS,
            timeout=15
        )

        soup = BeautifulSoup(
            response.text,
            "lxml"
        )

        candidatos = soup.find_all([
            "a",
            "h1",
            "h2",
            "h3"
        ])

        for item in candidatos:

            if item.name == "a":

                link_tag = item

            else:

                link_tag = item.find(
                    "a",
                    href=True
                )

            if not link_tag:
                continue

            titulo = limpar(
                link_tag.get_text()
            )

            if len(titulo) < 12:
                continue

            titulo_lower = titulo.lower()

            if any(
                x in titulo_lower
                for x in lixo
            ):
                continue

            titulo_norm = normalizar(
                titulo
            )

            termo = None

            for palavra in palavras:

                if palavra in titulo_norm:

                    termo = palavra
                    break

            if not termo:
                continue

            link = urljoin(
                site,
                link_tag["href"]
            )

            chave = f"{titulo}_{link}"

            if chave in vistos:
                continue

            vistos.add(chave)

            noticias.append({
                "titulo": titulo,
                "link": link,
                "termo": termo,
                "fonte": site
            })

    except Exception as e:

        print(f"Erro: {e}")


# =========================
# HTML
# =========================

data = datetime.now().strftime(
    "%d/%m/%Y %H:%M"
)

html = f"""
<!DOCTYPE html>

<html lang="pt-BR">

<head>

<meta charset="UTF-8">

<title>Radar Psicologia</title>

<style>

body {{
    background: #111827;
    color: white;
    font-family: Arial;
    padding: 40px;
}}

.card {{
    background: #1f2937;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 10px;
}}

.fonte {{
    color: #60a5fa;
    font-size: 12px;
    margin-bottom: 10px;
}}

.termo {{
    color: #34d399;
    font-size: 12px;
    margin-bottom: 10px;
}}

a {{
    color: white;
    text-decoration: none;
    font-size: 20px;
}}

a:hover {{
    text-decoration: underline;
}}

</style>

</head>

<body>

<h1>Radar Psicologia</h1>

<p>Atualizado em {data}</p>
"""

for noticia in noticias[:50]:

    html += f"""
    <div class="card">

        <div class="fonte">
            {noticia['fonte']}
        </div>

        <div class="termo">
            termo encontrado:
            {noticia['termo']}
        </div>

        <a href="{noticia['link']}">

            {noticia['titulo']}

        </a>

    </div>
    """

html += """
</body>
</html>
"""

with open(
    "index.html",
    "w",
    encoding="utf-8"
) as f:

    f.write(html)

print(f"Total: {len(noticias)}")

