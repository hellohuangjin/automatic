CXXFLAG = -I/usr/local/opt/opencv3/include
LDFLAGS = -L/usr/local/opt/opencv3/lib
LIBS = -lopencv_highgui -lopencv_imgcodecs -lopencv_core -lopencv_imgproc -lopencv_calib3d -lopencv_features2d -lopencv_objdetect -lopencv_flann -ltesseract -lzbar

objects = config.o processor.o main.o

ExpressClassify: $(objects)
	@echo 生成目标文件...
	clang++ $(objects) -o $@ $(LDFLAGS) $(LIBS)

config.o: config.cpp config.h
	@echo 正在编译config.o模块...
	clang++ -c $< $(CXXFLAG)

main.o: main.cpp processor.h
	@echo 正在编译main.o模块...
	clang++ -c $< $(CXXFLAG)

processor.o: processor.cpp processor.h
	@echo 正在编译processor.o模块...
	clang++ -c $< $(CXXFLAG)

.PHONY:clean

clean:
	rm -f $(objects) ExpressClassify

