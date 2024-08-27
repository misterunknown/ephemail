# EpheMail

This is a very simplistic temporary mail solution.

## Quickstart

Create a python3 virtual environment and install the requirements:

```bash
$ python3 -m venv myenv
$ source myenv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt

# Start the main script
$ python3 main.py
```

Don't forget to change the `config.json` according to your setup.

Configure postfix to pipe received mails to the `tcp_email_sender.py` script.
You have to replace `<HOSTNAME>` and `<PORT>` with the corresponding values from
the configuration. WARNING: This proposed configuration is only for absolutely
minimal proof-of-concept purposes, which can be used on a freshly installed
postfix to get started.

```postfix
# /etc/postfix/master.cf:
ephemail   unix  -       n       n       -       -       pipe
  flags=R  user=nobody  argv=/path/to/tcp_email_send.py  <HOSTNAME> <PORT>
```
```postfix
# /etc/postfix/main.cf:

ephemail_destination_transport_limit = 1
mydomain = foobar
alias_maps = 
default_transport = ephemail
```

Now, restart postfix and navigate to the web application. You should see the
generated email address. Try to send a mail to this address:

```
echo "test mail" | mail -s "test mail" "youremail@localhost.localdomain"
```

This email should now appear on the web interface.
