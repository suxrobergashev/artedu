from django.test import TestCase

# Create your tests here.
list_3 = ['Accidental', '4daa7fe9', 'eM131Me', 'Y!.90']
secret = []

for x in list_3:
    secret.append(x[:2])

print(''.join(secret))