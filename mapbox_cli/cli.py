import json
import os
from posixpath import path as upath

import boto3
import click
import requests


BASE_MAPBOX_URL = 'https://api.mapbox.com'
MAPBOX_REGION = 'us-east-1'


class UploadProgressBar:

  def __init__(self, filename, label="Upload progress"):
    self.filename = filename
    self.size = os.path.getsize(filename)
    self.progressbar = click.progressbar(length=self.size, label=label)

  def __call__(self, bytes_amount):
    self.bar.update(bytes_amount)

  def __enter__(self):
    self.bar.__enter__()

  def __exit__(self, *args):
    self.bar.__exit__(self, *args)


@click.group()
def cli():
  pass


@cli.command('upload')
@click.argument('upload')
@click.argument('tileset_name')
@click.option('--username', '-u', envvar='MAPBOX_USER', help="Mapbox username")
@click.option('--access-token', '-t', envvar='MAPBOX_ACCESS_TOKEN' help="Mapbox token")
def upload_command(upload, tileset_name, username, access_token):
  """
  Upload, stage, and create a tileset. UPLOAD is the path of the file to upload.
  """
  if not username:
    raise click.BadParameter("You must specify a username either with the --username option or as MAPBOX_USER")
  if not access_token:
    raise click.BadParameter("You must specify an access_token either with the --access-token option or as MAPBOX_ACCESS_TOKEN")

  # Get credentials from Mapbox
  url = ujoin(BASE_MAPBOX_URL, 'uploads', 'v1', username, 'credentials?' + access_token)
  response = requests.post(url)
  if not response.ok:
    raise Exception("There was an issue grabbing credentials: {}".format(json.dumps(response.json())))

  credentials = response.json()

  # Stage the dataset
  client = boto3.client(
    's3', MAPBOX_REGION,
    aws_access_key_id=credentials['accessKeyId'],
    aws_secret_access_key=credentials['secretAccessKey'],
    aws_session_token=credentials['sessionToken']
  )

  with UploadProgressBar(upload) as bar:
    client.upload_file(upload, credentials['bucket'], credentials['key'], Callback=bar)

  # Convert the dataset to a tileset
  url = upath.join(BASE_MAPBOX_URL, 'uploads', 'v1', username)
  response = requests.post(url, json={
    'tileset': '{}.{}'.format(username, tileset_name),
    'url': credentials['url'],
    'name': tileset_name
  })

  if not response.ok:
    raise Exception("Something went wrong converting to tileset: {}".format(json.dumps(response.json())))

  click.echo(json.dumps(response.json(), indent=2))
