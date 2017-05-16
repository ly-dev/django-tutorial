@echo get cert/key from https://zerossl.com/free-ssl/#self
@echo enable localhost invalid certificate with url chrome://flags/#allow-insecure-localhost
@python manage.py runsslserver 127.0.0.1:8100 --certificate crt.txt --key key.txt