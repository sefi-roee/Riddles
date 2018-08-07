# location of the Python header files
 
PYTHON_VERSION = 2.7
PYTHON_INCLUDE = /home/roee/anaconda2/include/python$(PYTHON_VERSION)
 
# location of the Boost Python include files and library
 
BOOST_INC = /usr/include
BOOST_LIB = /usr/lib/x86_64-linux-gnu/
 
# compile mesh classes
TARGET = shapeshifter
 
$(TARGET): $(TARGET).o 
	g++ -std=c++11 -Werror -Wall -pedantic -lpthread -pthread shapeshifter.cpp shape.cpp main.cpp -o shapeshifter -g -O3

$(TARGET).o: $(TARGET).cpp $(TARGET).hpp
	g++ -std=c++11 -Werror -Wall -pedantic -I$(PYTHON_INCLUDE) -I$(BOOST_INC) -fPIC -c $(TARGET).cpp

$(TARGET).so: $(TARGET).o
	g++ -std=c++11 -shared -Wl,--export-dynamic $(TARGET).o -L$(BOOST_LIB) -lboost_python -L/usr/lib/python$(PYTHON_VERSION)/config -lpython$(PYTHON_VERSION) -o $(TARGET).so

clean:
	\rm -rf $(TARGET).o $(TARGET).so
	
all: $(TARGET) $(TARGET).so