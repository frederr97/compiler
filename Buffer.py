class Buffer:
    def load_buffer(self):
        file = open('entrada.txt', 'r')
        line = file.readline()
        buffer = []
        cont = 1

        while line != "":
            buffer.append(line)
            line = file.readline()
            cont += 1
            if cont == 10 or line == '':
                buf = ''.join(buffer)
                cont = 1
                yield buf
                buffer = []
        file.close()
