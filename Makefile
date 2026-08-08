JC := javac
JAVA := java
SRC_DIR := src
BIN_DIR := bin

SOURCES := $(shell find $(SRC_DIR) -name '*.java' 2>/dev/null)
ifeq ($(SOURCES),)
	SRC_DIR := .
	SOURCES := $(shell find . -maxdepth 1 -name '*.java')
endif

MAIN_SERIAL   := FirelineSerial
MAIN_PARALLEL := FirelineParallel

.PHONY: all compile run run-serial run-parallel clean

all: compile

compile:
	mkdir -p $(BIN_DIR)
	$(JC) --release 11 -d $(BIN_DIR) -cp $(SRC_DIR) $(SOURCES)

run: run-parallel

run-parallel: compile
	$(JAVA) -cp $(BIN_DIR) $(MAIN_PARALLEL) $(ARGS)

run-serial: compile
	$(JAVA) -cp $(BIN_DIR) $(MAIN_SERIAL) $(ARGS)

clean:
	rm -rf $(BIN_DIR)
