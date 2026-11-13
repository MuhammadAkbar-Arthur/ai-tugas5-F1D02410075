import json


def muat_aturan(nama_file: str) -> dict:
    """Membaca file basis pengetahuan berformat JSON."""
    with open(nama_file, "r", encoding="utf-8") as file:
        return json.load(file)


def ambil_fakta_dasar(daftar_aturan: list) -> list:
    """
    Mengambil semua fakta pada 'jika' yang tidak pernah menjadi hasil 'maka'
    dengan tetap mempertahankan urutan kemunculannya.
    """
    semua_hasil = {r["maka"] for r in daftar_aturan}
    fakta_dasar = []
    for r in daftar_aturan:
        for syarat in r["jika"]:
            if syarat not in semua_hasil and syarat not in fakta_dasar:
                fakta_dasar.append(syarat)
    return fakta_dasar


def ambil_target_kesimpulan(daftar_aturan: list) -> list:
    """
    Mengambil semua hasil 'maka' yang merupakan kesimpulan akhir
    (tidak pernah dipakai lagi sebagai syarat 'jika' di aturan lain).
    """
    semua_syarat = {syarat for r in daftar_aturan for syarat in r["jika"]}
    kesimpulan_akhir = []
    for r in daftar_aturan:
        if r["maka"] not in semua_syarat and r["maka"] not in kesimpulan_akhir:
            kesimpulan_akhir.append(r["maka"])
    return kesimpulan_akhir


def syarat_terpenuhi(aturan: dict, memori: list) -> bool:
    """Mengecek apakah syarat aturan terpenuhi oleh memori sesuai mode 'dan'/'atau'."""
    if aturan["mode"] == "dan":
        return all(s in memori for s in aturan["jika"])
    elif aturan["mode"] == "atau":
        return any(s in memori for s in aturan["jika"])
    return False


def cetak_alasan(fakta: str, jejak_alasan: dict, memori: list, indentasi: int = 1):
    """Mencetak pohon jejak aturan (alasan) secara rekursif."""
    if fakta not in jejak_alasan:
        return

    aturan = jejak_alasan[fakta]
    syarat_aktif = [s for s in aturan["jika"] if s in memori]
    spasi = "  " * indentasi
    print(f"{spasi}{fakta}  <- {aturan['id']} ({', '.join(syarat_aktif)})")

    for syarat in syarat_aktif:
        if syarat in jejak_alasan:
            cetak_alasan(syarat, jejak_alasan, memori, indentasi + 1)


def main():
    kb = muat_aturan("kb_laptop.json")
    daftar_aturan = kb["aturan"]
    fakta_dasar = ambil_fakta_dasar(daftar_aturan)
    daftar_kesimpulan_akhir = ambil_target_kesimpulan(daftar_aturan)

    print(kb["judul"])
    print("Jawab y/t.")

    memori = []
    for idx, fakta in enumerate(fakta_dasar, start=1):
        jawaban = input(f"{idx}. Apakah {fakta}? (y/t) > ").strip().lower()
        if jawaban == "y":
            memori.append(fakta)

    fakta_awal = list(memori)
    print(f"\nFakta awal: {', '.join(fakta_awal) if fakta_awal else 'tidak ada'}\n")

    # Mesin Inferensi Forward Chaining
    jejak_alasan = {}
    siklus = 1
    while True:
        cocok = [
            r for r in daftar_aturan
            if syarat_terpenuhi(r, memori) and r["maka"] not in memori
        ]

        if not cocok:
            print(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
            break

        r = cocok[0]  # ambil aturan pertama yang cocok
        memori.append(r["maka"])
        jejak_alasan[r["maka"]] = r
        print(f"Siklus {siklus}: {r['id']} -> {r['maka']}")
        siklus += 1

    # Menentukan kesimpulan akhir yang berhasil dicapai di memori
    kesimpulan_tercapai = [k for k in memori if k in daftar_kesimpulan_akhir]

    if kesimpulan_tercapai:
        print(f"\nKesimpulan: {', '.join(kesimpulan_tercapai)}")
        print("Alasan:")
        for k in kesimpulan_tercapai:
            cetak_alasan(k, jejak_alasan, memori, indentasi=1)
    else:
        print("\nKesimpulan: tidak ada")
        print("Alasan: fakta yang diberikan belum cukup untuk mencapai kesimpulan akhir.")

    print(f"\nCatatan: {kb['batas']}")


if __name__ == "__main__":
    main()