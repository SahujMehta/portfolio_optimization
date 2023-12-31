# Copyright (C) 2006 International Business Machines and others.
# All Rights Reserved.
# This file is distributed under the Eclipse Public License.

# $Id$

##########################################################################
#    You can modify this example makefile to fit for your own program.   #
#    Usually, you only need to change the five CHANGEME entries below.   #
##########################################################################

# To compile other examples, either changed the following line, or
# add the argument DRIVER=problem_name to make
DRIVER = driver

# CHANGEME: This should be the name of your executable
EXE = $(DRIVER)

# CHANGEME: Here is the name of all object files corresponding to the source
#           code that you wrote in order to define the problem statement
OBJS =  $(DRIVER).o 

# extra object files that are required by some examples (we just link them into each one)
EXTRAOBJS = \
	CbcCompareUser.o \
	CbcSolver2.o \
	CbcSolver3.o \
	CbcSolverLongThin.o \
	ClpQuadInterface.o \
	CbcBranchFollow2.o \
	CbcBranchUser.o \
	CbcBranchLink.o

# CHANGEME: Additional libraries
# e.g., for driver2, put -lOsiCbc here
ADDLIBS =

# CHANGEME: Additional flags for compilation (e.g., include flags)
ADDINCFLAGS =

# CHANGEME: Directory to the sources for the (example) problem definition
# files
SRCDIR = /Users/ssmehta/coinbrew/Cbc/Cbc/examples
VPATH = /Users/ssmehta/coinbrew/Cbc/Cbc/examples

##########################################################################
#  Usually, you don't have to change anything below.  Note that if you   #
#  change certain compiler options, you might have to recompile the      #
#  package.                                                              #
##########################################################################

COIN_HAS_PKGCONFIG = TRUE
COIN_CXX_IS_CL = #TRUE
COIN_HAS_SAMPLE = TRUE
COIN_HAS_MIPLIB3 = TRUE

# C++ Compiler command
CXX = clang++

# C++ Compiler options
CXXFLAGS = -O3 -pipe -DNDEBUG -Wparentheses -Wreturn-type -Wcast-qual -Wall -Wpointer-arith -Wwrite-strings -Wconversion -Wno-unknown-pragmas -Wno-long-long   -DCBC_BUILD

# C Compiler options
CFLAGS = -O3 -pipe -DNDEBUG -Wimplicit -Wparentheses -Wsequence-point -Wreturn-type -Wcast-qual -Wall -Wno-unknown-pragmas -Wno-long-long   -DCBC_BUILD

# additional C++ Compiler options for linking
CXXLINKFLAGS = 

# Sample data directory
ifeq ($(COIN_HAS_SAMPLE), TRUE)
  ifeq ($(COIN_HAS_PKGCONFIG), TRUE)
    CXXFLAGS += -DSAMPLEDIR=\"`PKG_CONFIG_PATH=/Users/ssmehta/coinbrew/dist/lib/pkgconfig:/Users/ssmehta/coinbrew/dist/share/pkgconfig:/Users/ssmehta/coinbrew/dist/lib64/pkgconfig:/Users/ssmehta/coinbrew/dist/lib/pkgconfig:/Users/ssmehta/coinbrew/dist/share/pkgconfig: pkg-config --variable=datadir coindatasample`\"
      CFLAGS += -DSAMPLEDIR=\"`PKG_CONFIG_PATH=/Users/ssmehta/coinbrew/dist/lib/pkgconfig:/Users/ssmehta/coinbrew/dist/share/pkgconfig:/Users/ssmehta/coinbrew/dist/lib64/pkgconfig:/Users/ssmehta/coinbrew/dist/lib/pkgconfig:/Users/ssmehta/coinbrew/dist/share/pkgconfig: pkg-config --variable=datadir coindatasample`\"
  else
    CXXFLAGS += -DSAMPLEDIR=\"\"
      CFLAGS += -DSAMPLEDIR=\"\"
  endif
endif

# Miplib3 data directory
ifeq ($(COIN_HAS_MIPLIB3), TRUE)
  ifeq ($(COIN_HAS_PKGCONFIG), TRUE)
    CXXFLAGS += -DMIPLIB3DIR=\"`PKG_CONFIG_PATH=/Users/ssmehta/coinbrew/dist/lib/pkgconfig:/Users/ssmehta/coinbrew/dist/share/pkgconfig:/Users/ssmehta/coinbrew/dist/lib64/pkgconfig:/Users/ssmehta/coinbrew/dist/lib/pkgconfig:/Users/ssmehta/coinbrew/dist/share/pkgconfig: pkg-config --variable=datadir coindatamiplib3`\"
  else
    CXXFLAGS += -DMIPLIB3DIR=\"\"
  endif
endif

# Include directories (we use the CYGPATH_W variables to allow compilation with Windows compilers)
ifeq ($(COIN_HAS_PKGCONFIG), TRUE)
  INCL = `PKG_CONFIG_PATH=/Users/ssmehta/coinbrew/dist/lib/pkgconfig:/Users/ssmehta/coinbrew/dist/share/pkgconfig:/Users/ssmehta/coinbrew/dist/lib64/pkgconfig:/Users/ssmehta/coinbrew/dist/lib/pkgconfig:/Users/ssmehta/coinbrew/dist/share/pkgconfig: pkg-config --cflags cbc`
else
  INCL = 
endif
INCL += -I/Users/ssmehta/coinbrew/Cbc/Cbc/examples $(ADDINCFLAGS)

# Linker flags
ifeq ($(COIN_HAS_PKGCONFIG), TRUE)
  LIBS = `PKG_CONFIG_PATH=/Users/ssmehta/coinbrew/dist/lib/pkgconfig:/Users/ssmehta/coinbrew/dist/share/pkgconfig:/Users/ssmehta/coinbrew/dist/lib64/pkgconfig:/Users/ssmehta/coinbrew/dist/lib/pkgconfig:/Users/ssmehta/coinbrew/dist/share/pkgconfig: pkg-config --libs cbc`
else
  ifeq ($(COIN_CXX_IS_CL), TRUE)
    LIBS = -link -libpath:`$(CYGPATH_W) /Users/ssmehta/coinbrew/dist/lib` libCbcSolver.lib libCbc.lib libOsiCbc.lib 
  else
    LIBS = -L/Users/ssmehta/coinbrew/dist/lib -lCbcSolver -lCbc -lOsiCbc 
  endif
endif

# The following is necessary under cygwin, if native compilers are used
CYGPATH_W = echo

# Here we list all possible generated objects or executables to delete them
CLEANFILES = $(EXTRAOBJS) \
	allCuts.o allCuts \
	barrier.o barrier \
	cbc_driverC_sos.o cbc_driverC_sos \
	crew.o crew \
	driver.o driver \
	driver2.o driver2 \
	driver3.o driver3 \
	driver4.o driver4 \
	fast0507b.o fast0507b \
	fast0507.o fast0507 \
	gear.o gear \
	hotstart.o hotstart \
	interrupt.o interrupt \
	link.o link \
	longthin.o longthin \
	lotsize.o lotsize \
	minimum.o minimum \
	modify.o modify \
	nway.o nway \
	qmip.o qmip \
	qmip2.o qmip2 \
	repeat.o repeat \
	sample1.o sample1 \
	sample2.o sample2 \
	sample3.o sample3 \
	sample4.o sample4 \
	sample5.o sample5 \
	simpleBAB.o simpleBAB \
	sos.o sos \
	sudoku.o sudoku

all: $(EXE)

.SUFFIXES: .cpp .c .o .obj

$(EXE): $(OBJS) $(EXTRAOBJS)
	bla=;\
	for file in $(OBJS) $(EXTRAOBJS); do bla="$$bla `$(CYGPATH_W) $$file`"; done; \
	$(CXX) $(CXXLINKFLAGS) $(CXXFLAGS) -o $@ $$bla $(LIBS) $(ADDLIBS)

clean:
	rm -rf $(CLEANFILES) $(OBJS)

.cpp.o:
	$(CXX) $(CXXFLAGS) $(INCL) -c -o $@ `test -f '$<' || echo '$(SRCDIR)/'`$<


.cpp.obj:
	$(CXX) $(CXXFLAGS) $(INCL) -c -o $@ `if test -f '$<'; then $(CYGPATH_W) '$<'; else $(CYGPATH_W) '$(SRCDIR)/$<'; fi`

.c.o:
	$(CC) $(CFLAGS) $(INCL) -c -o $@ `test -f '$<' || echo '$(SRCDIR)/'`$<


.c.obj:
	$(CC) $(CFLAGS) $(INCL) -c -o $@ `if test -f '$<'; then $(CYGPATH_W) '$<'; else $(CYGPATH_W) '$(SRCDIR)/$<'; fi`
