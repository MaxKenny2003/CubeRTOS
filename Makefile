# Compiler is gcc (c)
CC = gcc

# Source files
SRC = main.c scheduler.c

# Object files (same as source but with .o)
OBJ = $(SRC:.c=.o)

# Output binary name
TARGET = cubeRTOS

# Default rule
all: $(TARGET)

# Linking rule
$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ)

# Compilation rule
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Cleanup
clean:
	rm -f $(OBJ) $(TARGET)
