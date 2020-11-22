BUILD_DIR = ./build
EXE_FILE = computeSSIM

.PHONY:build

build:
	mkdir $(BUILD_DIR); cd $(BUILD_DIR); cmake ..; make;

clean:
	rm -rf build/*;

run:
	cd $(BUILD_DIR); ./$(EXE_FILE)