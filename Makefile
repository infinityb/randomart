
librandomart.so: _randomart.c
	gcc -fPIC -shared -o librandomart.so _randomart.c

clean:
	rm librandomart.so
