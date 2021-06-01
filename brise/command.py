# -*- coding: UTF-8 -*-
import click
import brise
import os
import shutil
import zipfile
from brise.password_verify import password_en
from brise.mod import dump_mod, dumps_to_file


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.argument("project_name")
@click.pass_context
def new(ctx, project_name):
    tpl_path = os.path.join(brise.__path__[0], "bin/tpl")
    current_path = os.getcwd()
    if not os.path.exists(project_name):
        os.mkdir(project_name)
    apps_path = os.path.join(current_path, project_name, "apps")
    if not os.path.exists(apps_path):
        os.mkdir(apps_path)
    plugins_path = os.path.join(current_path, project_name, "plugins")
    if not os.path.exists(plugins_path):
        os.mkdir(plugins_path)
    for f in os.listdir(tpl_path):
        if not os.path.isdir(os.path.join(tpl_path, f)):
            shutil.copy(os.path.join(tpl_path, f), os.path.join(current_path, project_name, f[:-4]))


@cli.command()
@click.argument("module_name")
@click.pass_context
def add(ctx, module_name):
    tpl_path = os.path.join(brise.__path__[0], "bin/tpl", "module")
    current_path = os.getcwd()
    if not os.path.exists(module_name):
        os.mkdir(module_name)
    for f in os.listdir(tpl_path):
        copy2(os.path.join(tpl_path, f), os.path.join(current_path, module_name, f[:-4]), module_name)


@cli.command()
@click.argument("module_name")
@click.pass_context
def pack(ctx, module_name):
    module = dump_mod(module_name)
    if not os.path.exists("target"):
        os.mkdir("target")
    dumps_to_file(module, os.path.join("target", module_name + ".mod"))


@cli.command()
@click.argument("password")
@click.pass_context
def password_enc(ctx, password):
    print(password_en(password))


def copy2(src, dst, module_name):
    with open(src, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("module_name", module_name)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(content)


def zip_dir(module_name):
    if not os.path.exists("target"):
        os.mkdir("target")
    with zipfile.ZipFile(os.path.join("target", module_name + ".mod"), "w", zipfile.ZIP_DEFLATED) as f:
        for item in os.walk(module_name):
            for file in item[2]:
                f.write(os.path.join(item[0], file))
