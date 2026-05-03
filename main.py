from database import guardar_en_supabase, guardar_productos, inicializar_db
from scraper import scrapear_todas_las_categorias


def main():
    inicializar_db()
    print("Base de datos inicializada correctamente.")
    productos = scrapear_todas_las_categorias()
    guardar_productos(productos)
    guardar_en_supabase(productos)


if __name__ == "__main__":
    main()
