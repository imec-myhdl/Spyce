LIB = libpyblk.a
all: $(LIB)

RTPYINC = ../include

SRCALL = $(wildcard *.c)

#ifeq ($(strip $(JMODELICA_HOME)),)
#EXCLUDE = FMUinterface.c
#else
INCFMI = -I/usr/local/jmodelica/include/RuntimeLibrary/ -I/usr/local/jmodelica/ThirdParty/FMI/2.0/
#endif

SRC=$(filter-out $(EXCLUDE),$(SRCALL))
OBJ = $(SRC:.c=.o)

######DBG = -g -fPIC
DBG = -g

CC_FLAGS = -c $(DBG) -I$(RTPYINC) $(INCFMI)

%.o: %.c
	cc $(CC_FLAGS) $<

$(LIB): $(OBJ)
	ar -r $(LIB) $(OBJ)

install:
	mv $(LIB) ../lib

clean:
	rm -f $(LIB) $(OBJ)
