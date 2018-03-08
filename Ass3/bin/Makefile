# Makefile

CC = gcc
CFLAGS = -Wall -O3

CSRC = agent.c pipe.c
HSRC = pipe.h
OBJ = $(CSRC:.c=.o)

%o:%c $(HSRC)
	$(CC) $(CFLAGS) -c $<

# additional targets
.PHONY: clean

agent: $(OBJ)
	$(CC) -lm $(CFLAGS) -o agent $(OBJ)

clean:
	rm *.o *.class agent
