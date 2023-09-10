#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Самостоятельно изучите работу с пакетом python-psycopg2 для работы с базами данных
PostgreSQL. Для своего варианта лабораторной работы 2.17 необходимо реализовать
возможность хранения данных в базе данных СУБД PostgreSQL.
"""

import psycopg2
import typing as t
from pathlib import Path
import argparse


def connect():
    conn = psycopg2.connect(user="postgres",
                            password="1234",
                            host="127.0.0.1",
                            port="5432")
    return conn


def create_db() -> None:
    # Курсор для выполнения операций с базой данных
    cursor = connect().cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS shop_name (
        shop_id serial,
        PRIMARY KEY(shop_id),
        name TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS shops (
        shop_id serial,
        PRIMARY KEY(shop_id),
        product TEXT NOT NULL,
        price INTEGER NOT NULL,
        FOREIGN KEY(shop_id) REFERENCES shop_name(shop_id)
        ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )


def add_shop(
        name: str,
        product: str,
        price: int
    ) -> None:
    cursor = connect().cursor()
    cursor.execute(
        """
        SELECT shop_id FROM shop_name WHERE name = %s
        """,
        (name,)
    )
    row = cursor.fetchone()
    if row is None:

        cursor.execute(
            """
            INSERT INTO shop_name (name) VALUES (%s)
            """,
            (name,)
        )
        shop_id = cursor.lastrowid
    else:
        shop_id = row[0]
    cursor.execute(
        """
        INSERT INTO shops (shop_id, price, product)
        VALUES (%s, %s, %s)
        """,
        (shop_id, price, product)
    )
    connect().commit()


def display(shops: t.List[t.Dict[str, t.Any]]) -> None:
    if shops:
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 8,
            '-' * 20
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^8} |'.format(
                "No",
                "Название.",
                "Товар",
                "Цена"
            )
        )
        print(line)
        for idx, shop in enumerate(shops, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:>8} |'.format(

                    idx,
                    shop.get('name', ''),
                    shop.get('product', ''),
                    shop.get('price', 0)

                )
            )
            print(line)


def select_all():
    cursor = connect().cursor()
    cursor.execute(
        """
        SELECT shop_name.name, shops.product, shops.price
        FROM shops
        INNER JOIN shop_name ON shop_name.shop_id = shops.shop_id
        """
    )
    rows = cursor.fetchall()
    connect().close()
    return [
        {
            "name": row[0],
            "product": row[1],
            "price": row[2],

        }
        for row in rows
    ]


def select_shop(name) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать магазин
    """
    cursor = connect().cursor()
    cursor.execute(
        """
        SELECT shop_name.name, shops.product, shops.price
        FROM shops
        INNER JOIN shop_name ON shop_name.shop_id = shops.shop_id
        WHERE shop_name.name = %s
        """,
        (name,)
    )
    rows = cursor.fetchall()
    connect().close()
    return [
        {
            "name": row[0],
            "product": row[1],
            "price": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    """
    главная функция программы
    """
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "shops.db"),
        help="The data file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("shops")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления магазина.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new product"
    )
    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="The shop's name"
    )
    add.add_argument(
        "-p",
        "--product",
        action="store",
        help="The shop's product"
    )
    add.add_argument(
        "-pr",
        "--price",
        action="store",
        type=int,
        required=True,
        help="The price of product"
    )
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all product"
    )
    # Создать субпарсер для выбора работников.
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the shops"
    )
    select.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="The shop's name"
    )
    args = parser.parse_args(command_line)
    create_db()
    if args.command == "add":
        add_shop(args.name, args.product, args.price)
    elif args.command == "select":
        display(select_shop(args.name))
    elif args.command == "display":
        display(select_all())
    pass


if __name__ == '__main__':
    main()
