#Representa el rotor d'una ENIGMA i funcions bàsiques per treballar amb l'alfabet.
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N = len(ALPHABET)
#Converteix lletres 'A'-'Z' a índexs 0-25 i a l'inrevés per poder fer càlculs modulars.
def char_to_index(c):
    """Convierte una letra A-Z en un número 0-25."""
    return ALPHABET.index(c)

def index_to_char(i):
    """Convierte un número 0-25 en una letra A-Z."""
    return ALPHABET[i % N]
#Classe que modela un rotor amb el seu cablejat intern, la lletra notch i la posició actual.
class Rotor:
    def __init__(self, wiring, notch="Z", position=0):
        """
        wiring: string de 26 letras A-Z, permutación (ej: 'EKMFLGDQVZNTOWYHXUSPAIBRCJ')
        notch: letra donde este rotor hace avanzar al siguiente (ej: 'Q' o 'Z')
        position: entero 0-25 que indica la posición inicial (A=0, B=1, ...)
        """
        self.wiring = wiring
        self.notch = notch
        self.position = position

        # precalcular el cableado inverso para descifrar
        self.inverse_wiring = self._compute_inverse_wiring()
#Calcula el cablejat invers per saber quina lletra d'entrada produeix cada sortida.
    def _compute_inverse_wiring(self):
        """Devuelve la cadena de 26 letras que hace el mapeo inverso."""
        inverse = ["?"] * N
        for i, ch in enumerate(self.wiring):
            out_index = char_to_index(ch)
            inverse[out_index] = index_to_char(i)
        return "".join(inverse)
#Avança el rotor una posició (com un comptador) i indica si ha arribat a la lletra notch.
    def step(self):
        """Avanza el rotor una posición (0-25). Devuelve True si está en el notch."""
        self.position = (self.position + 1) % N
        current_letter = index_to_char(self.position)
        return current_letter == self.notch
#Aplica el cablejat del rotor en sentit d'esquerra a dreta, tenint en compte la posició.
    def encode_forward(self, c):
        """Pasa una letra de entrada (A-Z) hacia adelante por el rotor."""
        i = char_to_index(c)
        shifted = (i + self.position) % N
        wired_char = self.wiring[shifted]
        out_index = (char_to_index(wired_char) - self.position) % N
        return index_to_char(out_index)
#Aplica el cablejat invers del rotor en sentit de dreta a esquerra per desxifrar.
    def encode_backward(self, c):
        """Pasa una letra (A-Z) hacia atrás usando el cableado inverso."""
        i = char_to_index(c)
        shifted = (i + self.position) % N
        wired_char = self.inverse_wiring[shifted]
        out_index = (char_to_index(wired_char) - self.position) % N
        return index_to_char(out_index)

def load_rotor_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip().upper() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"[ERROR] No s'ha trobat el fitxer {filename}")
        return None

    if len(lines) == 0:
        print(f"[ERROR] {filename}: fitxer buit")
        return None

    wiring = lines[0]
    # comprobar que tiene 26 letras únicas A-Z
    if len(wiring) != 26 or any(ch not in ALPHABET for ch in wiring) or len(set(wiring)) != 26:
        print(f"[ERROR] {filename}: permutació incorrecta — calen 26 lletres úniques A–Z")
        return None

    notch = lines[1] if len(lines) >= 2 else "Z"
    notch = notch[0].upper()
    if notch not in ALPHABET:
        notch = "Z"

    return Rotor(wiring, notch=notch, position=0)


if __name__ == "__main__":
    wiring_example = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
    rotor = Rotor(wiring_example, notch="Q", position=0)

    letra = "A"
    cifrada = rotor.encode_forward(letra)
    vuelta = rotor.encode_backward(cifrada)

    print("Letra original:", letra)
    print("Tras pasar adelante:", cifrada)
    print("Tras volver atrás:", vuelta)

    for _ in range(5):
        avanzado = rotor.step()
        print("Posición:", rotor.position, "letra ventana:", index_to_char(rotor.position), "en notch?:", avanzado)