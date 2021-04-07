from paramiko import SSHClient
import argparse
import getpass
import os,subprocess
from pathlib import Path

class Password:
  DEFAULT = 'Prompt if not specify'
  def __init__(self, value):
    if value == self.DEFAULT:
      value = getpass.getpass('ssh Password: ')
    self.value = value
  def __str__(self):
    return self.value

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', type=str, help='ssh username', required=True)
parser.add_argument('-p', '--password', type=Password, help='ssh password', default=Password.DEFAULT)
parser.add_argument('-s', '--servers', type=argparse.FileType('r'), help='./hosts or server list by line', required=True)
args = parser.parse_args()

print('host file: {}\n'.format(args.servers.name))

def getPubKey():
  home = str(Path.home())
  username = getpass.getuser()
  pubKey = ''
  print(f'Home directory: {home}')
  print(f'System UserID: {username}')
  for root, dirs, files in os.walk(home + "/.ssh/", topdown=False):
    if files:
      for filename in files:
        if 'id_rsa.pub' in filename:
          with open(os.path.join(root,filename),'r') as pKey:
            print(f'Key Location: {root}{filename}\n')
            pubKey= pKey.read().strip()
    else:
      print("default id_rsa.pub not found, generating")
      subprocess.call('ssh-keygen -q -t rsa -N "" -f ~/.ssh/id_rsa',shell=True)
      time.sleep(1)
      print('\nNew key pairs created')
      getPubKey()
  print(f'{username}\'s public Key:\n{pubKey}\n')
  return pubKey

def fastSshCopyId():
  for instance in args.servers.readlines():
    instance = instance.strip()
    print(f'-------Host: {instance}-------')
  
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(instance, username=args.username, password=str(args.password))
    
    MyPubKey = getPubKey() 
    stdin, stdout, stderr = client.exec_command('echo "{}" >> ~/.ssh/authorized_keys'.format(MyPubKey))
    
    # list all keys
    #stdin, stdout, stderr = client.exec_command('cat  ~/.ssh/authorized_keys')
    # Print output of command. Will wait for command to finish.
    print(f'STDOUT:\n {stdout.read().decode("utf8")}')
    print(f'STDERR:\n {stderr.read().decode("utf8")}')
    # Get return code from command (0 is default for success)
    print(f'Return code: {stdout.channel.recv_exit_status()}\n')
    # Because they are file objects, they need to be closed
    stdin.close()
    stdout.close()
    stderr.close()
    
    client.close()

fastSshCopyId()
