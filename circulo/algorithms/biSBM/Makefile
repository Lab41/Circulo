# A better makefile is in Makefile_modify, but it's currently broken.
all:
	clang -O3 -Wall -g -pedantic working_biSBM.c -I/usr/local/Cellar/igraph/0.7.1/include/igraph -o working_biSBM -L/usr/local/Cellar/igraph/0.7.1/lib -ligraph

unopt:
	gcc -Wall -g -pedantic working_biSBM.c -I/usr/local/Cellar/igraph/0.7.1/include/igraph -o working_biSBM -L/usr/local/Cellar/igraph/0.7.1/lib -ligraph
# -std=c++0x or something like that for cpp


# # here's a better Makefile, but it doesn't currently work. TODO!

# # Makefile modified from http://www.cs.swarthmore.edu/~newhall/unixhelp/howto_makefiles.html

# # define the compiler to use
# CC = g++

# # define any compile-time flags
# CFLAGS = -O3 -Wall -g -pedantic

# # define any directories containing header files other than /usr/include
# INCLUDES = -I/usr/local/Cellar/igraph/0.7.1/include/igraph

# # define library paths in addition to /usr/lib
# LFLAGS = -L/usr/local/Cellar/igraph/0.7.1/lib

# # define any libraries to link into executable:
# LIBS = -ligraph

# # define the source files
# SRCS = working_biSBM.cpp

# # define the object files 
# OBJS = $(SRCS:.cpp=.o)

# # define the executable file 
# MAIN = working_biSBM

# #
# # The following part of the makefile is generic; it can be used to 
# # build any executable just by changing the definitions above and by
# # deleting dependencies appended to the file from 'make depend'
# #

# .PHONY: depend clean

# all:    $(MAIN)
# 	@echo  Compilation completed successfully.

# $(MAIN): $(OBJS) 
# 	$(CC) $(CFLAGS) $(INCLUDES) -o $(MAIN) $(OBJS) $(LFLAGS) $(LIBS)

# # this is a suffix replacement rule for building .o's from .c's
# # it uses automatic variables $<: the name of the prerequisite of
# # the rule(a .c file) and $@: the name of the target of the rule (a .o file) 
# # (see the gnu make manual section about automatic variables)
# .c.o:
# 	$(CC) $(CFLAGS) $(INCLUDES) -c $<  -o $@

# clean:
# 	$(RM) *.o *~ $(MAIN)

# depend: $(SRCS)
# 	makedepend $(INCLUDES) $^

# # DO NOT DELETE THIS LINE -- make depend needs it
