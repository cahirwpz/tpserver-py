all:
	@echo "init - initialize tp server database"
	@echo "turn - advance one turn"
	@echo "clean - cleanup directories from unnecessary files"

init:
	./tpserver-py-tool --addgame tp minisec admin@localhost "A test game"
	./tpserver-py-tool --populate tp 0 10 10 2 2
	./tpserver-py-tool --player tp <username> <password>

turn:
	./tpserver-py-tool --turn tp

clean:
	find -iname '*.pyc' -delete
	find -iname '*~' -delete

.PHONY: all init turn clean
