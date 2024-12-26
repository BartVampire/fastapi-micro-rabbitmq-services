# Создание RSA приватного ключа + публичного ключа

```shell
# Сгенерируйте закрытый ключ RSA размером 2048
openssl genrsa -out jwt-private.pem 2048
```

```shell
# Сгенерируйте публичный ключ RSA из закрытого ключа (приватного)
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```