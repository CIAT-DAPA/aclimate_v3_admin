#!/usr/bin/env python3

import os
import sys
import click
from babel.messages import frontend as babel

@click.group()
def cli():
    """Gestión de traducciones para AClimate Admin"""
    pass

@cli.command()
def extract():
    """Extraer strings para traducir"""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    click.echo('Strings extraídos exitosamente.')

@cli.command()
@click.argument('lang')
def init(lang):
    """Inicializar un nuevo idioma"""
    if os.system('pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    click.echo(f'Idioma {lang} inicializado exitosamente.')

@cli.command()
def update():
    """Actualizar todas las traducciones existentes"""
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command failed')
    click.echo('Traducciones actualizadas exitosamente.')

@cli.command()
def compile():
    """Compilar todas las traducciones"""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')
    click.echo('Traducciones compiladas exitosamente.')

if __name__ == '__main__':
    cli()