# # Makefile modified from http://www.cs.swarthmore.edu/~newhall/unixhelp/howto_makefiles.html


# Essentially the commands that are being run:

# all:
# 	gcc -O3 -Wall -pedantic biSBM.c -I/usr/local/Cellar/igraph/0.7.1/include/igraph -o biSBM -L/usr/local/Cellar/igraph/0.7.1/lib -ligraph

# debug:
# 	gcc -Wall -g -pedantic biSBM.c -I/usr/local/Cellar/igraph/0.7.1/include/igraph -o biSBM_debug -L/usr/local/Cellar/igraph/0.7.1/lib -ligraph


# # define the compiler to use
CC = gcc

# # define any compile-time flags
CFLAGS = -O3 -Wall -pedantic
CFLAGS_DEBUG = -Wall -g -pedantic

# # define any directories containing header files other than /usr/include
INCLUDES = -I/usr/local/Cellar/igraph/0.7.1/include/igraph

# # define library paths in addition to /usr/lib
LFLAGS = -L/usr/local/Cellar/igraph/0.7.1/lib

# # define any libraries to link into executable:
LIBS = -ligraph

# # define the source files
SRCS = biSBM.c

# # define the object files 
OBJS = $(SRCS:.c=.o)

# # define the executable file 
MAIN = biSBM

MAIN_DEBUG = biSBM_debug

.PHONY: depend clean

all:    $(MAIN)
	@echo  Compilation completed successfully.

debug:    $(MAIN_DEBUG)
	@echo  Unoptimized compilation completed successfully.

$(MAIN): $(OBJS) 
	$(CC) $(CFLAGS) $(INCLUDES) -o $(MAIN) $(OBJS) $(LFLAGS) $(LIBS)

$(MAIN_DEBUG): $(OBJS)
	$(CC) $(CFLAGS_UNOPT) $(INCLUDES) -o $(MAIN_DEBUG) $(OBJS) $(LFLAGS) $(LIBS)

# this is a suffix replacement rule for building .o's from .c's
# it uses automatic variables $<: the name of the prerequisite of
# the rule(a .c file) and $@: the name of the target of the rule (a .o file) 
# (see the gnu make manual section about automatic variables)
.c.o:
	$(CC) $(CFLAGS) $(INCLUDES) -c $<  -o $@

clean:
	$(RM) *.o *~ $(MAIN) $(MAIN_DEBUG)

depend: $(SRCS)
	makedepend $(INCLUDES) $^

# # DO NOT DELETE THIS LINE -- make depend needs it
