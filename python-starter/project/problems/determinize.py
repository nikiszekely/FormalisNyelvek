
from project.problem import Problem
from collections import deque


class Determinize(Problem):

    def initialize_parser(self, parser):
        parser.add_argument(
            "--det",
            action="store_true",
            help="Vege automata determinizalasa"
        )

    def is_chosen_problem(self, args):
        return args.det

    def run(self, args):
        if not args.input:
            raise ValueError("Add meg a bemeneti fajlt a --input kapcsoloval!")

        if not args.output:
            raise ValueError("Add meg a kimeneti fajlt a --output kapcsoloval!")

        self.determinizalas(args.input, args.output)

    def determinizalas(self, input_fajl, output_fajl):
        # bemeneti fajl beolvasasa
        try:
            with open(input_fajl, "r", encoding="utf-8") as fajl:
                sorok = fajl.read().splitlines()
        except OSError as hiba:
            raise ValueError(f"Nem sikerult megnyitni a bemeneti fajlt: {hiba}")

        if len(sorok) < 4:
            raise ValueError("A bemeneti fajl legalabb 4 sort tartalmazzon!")

        # felbontas
        allapotok = sorok[0].split()
        abc = sorted(sorok[1].split())
        kezdo = sorok[2].strip()
        vegallapotok = set(sorok[3].split())

        if not allapotok:
            raise ValueError("Nincs megadva egyetlen allapot sem!")

        if len(allapotok) != len(set(allapotok)):
            raise ValueError("Az allapotok kozott ismetlodes van!")

        if len(abc) != len(set(abc)):
            raise ValueError("Az abeceben ismetlodo jel van!")

        allapot_halmaz = set(allapotok)
        abc_halmaz = set(abc)

        if kezdo not in allapot_halmaz:
            raise ValueError(f"Ismeretlen kezdoallapot: {kezdo}")

        for allapot in vegallapotok:
            if allapot not in allapot_halmaz:
                raise ValueError(f"Ismeretlen vegallapot: {allapot}")

        # atmenetek beolvasasa
        atmenetek = {}

        for sorszam, sor in enumerate(sorok[4:], start=5):
            elemek = sor.split()

            if not elemek:
                continue

            if len(elemek) != 3:
                raise ValueError(f"Hibas atmenet a(z) {sorszam}. sorban!")

            forras, jel, cel = elemek

            if forras not in allapot_halmaz:
                raise ValueError(
                    f"Ismeretlen forrasallapot a(z) {sorszam}. sorban: {forras}"
                )

            if cel not in allapot_halmaz:
                raise ValueError(
                    f"Ismeretlen celallapot a(z) {sorszam}. sorban: {cel}"
                )

            if jel not in abc_halmaz:
                raise ValueError(
                    f"Ismeretlen bemeneti jel a(z) {sorszam}. sorban: {jel}"
                )

            # eltarolja a helyes atmeneteket
            atmenetek.setdefault((forras, jel), set()).add(cel) 

        # determinizalas
        kezdo_reszhalmaz = frozenset([kezdo])
        reszhalmazok = [kezdo_reszhalmaz]
        sorszamok = {kezdo_reszhalmaz: 0}
        feldolgozando = deque([kezdo_reszhalmaz])
        uj_atmenetek = []

        while feldolgozando:
            aktualis = feldolgozando.popleft()
            aktualis_nev = f"s{sorszamok[aktualis]}"

            for jel in abc:
                celok = set()

                for regi_allapot in aktualis:
                    celok.update(atmenetek.get((regi_allapot, jel), set()))

                # hianyzo atmenetet nem irunk ki
                if not celok:
                    continue

                cel_reszhalmaz = frozenset(celok)

                if cel_reszhalmaz not in sorszamok:
                    sorszamok[cel_reszhalmaz] = len(reszhalmazok)
                    reszhalmazok.append(cel_reszhalmaz)
                    feldolgozando.append(cel_reszhalmaz)

                cel_nev = f"s{sorszamok[cel_reszhalmaz]}"
                uj_atmenetek.append((aktualis_nev, jel, cel_nev))

        # vegallapotok meghatarozasa
        uj_allapotok = [f"s{i}" for i in range(len(reszhalmazok))]
        uj_vegallapotok = []

        for i, reszhalmaz in enumerate(reszhalmazok):
            if reszhalmaz & vegallapotok:
                uj_vegallapotok.append(f"s{i}")

        # atmenetek rendezese: forras, jel, cel
        uj_atmenetek.sort(
            key=lambda atmenet: (
                int(atmenet[0][1:]),
                atmenet[1],
                int(atmenet[2][1:])
            )
        )

        # Eredmeny kiirasa a megadott fajlba
        try:
            with open(output_fajl, "w", encoding="utf-8") as fajl:
                fajl.write(" ".join(uj_allapotok) + "\n")
                fajl.write(" ".join(abc) + "\n")
                fajl.write("s0\n")
                fajl.write(" ".join(uj_vegallapotok) + "\n")

                for forras, jel, cel in uj_atmenetek:
                    fajl.write(f"{forras} {jel} {cel}\n")

        except OSError as hiba:
            raise ValueError(f"Nem sikerult kiirni a kimeneti fajlt: {hiba}")

        print(f"A determinizalas sikeres: {output_fajl}")
