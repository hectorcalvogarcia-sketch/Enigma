from rotor import Rotor, ALPHABET, char_to_index, index_to_char

def load_rotor_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip().upper() for line in f.readlines() if line.strip()]
            print("DEBUG", filename, "->", lines)
    except FileNotFoundError:
        print(f"[ERROR] No s'ha trobat el fitxer {filename}")
        return None

    if len(lines) == 0:
        print(f"[ERROR] {filename}: fitxer buit")
        return None

    wiring = lines[0]
    if len(wiring) != 26 or any(ch not in ALPHABET for ch in wiring) or len(set(wiring)) != 26:
        print(f"[ERROR] {filename}: permutació incorrecta — calen 26 lletres úniques A–Z")
        return None

    notch = lines[1] if len(lines) >= 2 else "Z"
    notch = notch[0].upper()
    if notch not in ALPHABET:
        notch = "Z"

    return Rotor(wiring, notch=notch, position=0)

# ---------- Normalización de texto ----------

def normalize_text_for_encrypt(text):
    text = text.upper()
    solo_letras = "".join(ch for ch in text if ch in ALPHABET)
    grupos = []
    for i in range(0, len(solo_letras), 5):
        grupos.append(solo_letras[i:i+5])
    return solo_letras, " ".join(grupos)

# ---------- Avance de rotors ----------

def advance_rotors(r1, r2, r3):
    carry = r1.step()
    if carry:
        carry2 = r2.step()
        if carry2:
            r3.step()

# ---------- Cifrar / descifrar un carácter ----------

def encrypt_char(c, r1, r2, r3):
    x = r1.encode_forward(c)
    x = r2.encode_forward(x)
    x = r3.encode_forward(x)
    return x

def decrypt_char(c, r1, r2, r3):
    x = r3.encode_backward(c)
    x = r2.encode_backward(x)
    x = r1.encode_backward(x)
    return x

# ---------- Opciones del menú ----------

def option_encrypt():
    print("=== Xifrar missatge ===")
    text = input("Introdueix el missatge en llengua natural: ")

    with open("Missatge.txt", "w", encoding="utf-8") as f:
        f.write(text)

    window = input("Introdueix les 3 lletres de finestra (ex: A B C): ").upper().split()
    if len(window) != 3 or any(len(x) != 1 or x not in ALPHABET for x in window):
        print("[ERROR] Finestra inicial no vàlida")
        return

    r1 = load_rotor_from_file("Rotor1.txt")
    r2 = load_rotor_from_file("Rotor2.txt")
    r3 = load_rotor_from_file("Rotor3.txt")
    if not (r1 and r2 and r3):
        return

    r1.position = char_to_index(window[0])
    r2.position = char_to_index(window[1])
    r3.position = char_to_index(window[2])

    solo_letras, _ = normalize_text_for_encrypt(text)

    cifrado = []
    for ch in solo_letras:
        advance_rotors(r1, r2, r3)
        x = encrypt_char(ch, r1, r2, r3)
        cifrado.append(x)

    cifrado_str = ""
    for i in range(0, len(cifrado), 5):
        if i > 0:
            cifrado_str += " "
        cifrado_str += "".join(cifrado[i:i+5])

    with open("Xifrat.txt", "w", encoding="utf-8") as f:
        f.write(cifrado_str)

    print(f"[OK] Missatge xifrat a \"Xifrat.txt\" ({len(cifrado)} lletres)")

def option_decrypt():
    print("=== Desxifrar missatge ===")

    # leer Xifrat.txt
    try:
        with open("Xifrat.txt", "r", encoding="utf-8") as f:
            cifrado_str = f.read().strip().upper()
    except FileNotFoundError:
        print("[ERROR] No s'ha trobat el fitxer Xifrat.txt")
        return

    # quitar espacios, dejar solo letras A-Z
    solo_lletres = "".join(ch for ch in cifrado_str if ch in ALPHABET)

    # pedir mismas posiciones iniciales
    window = input("Introdueix les 3 lletres de finestra (ex: A B C): ").upper().split()
    if len(window) != 3 or any(len(x) != 1 or x not in ALPHABET for x in window):
        print("[ERROR] Finestra inicial no vàlida")
        return

    # cargar rotors
    r1 = load_rotor_from_file("Rotor1.txt")
    r2 = load_rotor_from_file("Rotor2.txt")
    r3 = load_rotor_from_file("Rotor3.txt")
    if not (r1 and r2 and r3):
        return

    # aplicar posiciones iniciales
    r1.position = char_to_index(window[0])
    r2.position = char_to_index(window[1])
    r3.position = char_to_index(window[2])

    # desxifrar
    desxifrat = []
    for ch in solo_lletres:
        advance_rotors(r1, r2, r3)
        x = decrypt_char(ch, r1, r2, r3)
        desxifrat.append(x)

    desxifrat_str = "".join(desxifrat)

    with open("desxifrat.txt", "w", encoding="utf-8") as f:
        f.write(desxifrat_str)

    print(f"[OK] Missatge desxifrat a \"desxifrat.txt\" ({len(desxifrat)} lletres)")

def is_valid_permutation(wiring):
    wiring = wiring.upper()
    if len(wiring) != 26:
        return False
    if any(ch not in ALPHABET for ch in wiring):
        return False
    if len(set(wiring)) != 26:
        return False
    return True

def option_edit_rotors():
    print("=== Editar rotors ===")
    print("Tria rotor a editar:")
    print("1. Rotor1.txt")
    print("2. Rotor2.txt")
    print("3. Rotor3.txt")

    choice = input("Opció (1-3): ").strip()
    if choice not in ("1", "2", "3"):
        print("[ERROR] Opció invàlida")
        return

    filename = f"Rotor{choice}.txt"

    print("Introdueix una nova permutació de 26 lletres A-Z, sense espais ni repeticions.")
    print("Exemple: EKMFLGDQVZNTOWYHXUSPAIBRCJ")
    new_wiring = input("Nova permutació: ").strip().upper()

    if not is_valid_permutation(new_wiring):
        print("[ERROR] Permutació invàlida. Calen exactament 26 lletres úniques A–Z.")
        return

    notch = input("Introdueix la lletra notch (o enter per defecte Z): ").strip().upper()
    if notch == "":
        notch = "Z"
    else:
        notch = notch[0]
        if notch not in ALPHABET:
            print("[ERROR] Notch invàlid, s'utilitzarà Z.")
            notch = "Z"

    # guardar en el fitxer (sobreescriure)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_wiring + "\n")
        f.write(notch + "\n")

    print(f"[OK] Rotor actualitzat i desat a \"{filename}\"")


# ---------- Menú principal ----------

def main():
    while True:
        print("ENIGMA:")
        print("-------------------------------")
        print("1. Xifrar missatge")
        print("2. Desxifrar missatge")
        print("3. Editar rotors")
        print("4. Sortir")

        choice = input("Escull una opció: ").strip()

        if choice == "1":
            option_encrypt()
        elif choice == "2":
            option_decrypt()
        elif choice == "3":
            option_edit_rotors()
        elif choice == "4":
            print("Sortint...")
            break
        else:
            print("Opció invàlida")

