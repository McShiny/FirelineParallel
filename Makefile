JC := javac
JAVA := java
SRC_DIR := src
BIN_DIR := bin
MAIN ?= Main

SOURCES := $(shell find $(SRC_DIR) -name '*.java' 2>/dev/null)
ifeq ($(SOURCES),)
	SRC_DIR := .
	SOURCES := $(shell find . -maxdepth 1 -name '*.java')
endif

.PHONY: all compile run clean

all: compile

compile:
	mkdir -p $(BIN_DIR)
	$(JC) -d $(BIN_DIR) -cp $(SRC_DIR) $(SOURCES)

run: compile
	$(JAVA) -cp $(BIN_DIR) $(MAIN)

clean:
	rm -rf $(BIN_DIR)
