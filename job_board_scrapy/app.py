from peewee import *
from datetime import *
from flask import jsonify, Flask

app = Flask(__name__)
db = SqliteDatabase("poslovi.db")


class BaseModel(Model):
    class Meta:
        database = db


class Mojposao(BaseModel):
    datum_prikupljanja = DateField()
    link_za_posao = TextField()
    mjesto = TextField()
    pozicija = TextField()
    tvrtka = TextField()
    vrijedi_do = TextField()
    zupanija = TextField()

    class Meta:
        table_name = "mojposao"


class Posaohr(BaseModel):
    datum_prikupljanja = DateField()
    link_za_posao = TextField()
    mjesto = TextField()
    pozicija = TextField()
    tvrtka = TextField()
    vrijedi_do = TextField()
    zupanija = TextField()

    class Meta:
        table_name = "posaohr"


db.connect()


@app.route("/svi_poslovi", methods=["GET"])
def svi_poslovi():
    svi_poslovi = list()
    for job in Posaohr.select():
        svi_poslovi.append(
            dict(
                zupanija=job.zupanija,
                mjesto=job.mjesto,
                tvrtka=job.tvrtka,
                pozicija=job.pozicija,
                link_za_posao=job.link_za_posao,
                vrijedi_do=job.vrijedi_do,
                datum_prikupljanja=job.datum_prikupljanja,
            )
        )
    for job in Mojposao.select():
        svi_poslovi.append(
            dict(
                zupanija=job.zupanija,
                mjesto=job.mjesto,
                tvrtka=job.tvrtka,
                pozicija=job.pozicija,
                link_za_posao=job.link_za_posao,
                vrijedi_do=job.vrijedi_do,
                datum_prikupljanja=job.datum_prikupljanja,
            )
        )
    return jsonify(svi_poslovi)


@app.route("/svi_poslovi_moj_posao", methods=["GET"])
def svi_poslovi_moj_posao():
    svi_poslovi = list()
    for job in Mojposao.select():
        svi_poslovi.append(
            dict(
                zupanija=job.zupanija,
                mjesto=job.mjesto,
                tvrtka=job.tvrtka,
                pozicija=job.pozicija,
                link_za_posao=job.link_za_posao,
                vrijedi_do=job.vrijedi_do,
                datum_prikupljanja=job.datum_prikupljanja,
            )
        )
    return jsonify(svi_poslovi)


@app.route("/svi_poslovi_posaohr", methods=["GET"])
def svi_poslovi_posaohr():
    svi_poslovi = list()
    for job in Posaohr.select():
        svi_poslovi.append(
            dict(
                zupanija=job.zupanija,
                mjesto=job.mjesto,
                tvrtka=job.tvrtka,
                pozicija=job.pozicija,
                link_za_posao=job.link_za_posao,
                vrijedi_do=job.vrijedi_do,
                datum_prikupljanja=job.datum_prikupljanja,
            )
        )
    return jsonify(svi_poslovi)


@app.route("/svi_poslovi_posaohr/<datum>", methods=["GET"])
def datum_svi_poslovi_posaohr(datum):
    datum = datetime.strptime(datum, "%Y-%m-%d").date()
    svi_poslovi = list()
    for job in Posaohr.select():
        if datum == job.datum_prikupljanja:
            svi_poslovi.append(
                dict(
                    zupanija=job.zupanija,
                    mjesto=job.mjesto,
                    tvrtka=job.tvrtka,
                    pozicija=job.pozicija,
                    link_za_posao=job.link_za_posao,
                    vrijedi_do=job.vrijedi_do,
                    datum_prikupljanja=job.datum_prikupljanja,
                )
            )
    if svi_poslovi == []:
        return jsonify({"Poruka": "Na ovaj datum nema prikupljenih poslova."}), 404
    return jsonify(svi_poslovi)


@app.route("/svi_poslovi_moj_posao/<datum>", methods=["GET"])
def datum_svi_poslovi_mojposao(datum):
    datum = datetime.strptime(datum, "%Y-%m-%d").date()
    svi_poslovi = list()
    for job in Mojposao.select():
        if datum == job.datum_prikupljanja:
            svi_poslovi.append(
                dict(
                    zupanija=job.zupanija,
                    mjesto=job.mjesto,
                    tvrtka=job.tvrtka,
                    pozicija=job.pozicija,
                    link_za_posao=job.link_za_posao,
                    vrijedi_do=job.vrijedi_do,
                    datum_prikupljanja=job.datum_prikupljanja,
                )
            )
    if svi_poslovi == []:
        return jsonify({"Poruka": "Na ovaj datum nema prikupljenih poslova."}), 404
    return jsonify(svi_poslovi)


@app.route("/svi_poslovi_od_tvrtke/<datum>/<string:tvrtka>", methods=["GET"])
def svi_poslovi_od_tvrtke(datum, tvrtka):
    datum = datetime.strptime(datum, "%Y-%m-%d").date()
    svi_poslovi = list()
    for job in Posaohr.select().where(Posaohr.tvrtka == tvrtka):
        if datum == job.datum_prikupljanja:
            svi_poslovi.append(
                dict(
                    zupanija=job.zupanija,
                    mjesto=job.mjesto,
                    tvrtka=job.tvrtka,
                    pozicija=job.pozicija,
                    link_za_posao=job.link_za_posao,
                    vrijedi_do=job.vrijedi_do,
                    datum_prikupljanja=job.datum_prikupljanja,
                )
            )
    for job in Mojposao.select().where(Mojposao.tvrtka == tvrtka):
        if datum == job.datum_prikupljanja:
            svi_poslovi.append(
                dict(
                    zupanija=job.zupanija,
                    mjesto=job.mjesto,
                    tvrtka=job.tvrtka,
                    pozicija=job.pozicija,
                    link_za_posao=job.link_za_posao,
                    vrijedi_do=job.vrijedi_do,
                    datum_prikupljanja=job.datum_prikupljanja,
                )
            )
    if svi_poslovi == []:
        return (
            jsonify(
                {
                    "Poruka": "Na ovaj datum nema objavljenih poslova od zatrazene tvrtke."
                }
            ),
            404,
        )
    return jsonify(svi_poslovi)


@app.route("/svi_poslovi_na_mjestu/<datum>/<string:mjesto>", methods=["GET"])
def svi_poslovi_u_mjestu(datum, mjesto):
    datum = datetime.strptime(datum, "%Y-%m-%d").date()
    svi_poslovi = list()
    for job in Posaohr.select().where(Posaohr.mjesto == mjesto):
        if datum == job.datum_prikupljanja:
            svi_poslovi.append(
                dict(
                    zupanija=job.zupanija,
                    mjesto=job.mjesto,
                    tvrtka=job.tvrtka,
                    pozicija=job.pozicija,
                    link_za_posao=job.link_za_posao,
                    vrijedi_do=job.vrijedi_do,
                    datum_prikupljanja=job.datum_prikupljanja,
                )
            )
    for job in Mojposao.select().where(Mojposao.mjesto == mjesto):
        if datum == job.datum_prikupljanja:
            svi_poslovi.append(
                dict(
                    zupanija=job.zupanija,
                    mjesto=job.mjesto,
                    tvrtka=job.tvrtka,
                    pozicija=job.pozicija,
                    link_za_posao=job.link_za_posao,
                    vrijedi_do=job.vrijedi_do,
                    datum_prikupljanja=job.datum_prikupljanja,
                )
            )
    if svi_poslovi == []:
        return (
            jsonify(
                {
                    "Poruka": "Na ovaj datum nema objavljenih poslova unutar zatrazenog mjesta."
                }
            ),
            404,
        )
    return jsonify(svi_poslovi)


app.run(port=5000)
db.close()
