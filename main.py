from database import guardar_productos, inicializar_db
from scraper import scrapear_superseis


def main():
    inicializar_db()
    print("Base de datos inicializada correctamente.")
    productos = scrapear_superseis()
    guardar_productos(productos)


if __name__ == "__main__":
    main()
