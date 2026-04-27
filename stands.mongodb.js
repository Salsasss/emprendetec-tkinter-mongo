db.usuarios.insertOne(
    {
        "nombre": "Aarón",
        "correo": "aaronsalasn@gmail.com",
        "contrasena": "",
        "rol": "admin",
        "fecha_creacion": ISODate("2026-04-26"),
        "esta_activo": "true"
    }
)

db.stands.insertMany(
    [
        {
            "_id": "Stand-01",
            "agenda": [],
            "ubicacion": {
                "zona": "Sombreadero",
                "pasillo": "A",
                "numero_mesa": 1
            }
        },
        {
            "_id": "Stand-02",
            "agenda": [],
            "ubicacion": {
                "zona": "Sombreadero",
                "pasillo": "A",
                "numero_mesa": 2
            }
        },
        {
            "_id": "Stand-03",
            "agenda": [],
            "ubicacion": {
                "zona": "Sombreadero",
                "pasillo": "A",
                "numero_mesa": 3
            }
        },
        {
            "_id": "Stand-04",
            "agenda": [],
            "ubicacion": {
                "zona": "Sombreadero",
                "pasillo": "A",
                "numero_mesa": 4
            }
        },
        {
            "_id": "Stand-05",
            "agenda": [],
            "ubicacion": {
                "zona": "Sombreadero",
                "pasillo": "B",
                "numero_mesa": 5
            }
        },
        {
            "_id": "Stand-06",
            "agenda": [],
            "ubicacion": {
                "zona": "Sombreadero",
                "pasillo": "B",
                "numero_mesa": 6
            }
        },
        {
            "_id": "Stand-07",
            "agenda": [],
            "ubicacion": {
                "zona": "Sombreadero",
                "pasillo": "B",
                "numero_mesa": 7
            }
        },
        {
            "_id": "Stand-08",
            "agenda": [],
            "ubicacion": {
                "zona": "Sombreadero",
                "pasillo": "B",
                "numero_mesa": 8
            }
        },
        {
            "_id": "Stand-09",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 9
            }
        },
        {
            "_id": "Stand-10",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 10
            }
        },
        {
            "_id": "Stand-11",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 11
            }
        },
        {
            "_id": "Stand-12",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 12
            }
        },
        {
            "_id": "Stand-13",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 13
            }
        },
        {
            "_id": "Stand-14",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 14
            }
        },
        {
            "_id": "Stand-15",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 15
            }
        },
        {
            "_id": "Stand-16",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 16
            }
        },
        {
            "_id": "Stand-17",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 17
            }
        },
        {
            "_id": "Stand-18",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 18
            }
        },
        {
            "_id": "Stand-19",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 19
            }
        },
        {
            "_id": "Stand-20",
            "agenda": [],
            "ubicacion": {
                "zona": "Frente al E",
                "pasillo": "C",
                "numero_mesa": 20
            }
        }
    ])